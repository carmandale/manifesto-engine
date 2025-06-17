#!/usr/bin/env python3
import click
import yaml
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .core.injector import inject_manifesto
from .core.validator import validate_manifesto
from .verify.swift import SwiftVerifier

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
    
    verifier = SwiftVerifier(data)
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
        console.print(f"[bold]Project:[/bold] {data['title']}")
        console.print(f"[bold]Status:[/bold] {data['status']}")
        console.print(f"[bold]Tasks:[/bold] {len(data.get('tasks', []))}")
    else:
        console.print("[red]No manifesto found in current directory[/red]")

if __name__ == "__main__":
    cli()
