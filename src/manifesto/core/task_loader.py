"""Task loader module for loading tasks from individual files or manifesto.yaml"""
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def load_task_file(file_path: Path) -> Optional[Dict]:
    """Load a single task from a YAML file."""
    try:
        with open(file_path) as f:
            task = yaml.safe_load(f)
            # Validate has required fields
            if not task.get('id'):
                logger.warning(f"Task file {file_path} missing 'id' field")
                return None
            # Add source file for duplicate detection
            task['source_file'] = str(file_path)
            return task
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
        return None


def check_duplicate_ids(tasks: List[Dict]) -> None:
    """Check for duplicate task IDs and raise ValueError if found."""
    seen_ids = {}
    for task in tasks:
        task_id = task.get('id')
        if task_id in seen_ids:
            raise ValueError(
                f"Duplicate task ID '{task_id}' in files: "
                f"{seen_ids[task_id]} and {task.get('source_file', 'manifesto.yaml')}"
            )
        seen_ids[task_id] = task.get('source_file', 'manifesto.yaml')


def load_tasks(manifest_dir: str) -> List[Dict]:
    """
    Load tasks from tasks/ directory if it exists, otherwise from manifesto.yaml.
    
    Args:
        manifest_dir: Path to the directory containing manifesto.yaml
        
    Returns:
        List of task dictionaries
    """
    manifest_path = Path(manifest_dir)
    tasks_dir = manifest_path / "tasks"
    tasks = []
    
    # Try loading from tasks/ directory first
    if tasks_dir.exists() and tasks_dir.is_dir():
        logger.info(f"Loading tasks from {tasks_dir}")
        for task_file in sorted(tasks_dir.glob("TASK-*.yaml")):
            task = load_task_file(task_file)
            if task:
                tasks.append(task)
    
    # If no tasks found in directory, fall back to manifesto.yaml
    if not tasks:
        manifest_file = manifest_path / "manifesto.yaml"
        if manifest_file.exists():
            logger.info(f"Loading tasks from {manifest_file}")
            with open(manifest_file) as f:
                data = yaml.safe_load(f)
                tasks = data.get('tasks', [])
                # Add source_file for consistency
                for task in tasks:
                    task['source_file'] = 'manifesto.yaml'
    
    # Check for duplicate IDs
    if tasks:
        check_duplicate_ids(tasks)
    
    return tasks