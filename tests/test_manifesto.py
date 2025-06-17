import pytest
from pathlib import Path
import yaml
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from manifesto.core.validator import validate_manifesto, ManifestoSchema

def test_manifest_schema():
    """Test that a valid manifesto passes validation"""
    valid_manifest = {
        "prd_id": "PRD-2025-TEST",
        "title": "Test Project",
        "status": "Draft",
        "owner": "Test Owner",
        "tech_stack": ["python"],
        "metrics": {
            "north_star": "Test metric",
            "guardrails": [
                {"name": "Performance", "target": "< 100ms"}
            ]
        },
        "tasks": [
            {
                "id": "TASK-001",
                "description": "Test task",
                "owner_role": "DEV-AGENT",
                "depends_on": [],
                "acceptance": {
                    "file_exists": ["test.py"]
                }
            }
        ]
    }
    
    assert validate_manifesto(valid_manifest) == True

def test_invalid_task_id():
    """Test that invalid task ID format fails"""
    invalid_manifest = {
        "prd_id": "PRD-2025-TEST",
        "title": "Test Project",
        "status": "Draft",
        "owner": "Test Owner",
        "tech_stack": ["python"],
        "metrics": {
            "north_star": "Test metric",
            "guardrails": []
        },
        "tasks": [
            {
                "id": "INVALID-ID",  # Should be TASK-XXX
                "description": "Test task",
                "owner_role": "DEV-AGENT",
                "depends_on": [],
                "acceptance": {}
            }
        ]
    }
    
    assert validate_manifesto(invalid_manifest) == False

def test_task_description_length():
    """Test that task descriptions have max length"""
    long_description = "x" * 200  # Over 120 char limit
    invalid_manifest = {
        "prd_id": "PRD-2025-TEST",
        "title": "Test Project",
        "status": "Draft",
        "owner": "Test Owner",
        "tech_stack": ["python"],
        "metrics": {
            "north_star": "Test metric",
            "guardrails": []
        },
        "tasks": [
            {
                "id": "TASK-001",
                "description": long_description,
                "owner_role": "DEV-AGENT",
                "depends_on": [],
                "acceptance": {}
            }
        ]
    }
    
    assert validate_manifesto(invalid_manifest) == False
