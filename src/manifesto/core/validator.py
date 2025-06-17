from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from pathlib import Path
from .task_loader import load_tasks

class AcceptanceCriteria(BaseModel):
    file_exists: Optional[List[str]] = None
    file_contains: Optional[Dict[str, str]] = None
    command_succeeds: Optional[List[str]] = None
    performance_metric: Optional[Dict[str, float]] = None
    test_passes: Optional[str] = None

class Task(BaseModel):
    id: str = Field(pattern=r"^TASK-\d{3}$")
    description: str = Field(max_length=120)
    owner_role: str
    vision_link: str = Field(description="How this task supports the main vision")
    depends_on: List[str] = []
    acceptance: AcceptanceCriteria

class Metric(BaseModel):
    name: str
    target: str
    measurement: Optional[str] = None

class Metrics(BaseModel):
    north_star: str
    guardrails: List[Metric]

class ManifestoSchema(BaseModel):
    prd_id: str
    title: str
    status: Literal["Draft", "Approved", "In-dev", "Frozen"]
    owner: str
    tech_stack: List[str]
    metrics: Metrics
    tasks: Optional[List[Task]] = None  # Made optional for task directory support
    
def _enforce_radical_constraints(data: dict, manifest_dir: Optional[str] = None):
    """Raise ValidationError if radical constraints violated."""
    # Load tasks from directory or manifest
    if manifest_dir:
        tasks = load_tasks(manifest_dir)
    else:
        tasks = data.get("tasks", [])
    
    if len(tasks) > 8:
        raise ValidationError([{"loc": ("tasks",), "msg": "More than 8 tasks defined", "type": "value_error"}])

    for t in tasks:
        desc_words = t.get("description", "").strip().split()
        if len(desc_words) > 12:
            raise ValidationError([{"loc": ("tasks", t.get("id", "?"), "description"), "msg": "Description exceeds 12 words", "type": "value_error"}])


def validate_manifesto(data: dict, manifest_dir: Optional[str] = None) -> bool:
    """Validate manifesto against schema and radical constraints."""
    try:
        ManifestoSchema(**data)  # base schema validation
        _enforce_radical_constraints(data, manifest_dir)  # additional constraints
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False
