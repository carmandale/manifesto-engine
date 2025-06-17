"""Prompt generator for creating worker and supervisor prompts from templates."""
import yaml
from pathlib import Path
from typing import Dict, Optional, Literal
from jinja2 import Template, Environment, FileSystemLoader
from datetime import datetime

from .task_loader import load_tasks


class PromptGenerator:
    """Generate prompts from templates and task data."""
    
    def __init__(self, manifest_dir: str = "docs/_MANIFESTO"):
        self.manifest_dir = Path(manifest_dir)
        self.template_dir = Path(__file__).parent.parent / "templates"
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Load manifesto data
        self.manifesto_data = self._load_manifesto()
    
    def _load_manifesto(self) -> Dict:
        """Load manifesto.yaml data."""
        manifest_file = self.manifest_dir / "manifesto.yaml"
        if manifest_file.exists():
            with open(manifest_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_task(self, task_id: str) -> Optional[Dict]:
        """Load a specific task by ID."""
        tasks = load_tasks(str(self.manifest_dir))
        for task in tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def _format_acceptance_criteria(self, acceptance: Dict) -> str:
        """Format acceptance criteria for display."""
        lines = []
        
        if 'file_exists' in acceptance:
            lines.append("**Files that must exist:**")
            for file in acceptance['file_exists']:
                lines.append(f"- {file}")
        
        if 'file_contains' in acceptance:
            lines.append("\n**Files must contain:**")
            for file, content in acceptance['file_contains'].items():
                lines.append(f"- {file}: '{content}'")
        
        if 'command_succeeds' in acceptance:
            lines.append("\n**Commands that must succeed:**")
            for cmd in acceptance['command_succeeds']:
                lines.append(f"- `{cmd}`")
        
        if 'performance_metric' in acceptance:
            lines.append("\n**Performance metrics:**")
            for metric, value in acceptance['performance_metric'].items():
                lines.append(f"- {metric}: {value}")
        
        if 'test_passes' in acceptance:
            lines.append(f"\n**Tests that must pass:** {acceptance['test_passes']}")
        
        return '\n'.join(lines) if lines else "No specific acceptance criteria defined"
    
    def generate_worker_prompt(self, task_id: str) -> Optional[str]:
        """Generate a worker prompt for a specific task."""
        task = self._load_task(task_id)
        if not task:
            return None
        
        # Load template
        template = self.env.get_template("worker_prompt.md")
        
        # Prepare context
        context = {
            'task_id': task['id'],
            'task_title': task.get('title', task.get('description', '')[:50]),
            'task_description': task.get('description', ''),
            'vision': self.manifesto_data.get('vision', 'No vision statement'),
            'north_star': self.manifesto_data.get('metrics', {}).get('north_star', 'No north star metric'),
            'vision_link': task.get('vision_link', 'No vision link specified'),
            'acceptance_criteria': self._format_acceptance_criteria(task.get('acceptance', {}))
        }
        
        return template.render(**context)
    
    def generate_supervisor_prompt(self, task_id: str, worker_summary: Optional[str] = None) -> Optional[str]:
        """Generate a supervisor review prompt for a specific task."""
        task = self._load_task(task_id)
        if not task:
            return None
        
        # Load template
        template = self.env.get_template("supervisor_review.md")
        
        # Prepare context
        context = {
            'task_id': task['id'],
            'task_title': task.get('title', task.get('description', '')[:50]),
            'worker_name': 'Claude Code',
            'completion_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'task_description': task.get('description', ''),
            'worker_summary': worker_summary or '[Worker summary will be inserted here after execution]',
            'feedback': '[Your feedback here]',
            'revision_1': '[First revision if needed]',
            'revision_2': '[Second revision if needed]',
            'revision_3': '[Third revision if needed]',
            'drift_warnings': '[Any drift warnings]',
            'commendations': '[What was done well]',
            'next_steps': '[What should happen next]'
        }
        
        return template.render(**context)
    
    def generate_prompt(self, task_id: str, prompt_type: Literal['worker', 'supervisor'], 
                       worker_summary: Optional[str] = None) -> Optional[str]:
        """Generate a prompt of the specified type."""
        if prompt_type == 'worker':
            return self.generate_worker_prompt(task_id)
        elif prompt_type == 'supervisor':
            return self.generate_supervisor_prompt(task_id, worker_summary)
        else:
            raise ValueError(f"Invalid prompt type: {prompt_type}")