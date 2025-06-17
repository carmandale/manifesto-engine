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
from .core.task_parser import TaskParser
from .core.prompt_generator import PromptGenerator
from .core.markdown_parser import MarkdownImporter
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

@cli.command()
@click.argument('description', nargs=-1, required=True)
@click.option('--manifest-dir', default='docs/_MANIFESTO', help='Manifesto directory')
def add(description, manifest_dir):
    """Add a new task using natural language description."""
    # Join the description words
    description_text = ' '.join(description)
    
    # Create parser and parse
    parser = TaskParser(manifest_dir)
    task_id = parser.create_task(description_text)
    
    if task_id:
        console.print(f"\n[bold green]🚀 Task {task_id} created successfully![/bold green]")
        console.print(f"Run 'manifesto verify {task_id}' to test it")
    else:
        console.print("[red]Task creation cancelled[/red]")

@cli.command('check-alignment')
@click.option('--manifest-dir', default='docs/_MANIFESTO', help='Manifesto directory')
@click.option('--output', type=click.Choice(['table', 'detailed']), default='table', help='Output format')
def check_alignment(manifest_dir, output):
    """Check all tasks for vision alignment and flag drift."""
    manifest_path = Path(manifest_dir)
    
    # Load vision
    manifest_file = manifest_path / "manifesto.yaml"
    if not manifest_file.exists():
        console.print("[red]No manifesto found[/red]")
        sys.exit(1)
        
    with open(manifest_file) as f:
        manifest_data = yaml.safe_load(f)
    
    vision = manifest_data.get('vision', 'No vision found')
    north_star = manifest_data.get('metrics', {}).get('north_star', 'No north star metric')
    
    # Load all tasks
    tasks = load_tasks(manifest_dir)
    
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return
    
    # Analyze each task
    alignment_scores = []
    
    for task in tasks:
        score = _calculate_alignment_score(task, vision)
        alignment_scores.append({
            'task': task,
            'score': score['score'],
            'status': score['status'],
            'issues': score['issues']
        })
    
    # Display results
    if output == 'table':
        table = Table(title="Vision Alignment Report")
        table.add_column("Task ID", style="cyan")
        table.add_column("Title", style="white") 
        table.add_column("Score", style="bold")
        table.add_column("Status", style="bold")
        table.add_column("Issues", style="yellow")
        
        for item in alignment_scores:
            task = item['task']
            score_color = "green" if item['score'] >= 4 else "yellow" if item['score'] >= 3 else "red"
            status_color = "green" if item['status'] == "ALIGNED" else "yellow" if item['status'] == "NEEDS_REVIEW" else "red"
            
            table.add_row(
                task['id'],
                task.get('title', task.get('description', '')[:40]),
                f"[{score_color}]{item['score']}/5[/{score_color}]",
                f"[{status_color}]{item['status']}[/{status_color}]",
                ', '.join(item['issues']) if item['issues'] else "✓"
            )
        
        console.print(table)
        
        # Summary
        avg_score = sum(item['score'] for item in alignment_scores) / len(alignment_scores)
        drift_count = sum(1 for item in alignment_scores if item['score'] < 3)
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"Average alignment score: {avg_score:.1f}/5")
        console.print(f"Tasks with potential drift: {drift_count}/{len(tasks)}")
        
    else:  # detailed output
        for item in alignment_scores:
            task = item['task']
            console.print(f"\n[bold cyan]Task {task['id']}:[/bold cyan] {task.get('title', '')}")
            console.print(f"Vision Link: {task.get('vision_link', '[red]MISSING[/red]')}")
            console.print(f"Alignment Score: {item['score']}/5")
            console.print(f"Status: {item['status']}")
            if item['issues']:
                console.print(f"Issues: {', '.join(item['issues'])}")
            console.print("-" * 40)

def _calculate_alignment_score(task: dict, vision: str) -> dict:
    """Calculate vision alignment score for a task."""
    score = 5  # Start with perfect score
    issues = []
    
    # Check for vision_link field
    vision_link = task.get('vision_link', '')
    if not vision_link:
        score -= 2
        issues.append("Missing vision_link")
    else:
        # Check quality of vision link
        if len(vision_link) < 30:
            score -= 1
            issues.append("Vision link too brief")
        
        vague_terms = ['helps', 'supports', 'improves', 'better']
        if any(term in vision_link.lower() for term in vague_terms) and len(vision_link) < 50:
            score -= 1
            issues.append("Vision link is vague")
    
    # Check if description mentions vision keywords
    description = task.get('description', '').lower()
    vision_keywords = ['speed', 'thought', 'ambiguity', 'verify', 'align']
    has_vision_reference = any(keyword in description for keyword in vision_keywords)
    
    if not has_vision_reference and score > 3:
        score -= 0.5
        issues.append("No vision keywords in description")
    
    # Determine status
    if score >= 4:
        status = "ALIGNED"
    elif score >= 3:
        status = "NEEDS_REVIEW"
    else:
        status = "DRIFT_RISK"
    
    return {
        'score': max(1, min(5, score)),  # Clamp between 1-5
        'status': status,
        'issues': issues
    }

@cli.command('generate-prompt')
@click.argument('task_id')
@click.option('--type', 'prompt_type', type=click.Choice(['worker', 'supervisor']), required=True, help='Type of prompt to generate')
@click.option('--output', type=click.Choice(['console', 'file']), default='console', help='Output destination')
@click.option('--manifest-dir', default='docs/_MANIFESTO', help='Manifesto directory')
@click.option('--summary', help='Worker summary for supervisor prompts')
def generate_prompt(task_id, prompt_type, output, manifest_dir, summary):
    """Generate a prompt from templates for a specific task."""
    generator = PromptGenerator(manifest_dir)
    
    # Generate the prompt
    if prompt_type == 'worker':
        prompt = generator.generate_worker_prompt(task_id)
    else:  # supervisor
        prompt = generator.generate_supervisor_prompt(task_id, summary)
    
    if not prompt:
        console.print(f"[red]Task {task_id} not found[/red]")
        sys.exit(1)
    
    # Output the prompt
    if output == 'console':
        console.print(prompt)
    else:  # file
        output_file = Path(f"{task_id}_{prompt_type}_prompt.md")
        with open(output_file, 'w') as f:
            f.write(prompt)
        console.print(f"[green]✅ Prompt saved to {output_file}[/green]")

@cli.command('import')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--interactive/--no-interactive', default=True, help='Interactive clarification mode')
@click.option('--dry-run', is_flag=True, help='Preview without creating files')
@click.option('--manifest-dir', default='docs/_MANIFESTO', help='Manifesto directory')
def import_markdown(file_path, interactive, dry_run, manifest_dir):
    """Import tasks from a markdown brain dump file."""
    importer = MarkdownImporter(manifest_dir)
    importer.import_file(file_path, interactive=interactive, dry_run=dry_run)

if __name__ == "__main__":
    cli()
