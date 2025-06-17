from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime

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
    tasks: List[Task]
    
def validate_manifesto(data: dict) -> bool:
    """Validate manifesto against schema"""
    try:
        ManifestoSchema(**data)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False
