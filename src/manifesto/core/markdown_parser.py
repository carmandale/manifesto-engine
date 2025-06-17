"""Markdown parser for brain dump import functionality."""
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


@dataclass
class ExtractedItem:
    """Represents an extracted task or epic from markdown."""
    item_type: str  # 'epic' or 'task'
    title: str
    description: str
    parent: Optional[str] = None  # For tasks under epics
    acceptance_hints: List[str] = None
    commands: List[str] = None
    source_line: int = 0


class MarkdownParser:
    """Parse markdown files to extract tasks and epics."""
    
    # Patterns that indicate actionable items
    ACTION_PATTERNS = [
        r'need(?:s)? to\s+(.+)',
        r'must\s+(.+)',
        r'should\s+(.+)',
        r'will\s+(.+)',
        r'fix(?:ing)?\s+(.+)',
        r'create\s+(.+)',
        r'implement\s+(.+)',
        r'add(?:ing)?\s+(.+)',
        r'optimize\s+(.+)',
        r'profile\s+(.+)',
        r'capture\s+(.+)',
        r'reduce\s+(.+)',
    ]
    
    # Patterns for acceptance criteria
    ACCEPTANCE_PATTERNS = [
        r'success:\s*(.+)',
        r'done when:\s*(.+)',
        r'complete when:\s*(.+)',
        r'acceptance:\s*(.+)',
        r'criteria:\s*(.+)',
    ]
    
    def __init__(self):
        self.items: List[ExtractedItem] = []
        self.current_epic: Optional[str] = None
    
    def parse_file(self, file_path: str) -> List[ExtractedItem]:
        """Parse a markdown file and extract items."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        self.items = []
        self.current_epic = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check for headers (potential epics)
            if line.startswith('#'):
                self._process_header(line, i)
            
            # Check for list items (potential tasks)
            elif line.startswith(('- ', '* ', '+ ')):
                self._process_list_item(line, i)
            
            # Check for action patterns in paragraphs
            else:
                self._process_paragraph(line, lines, i)
            
            i += 1
        
        return self.items
    
    def _process_header(self, line: str, line_num: int):
        """Process markdown headers as potential epics."""
        level = len(line) - len(line.lstrip('#'))
        title = line.lstrip('#').strip()
        
        if level == 1:
            # Top-level header - definitely an epic
            self.current_epic = title
            self.items.append(ExtractedItem(
                item_type='epic',
                title=title,
                description=f"Epic for {title}",
                source_line=line_num
            ))
        elif level == 2 and self.current_epic:
            # Second-level might be a task under current epic
            self._extract_task_from_text(title, line_num, parent_epic=self.current_epic)
    
    def _process_list_item(self, line: str, line_num: int):
        """Process list items as potential tasks."""
        # Remove list marker
        text = line.lstrip('- *+').strip()
        self._extract_task_from_text(text, line_num, parent_epic=self.current_epic)
    
    def _process_paragraph(self, line: str, all_lines: List[str], line_num: int):
        """Process paragraph text for action patterns."""
        # Look for multi-line paragraphs
        paragraph = line
        i = line_num + 1
        while i < len(all_lines) and all_lines[i].strip() and not all_lines[i].startswith(('#', '-', '*', '+')):
            paragraph += ' ' + all_lines[i].strip()
            i += 1
        
        # Check for action patterns
        for pattern in self.ACTION_PATTERNS:
            matches = re.finditer(pattern, paragraph.lower())
            for match in matches:
                action_text = match.group(0)
                # Extract the full sentence containing the action
                sentences = re.split(r'[.!?]\s+', paragraph)
                for sentence in sentences:
                    if action_text.lower() in sentence.lower():
                        self._extract_task_from_text(sentence.strip(), line_num, parent_epic=self.current_epic)
                        break
    
    def _extract_task_from_text(self, text: str, line_num: int, parent_epic: Optional[str] = None):
        """Extract a task from text."""
        # Skip if too short or looks like a note
        if len(text) < 10 or text.startswith(('Note:', 'TODO:', 'FIXME:')):
            return
        
        # Look for acceptance criteria in the text
        acceptance_hints = []
        for pattern in self.ACCEPTANCE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                acceptance_hints.append(match.group(1).strip())
        
        # Look for commands (backtick blocks)
        commands = re.findall(r'`([^`]+)`', text)
        
        # Clean up the title
        title = text
        for pattern in self.ACCEPTANCE_PATTERNS:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        title = re.sub(r'`[^`]+`', '', title)  # Remove inline code
        title = title.strip(' .,;:')
        
        # Only add if we have a meaningful title
        if len(title) > 5:
            self.items.append(ExtractedItem(
                item_type='task',
                title=self._clean_title(title),
                description=text,
                parent=parent_epic,
                acceptance_hints=acceptance_hints if acceptance_hints else None,
                commands=commands if commands else None,
                source_line=line_num
            ))
    
    def _clean_title(self, title: str) -> str:
        """Clean up title for display."""
        # Remove common prefixes
        title = re.sub(r'^(we )?(need to |must |should |will )', '', title.lower())
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        # Limit length
        if len(title) > 60:
            title = title[:57] + '...'
        return title
    
    def group_items(self) -> Dict[str, List[ExtractedItem]]:
        """Group items by epic."""
        grouped = {'standalone': []}
        
        for item in self.items:
            if item.item_type == 'epic':
                grouped[item.title] = []
            elif item.parent:
                if item.parent in grouped:
                    grouped[item.parent].append(item)
                else:
                    grouped[item.parent] = [item]
            else:
                grouped['standalone'].append(item)
        
        # Remove empty groups
        return {k: v for k, v in grouped.items() if v or k != 'standalone'}
    
    def display_structure(self, grouped_items: Dict[str, List[ExtractedItem]]):
        """Display the extracted structure for review."""
        console.print("\n[bold blue]Extracted Structure:[/bold blue]\n")
        
        task_count = sum(len(tasks) for tasks in grouped_items.values())
        epic_count = len([k for k in grouped_items.keys() if k != 'standalone'])
        
        console.print(f"Found [green]{epic_count}[/green] epics, [green]{task_count}[/green] potential tasks\n")
        
        for epic_name, tasks in grouped_items.items():
            if epic_name != 'standalone':
                console.print(f"[bold yellow]EPIC: {epic_name}[/bold yellow]")
                for task in tasks:
                    console.print(f"  - {task.title}")
                    if task.acceptance_hints:
                        console.print(f"    [dim]Acceptance: {task.acceptance_hints[0]}[/dim]")
                console.print()
        
        if grouped_items.get('standalone'):
            console.print("[bold yellow]Standalone Tasks:[/bold yellow]")
            for task in grouped_items['standalone']:
                console.print(f"  - {task.title}")
                if task.acceptance_hints:
                    console.print(f"    [dim]Acceptance: {task.acceptance_hints[0]}[/dim]")


class MarkdownImporter:
    """Import tasks from markdown brain dumps."""
    
    def __init__(self, manifest_dir: str = "docs/_MANIFESTO"):
        self.manifest_dir = Path(manifest_dir)
        self.parser = MarkdownParser()
        self.tasks_dir = self.manifest_dir / "tasks"
        self.tasks_dir.mkdir(exist_ok=True)
    
    def import_file(self, file_path: str, interactive: bool = True, dry_run: bool = False):
        """Import tasks from a markdown file."""
        console.print(f"\n[bold]Importing from:[/bold] {file_path}")
        
        # Parse the file
        items = self.parser.parse_file(file_path)
        if not items:
            console.print("[yellow]No actionable items found in file.[/yellow]")
            return
        
        # Group items
        grouped = self.parser.group_items()
        
        # Display structure
        self.parser.display_structure(grouped)
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - No files will be created[/yellow]")
            return
        
        # Interactive clarification
        if interactive:
            if not Confirm.ask("\nContinue with import?", default=True):
                console.print("[red]Import cancelled[/red]")
                return
            
            # Allow editing if needed
            grouped = self._interactive_clarification(grouped)
        
        # Create tasks
        created_tasks = self._create_tasks(grouped)
        
        console.print(f"\n[bold green]✅ Import complete![/bold green]")
        console.print(f"Created {len(created_tasks)} task files")
    
    def _interactive_clarification(self, grouped: Dict[str, List[ExtractedItem]]) -> Dict[str, List[ExtractedItem]]:
        """Allow user to clarify and edit extracted items."""
        # For now, return as-is
        # Future: implement interactive editing
        return grouped
    
    def _create_tasks(self, grouped: Dict[str, List[ExtractedItem]]) -> List[str]:
        """Create task files from grouped items."""
        from .task_loader import load_tasks
        
        created = []
        
        # Get next task ID
        existing_tasks = load_tasks(str(self.manifest_dir))
        existing_ids = [int(t['id'].split('-')[1]) for t in existing_tasks if t.get('id', '').startswith('TASK-')]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        # Create tasks
        for epic_name, tasks in grouped.items():
            for task in tasks:
                task_id = f"TASK-{next_id:03d}"
                task_data = {
                    'id': task_id,
                    'title': task.title,
                    'description': task.description,
                    'owner_role': 'DEV-AGENT',
                    'depends_on': [],
                    'vision_link': f"Extracted from brain dump to support {epic_name if epic_name != 'standalone' else 'project goals'}",
                    'acceptance': {}
                }
                
                # Add acceptance criteria if found
                if task.acceptance_hints:
                    task_data['acceptance']['notes'] = task.acceptance_hints
                
                if task.commands:
                    task_data['acceptance']['command_succeeds'] = task.commands
                
                # Write task file
                task_file = self.tasks_dir / f"{task_id}.yaml"
                import yaml
                
                with open(task_file, 'w') as f:
                    yaml.dump(task_data, f, default_flow_style=False, 
                             sort_keys=False, allow_unicode=True)
                
                created.append(task_id)
                console.print(f"Created: {task_file}")
                next_id += 1
        
        return created