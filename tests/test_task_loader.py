"""Tests for the task_loader module"""
import pytest
import yaml
import tempfile
from pathlib import Path
from src.manifesto.core.task_loader import load_tasks, load_task_file, check_duplicate_ids


class TestTaskLoader:
    
    def test_load_from_directory(self):
        """Test loading tasks from individual YAML files in tasks/ directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tasks_dir = tmpdir_path / "tasks"
            tasks_dir.mkdir()
            
            # Create test task files
            task1 = {
                "id": "TASK-001",
                "description": "First test task",
                "owner_role": "TEST-AGENT",
                "depends_on": [],
                "acceptance": {"file_exists": ["test1.txt"]}
            }
            task2 = {
                "id": "TASK-002", 
                "description": "Second test task",
                "owner_role": "TEST-AGENT",
                "depends_on": ["TASK-001"],
                "acceptance": {"file_exists": ["test2.txt"]}
            }
            
            with open(tasks_dir / "TASK-001.yaml", "w") as f:
                yaml.dump(task1, f)
            with open(tasks_dir / "TASK-002.yaml", "w") as f:
                yaml.dump(task2, f)
                
            # Load tasks
            tasks = load_tasks(str(tmpdir_path))
            
            assert len(tasks) == 2
            assert tasks[0]["id"] == "TASK-001"
            assert tasks[1]["id"] == "TASK-002"
            assert tasks[0]["source_file"].endswith("TASK-001.yaml")
            assert tasks[1]["source_file"].endswith("TASK-002.yaml")
    
    def test_load_from_manifesto_fallback(self):
        """Test fallback to loading tasks from manifesto.yaml when no tasks/ directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create manifesto with embedded tasks
            manifesto = {
                "prd_id": "TEST-001",
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
                        "description": "Embedded task",
                        "owner_role": "TEST-AGENT",
                        "depends_on": [],
                        "acceptance": {"file_exists": ["test.txt"]}
                    }
                ]
            }
            
            with open(tmpdir_path / "manifesto.yaml", "w") as f:
                yaml.dump(manifesto, f)
                
            # Load tasks
            tasks = load_tasks(str(tmpdir_path))
            
            assert len(tasks) == 1
            assert tasks[0]["id"] == "TASK-001"
            assert tasks[0]["source_file"] == "manifesto.yaml"
    
    def test_malformed_task_file(self):
        """Test handling of malformed task files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tasks_dir = tmpdir_path / "tasks"
            tasks_dir.mkdir()
            
            # Create valid task
            valid_task = {
                "id": "TASK-001",
                "description": "Valid task",
                "owner_role": "TEST-AGENT",
                "depends_on": [],
                "acceptance": {}
            }
            with open(tasks_dir / "TASK-001.yaml", "w") as f:
                yaml.dump(valid_task, f)
            
            # Create task without ID
            invalid_task = {
                "description": "Task without ID",
                "owner_role": "TEST-AGENT"
            }
            with open(tasks_dir / "TASK-002.yaml", "w") as f:
                yaml.dump(invalid_task, f)
                
            # Create unparseable YAML
            with open(tasks_dir / "TASK-003.yaml", "w") as f:
                f.write("invalid: yaml: content: [")
                
            # Load tasks - should only get the valid one
            tasks = load_tasks(str(tmpdir_path))
            
            assert len(tasks) == 1
            assert tasks[0]["id"] == "TASK-001"
    
    def test_duplicate_id_detection(self):
        """Test detection of duplicate task IDs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tasks_dir = tmpdir_path / "tasks"
            tasks_dir.mkdir()
            
            # Create two tasks with same ID
            task = {
                "id": "TASK-001",
                "description": "Duplicate task",
                "owner_role": "TEST-AGENT",
                "depends_on": [],
                "acceptance": {}
            }
            
            with open(tasks_dir / "TASK-001.yaml", "w") as f:
                yaml.dump(task, f)
            with open(tasks_dir / "TASK-001-duplicate.yaml", "w") as f:
                yaml.dump(task, f)
                
            # Should raise ValueError for duplicate IDs
            with pytest.raises(ValueError) as exc_info:
                load_tasks(str(tmpdir_path))
                
            assert "Duplicate task ID 'TASK-001'" in str(exc_info.value)
    
    def test_empty_directory(self):
        """Test loading from empty directory falls back to manifesto"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tasks_dir = tmpdir_path / "tasks"
            tasks_dir.mkdir()  # Empty tasks directory
            
            # No manifesto.yaml either
            tasks = load_tasks(str(tmpdir_path))
            assert tasks == []
    
    def test_load_task_file_directly(self):
        """Test loading a single task file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            task = {
                "id": "TASK-001",
                "description": "Test task",
                "owner_role": "TEST-AGENT"
            }
            yaml.dump(task, f)
            f.flush()
            
            loaded_task = load_task_file(Path(f.name))
            assert loaded_task is not None
            assert loaded_task["id"] == "TASK-001"
            
            Path(f.name).unlink()  # Clean up
    
    def test_check_duplicate_ids_function(self):
        """Test the check_duplicate_ids function directly"""
        tasks = [
            {"id": "TASK-001", "source_file": "file1.yaml"},
            {"id": "TASK-002", "source_file": "file2.yaml"},
            {"id": "TASK-001", "source_file": "file3.yaml"}
        ]
        
        with pytest.raises(ValueError) as exc_info:
            check_duplicate_ids(tasks)
            
        assert "file1.yaml and file3.yaml" in str(exc_info.value)