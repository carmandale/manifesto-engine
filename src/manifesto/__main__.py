#!/usr/bin/env python3
import click
import yaml
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .core.injector import inject_manifesto
from .core.validator import validate_manifesto
from .core.task_loader import load_tasks
from .verify.swift import SwiftVerifier
from .orchestrate.planner import ManifestoPlanner

console = Console()

@click.group()
def cli():
    """Manifesto Engine - Zero ambiguity project orchestration"""
    pass

@cli.command()
@click.option('--type', default='visionos', help='Project type')
@click.option('--name', required=True, help='Project name')
@click.option('--path', default='.', help='Project path')
def init(type, name, path):
    """Initialize a new project with manifesto"""
    console.print(f"[bold green]Initializing {type} project: {name}[/bold green]")
    
    project_path = Path(path).resolve()
    success = inject_manifesto(project_path, name, type)
    
    if success:
        console.print("✅ Manifesto initialized successfully")
        console.print(f"📁 Created at: {project_path}/docs/_MANIFESTO/")
    else:
        console.print("[bold red]❌ Failed to initialize manifesto[/bold red]")
        sys.exit(1)

@cli.command()
@click.argument('task_id')
@click.option('--manifest', default='docs/_MANIFESTO/manifesto.yaml', help='Manifesto file')
def verify(task_id, manifest):
    """Verify a task was completed correctly"""
    console.print(f"[bold blue]Verifying task {task_id}...[/bold blue]")
    
    manifest_path = Path(manifest)
    if not manifest_path.exists():
        console.print(f"[red]❌ Manifesto not found at {manifest}[/red]")
        sys.exit(1)
    
    with open(manifest_path) as f:
        data = yaml.safe_load(f)
    
    # Pass manifest directory to verifier
    verifier = SwiftVerifier(data, str(manifest_path.parent))
    passed, results = verifier.verify_task(task_id)
    
    # Display results table
    table = Table(title=f"Task {task_id} Verification")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    for check, result in results.items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        table.add_row(check, status, result.get('details', ''))
    
    console.print(table)
    
    if not passed:
        sys.exit(1)

@cli.command()
def status():
    """Show manifesto status"""
    manifest_path = Path("docs/_MANIFESTO/manifesto.yaml")
    if manifest_path.exists():
        with open(manifest_path) as f:
            data = yaml.safe_load(f)
        # Load tasks using task loader
        tasks = load_tasks(str(manifest_path.parent))
        console.print(f"[bold]Project:[/bold] {data['title']}")
        console.print(f"[bold]Status:[/bold] {data['status']}")
        console.print(f"[bold]Tasks:[/bold] {len(tasks)}")
    else:
        console.print("[red]No manifesto found in current directory[/red]")

@cli.command()
@click.option('--manifest', default='docs/_MANIFESTO/manifesto.yaml', help='Manifesto file')
def plan(manifest):
    """Generate a PLAN only (no execution)."""
    console.print("[bold yellow]Generating PLAN (no execution)...[/bold yellow]")
    planner = ManifestoPlanner()
    plan_obj = planner.generate_plan(manifest)
    if not planner.validate_plan(plan_obj):
        console.print("[red]❌ Plan validation failed. Fix issues before proceeding.[/red]")
        sys.exit(1)
    plan_path = Path(manifest).parent / "plan.json"
    with open(plan_path, "w") as f:
        json.dump(plan_obj, f, indent=2)
    console.print(f"✅ PLAN saved to {plan_path}. Review and run 'manifesto execute' when ready.")

@cli.command()
@click.option('--manifest', default='docs/_MANIFESTO/manifesto.yaml', help='Manifesto file')
def execute(manifest):
    """Execute tasks after PLAN approval."""
    plan_path = Path(manifest).parent / "plan.json"
    if not plan_path.exists():
        console.print("[red]No PLAN found. Run 'manifesto plan' first.[/red]")
        sys.exit(1)
    with open(plan_path) as f:
        plan_obj = json.load(f)
    planner = ManifestoPlanner()
    success = planner.execute_plan(plan_obj)
    if not success:
        console.print("[bold red]❌ Execution failed. Review output above.[/bold red]")
        sys.exit(1)
    console.print("[bold green]🎉 All tasks executed successfully![/bold green]")

@cli.command('migrate-tasks')
@click.option('--manifest', default='docs/_MANIFESTO/manifesto.yaml', help='Manifesto file')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
def migrate_tasks(manifest, dry_run):
    """Migrate tasks from manifesto.yaml to individual task files."""
    manifest_path = Path(manifest)
    if not manifest_path.exists():
        console.print(f"[red]❌ Manifesto not found at {manifest}[/red]")
        sys.exit(1)
    
    # Load existing manifesto
    with open(manifest_path) as f:
        data = yaml.safe_load(f)
    
    tasks = data.get('tasks', [])
    if not tasks:
        console.print("[yellow]No tasks found in manifesto.yaml[/yellow]")
        return
    
    tasks_dir = manifest_path.parent / "tasks"
    
    if dry_run:
        console.print("[bold blue]DRY RUN - No changes will be made[/bold blue]")
        console.print(f"\nWould create directory: {tasks_dir}")
        console.print(f"Would backup to: {manifest_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        console.print(f"\nWould create {len(tasks)} task files:")
        for task in tasks:
            console.print(f"  - tasks/{task['id']}.yaml")
        console.print("\nWould remove tasks section from manifesto.yaml")
        return
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = manifest_path.parent / f"{manifest_path.name}.backup-{timestamp}"
    shutil.copy2(manifest_path, backup_path)
    console.print(f"✅ Created backup: {backup_path}")
    
    # Create tasks directory
    tasks_dir.mkdir(exist_ok=True)
    console.print(f"✅ Created directory: {tasks_dir}")
    
    # Configure YAML dumper for pretty output
    class LiteralStr(str):
        pass
    
    def literal_presenter(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    yaml.add_representer(LiteralStr, literal_presenter)
    
    # Write individual task files
    for task in tasks:
        task_file = tasks_dir / f"{task['id']}.yaml"
        
        # Format task data
        task_data = {
            'id': task['id'],
            'title': task.get('title', ''),
            'description': LiteralStr(task.get('description', '')),
            'owner_role': task.get('owner_role', ''),
            'depends_on': task.get('depends_on', []),
            'acceptance': task.get('acceptance', {})
        }
        
        # Remove empty fields
        task_data = {k: v for k, v in task_data.items() if v}
        
        with open(task_file, 'w') as f:
            yaml.dump(task_data, f, default_flow_style=False, 
                     sort_keys=False, allow_unicode=True, width=80)
        
        console.print(f"✅ Created: {task_file}")
    
    # Remove tasks from manifesto and write updated version
    del data['tasks']
    
    # Write updated manifesto
    with open(manifest_path, 'w') as f:
        # Preserve comments by reading original file
        with open(backup_path) as orig:
            lines = orig.readlines()
            # Write header comments
            for line in lines:
                if line.strip().startswith('#') or line.strip() == '':
                    f.write(line)
                else:
                    break
        
        # Write data without tasks
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                 allow_unicode=True, width=80)
    
    console.print(f"\n[bold green]✅ Migration complete![/bold green]")
    console.print(f"   - Migrated {len(tasks)} tasks to {tasks_dir}")
    console.print(f"   - Updated {manifest_path}")
    console.print(f"   - Backup saved to {backup_path}")

if __name__ == "__main__":
    cli()
