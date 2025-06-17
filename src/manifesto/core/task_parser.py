"""Task parser for speed-of-thought task creation"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()


class TaskParser:
    """Parse natural language into structured tasks with interactive clarification."""
    
    # Keywords that indicate different task types
    ACTION_KEYWORDS = {
        'fix': 'repair',
        'create': 'build',
        'implement': 'build',
        'add': 'build',
        'refactor': 'improve',
        'optimize': 'improve',
        'test': 'verify',
        'debug': 'repair',
        'update': 'modify',
        'remove': 'delete',
        'migrate': 'transform'
    }
    
    def __init__(self, manifest_dir: str = "docs/_MANIFESTO"):
        self.manifest_dir = Path(manifest_dir)
        self.tasks_dir = self.manifest_dir / "tasks"
        self.tasks_dir.mkdir(exist_ok=True)
        self.vision = self._load_vision()
    
    def _load_vision(self) -> Dict[str, str]:
        """Load vision from manifesto.yaml"""
        manifest_file = self.manifest_dir / "manifesto.yaml"
        if manifest_file.exists():
            with open(manifest_file) as f:
                data = yaml.safe_load(f)
                return {
                    'vision': data.get('vision', 'No vision statement found'),
                    'north_star': data.get('metrics', {}).get('north_star', 'No north star metric found')
                }
        return {'vision': 'No manifesto found', 'north_star': 'No north star metric'}
    
    def parse_description(self, text: str) -> Dict[str, any]:
        """Parse free-form text into task components."""
        # Extract action
        action = None
        for keyword, action_type in self.ACTION_KEYWORDS.items():
            if keyword in text.lower():
                action = action_type
                break
        
        # Extract potential targets (files, features, etc.)
        # Look for quoted strings or capitalized words
        quoted = re.findall(r'"([^"]*)"', text)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Extract numeric values (could be metrics)
        numbers = re.findall(r'\b\d+\b', text)
        
        return {
            'raw_text': text,
            'action': action,
            'quoted_items': quoted,
            'entities': capitalized,
            'numbers': numbers,
            'has_command': 'command' in text.lower() or 'run' in text.lower(),
            'has_file': any(word in text.lower() for word in ['file', 'files', '.yaml', '.py', '.swift'])
        }
    
    def generate_task_id(self) -> str:
        """Generate next available task ID."""
        existing_ids = []
        
        # Check task files
        for task_file in self.tasks_dir.glob("TASK-*.yaml"):
            match = re.match(r'TASK-(\d{3})\.yaml', task_file.name)
            if match:
                existing_ids.append(int(match.group(1)))
        
        # Also check manifesto.yaml in case of mixed state
        manifest_file = self.manifest_dir / "manifesto.yaml"
        if manifest_file.exists():
            with open(manifest_file) as f:
                data = yaml.safe_load(f)
                for task in data.get('tasks', []):
                    match = re.match(r'TASK-(\d{3})', task.get('id', ''))
                    if match:
                        existing_ids.append(int(match.group(1)))
        
        next_id = max(existing_ids) + 1 if existing_ids else 1
        return f"TASK-{next_id:03d}"
    
    def clarify_task(self, parsed: Dict) -> Optional[Dict]:
        """Interactive clarification to build structured task."""
        console.print("\n[bold blue]SUPERVISOR: Breaking this down into an atomic task...[/bold blue]\n")
        
        # Show vision context
        console.print(f"[bold yellow]PROJECT VISION:[/bold yellow] {self.vision['vision']}")
        console.print(f"[bold yellow]NORTH STAR:[/bold yellow] {self.vision['north_star']}\n")
        
        # Start with parsed info
        task_data = {
            'id': self.generate_task_id(),
            'owner_role': 'DEV-AGENT',  # Default
            'depends_on': [],
            'acceptance': {}
        }
        
        # Title - suggest based on action and entities
        suggested_title = self._suggest_title(parsed)
        task_data['title'] = Prompt.ask(
            "Task title (short, actionable)", 
            default=suggested_title
        )
        
        # Description - use the raw text as starting point
        console.print(f"\n[dim]Original request: {parsed['raw_text']}[/dim]")
        task_data['description'] = Prompt.ask(
            "\nTask description (can be multi-line, press Enter twice to finish)",
            default=parsed['raw_text']
        )
        
        # Vision alignment - CRITICAL
        console.print("\n[bold red]VISION ALIGNMENT CHECK[/bold red]")
        suggested_link = self._suggest_vision_link(parsed, task_data['title'])
        task_data['vision_link'] = Prompt.ask(
            "How does this task support the vision?",
            default=suggested_link
        )
        
        # Validate vision link
        if not self._validate_vision_link(task_data['vision_link']):
            console.print("[yellow]⚠️  Vision link seems vague. Please be specific about HOW this supports the vision.[/yellow]")
            task_data['vision_link'] = Prompt.ask("Please provide a clearer vision link")
        
        # Acceptance criteria
        console.print("\n[bold]Acceptance Criteria:[/bold]")
        
        # Ask about specific types based on parsed content
        if parsed['has_file'] or 'create' in parsed['raw_text'].lower():
            files = Prompt.ask("Files that must exist (comma-separated)", default="")
            if files:
                task_data['acceptance']['file_exists'] = [f.strip() for f in files.split(',')]
        
        if parsed['has_command']:
            cmd = Prompt.ask("Command that must succeed", default="")
            if cmd:
                task_data['acceptance']['command_succeeds'] = [cmd]
        
        if parsed['numbers'] and any(word in parsed['raw_text'].lower() for word in ['error', 'count', 'metric']):
            metric_name = Prompt.ask("Performance metric name", default="error_count")
            metric_value = Prompt.ask("Target value", default="0")
            try:
                task_data['acceptance']['performance_metric'] = {
                    metric_name: float(metric_value)
                }
            except ValueError:
                pass
        
        # Additional criteria
        if Confirm.ask("Add test specification?", default=False):
            test_spec = Prompt.ask("Test specification")
            task_data['acceptance']['test_passes'] = test_spec
        
        # Dependencies
        deps = Prompt.ask("Depends on tasks (comma-separated IDs)", default="")
        if deps:
            task_data['depends_on'] = [d.strip() for d in deps.split(',')]
        
        # Owner role
        task_data['owner_role'] = Prompt.ask(
            "Owner role", 
            default="DEV-AGENT",
            choices=["DEV-AGENT", "TEST-AGENT", "ARCHITECT", "SUPERVISOR"]
        )
        
        # Show preview
        console.print("\n[bold green]Task Preview:[/bold green]")
        self._preview_task(task_data)
        
        if Confirm.ask("\nCreate this task?", default=True):
            return task_data
        
        return None
    
    def _suggest_title(self, parsed: Dict) -> str:
        """Suggest a title based on parsed content."""
        action = parsed['action'] or 'handle'
        entities = parsed['entities'] or parsed['quoted_items'] or ['task']
        
        # Build title from action and first entity
        entity = entities[0] if entities else 'system'
        
        # Capitalize properly
        action_word = action.capitalize()
        
        # Common patterns
        if action == 'repair':
            return f"Fix {entity}"
        elif action == 'build':
            return f"Create {entity}"
        elif action == 'verify':
            return f"Test {entity}"
        else:
            return f"{action_word} {entity}"
    
    def _suggest_vision_link(self, parsed: Dict, title: str) -> str:
        """Suggest vision link based on keywords."""
        vision_keywords = {
            'speed': 'Reduces time to achieve results, supporting speed of thought',
            'fast': 'Accelerates development cycle for speed of thought',
            'error': 'Improves reliability and reduces ambiguity',
            'fix': 'Removes blockers that slow down creative flow',
            'create': 'Builds foundation for rapid iteration',
            'test': 'Ensures zero ambiguity through verification',
            'verify': 'Provides cryptographic proof supporting zero ambiguity vision',
            'align': 'Ensures all work stays focused on core vision'
        }
        
        text_lower = parsed['raw_text'].lower()
        for keyword, link in vision_keywords.items():
            if keyword in text_lower:
                return link
        
        # Default suggestion
        return "Supports the vision by..."
    
    def _validate_vision_link(self, vision_link: str) -> bool:
        """Check if vision link is specific enough."""
        vague_phrases = [
            'supports the vision',
            'helps the project',
            'makes things better',
            'improves the system',
            'good for the project'
        ]
        
        link_lower = vision_link.lower()
        
        # Too short
        if len(vision_link) < 20:
            return False
        
        # Contains vague phrases
        for phrase in vague_phrases:
            if phrase in link_lower and len(vision_link) < 50:
                return False
        
        # Should contain specific terms
        specific_indicators = ['by', 'through', 'enables', 'reduces', 'increases', 'ensures']
        has_specific = any(word in link_lower for word in specific_indicators)
        
        return has_specific
    
    def _preview_task(self, task_data: Dict):
        """Show task preview in YAML format."""
        # Format for display
        yaml_str = yaml.dump(task_data, default_flow_style=False, sort_keys=False)
        console.print(yaml_str)
    
    def create_task(self, description: str) -> Optional[str]:
        """Main entry point: create task from description."""
        start_time = datetime.now()
        
        # Parse the description
        parsed = self.parse_description(description)
        
        # Interactive clarification
        task_data = self.clarify_task(parsed)
        
        if not task_data:
            return None
        
        # Write task file
        task_file = self.tasks_dir / f"{task_data['id']}.yaml"
        
        # Use custom YAML formatting for nice output
        class LiteralStr(str):
            pass
        
        def literal_presenter(dumper, data):
            if '\n' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        
        yaml.add_representer(LiteralStr, literal_presenter)
        
        # Convert description to literal string if multiline
        if '\n' in task_data.get('description', ''):
            task_data['description'] = LiteralStr(task_data['description'])
        
        with open(task_file, 'w') as f:
            yaml.dump(task_data, f, default_flow_style=False, 
                     sort_keys=False, allow_unicode=True, width=80)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        console.print(f"\n✅ Created: {task_file}")
        console.print(f"⏱️  Time: {elapsed:.1f} seconds")
        
        return task_data['id']