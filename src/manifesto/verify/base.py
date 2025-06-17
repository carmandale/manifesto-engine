from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import hashlib
import json
from datetime import datetime
from typing import Dict, Tuple, Any, List

from datetime import datetime

class BaseVerifier(ABC):
    def __init__(self, manifest: dict):
        self.manifest = manifest
        
    def verify_task(self, task_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Verify a specific task"""
        # Find task
        task = None
        for t in self.manifest.get('tasks', []):
            if t['id'] == task_id:
                task = t
                break
                
        if not task:
            return False, {"error": {"passed": False, "details": f"Task {task_id} not found"}}
        
        results = {}
        acceptance = task.get('acceptance', {})
        
        # Check file existence
        if 'file_exists' in acceptance:
            for file_path in acceptance['file_exists']:
                exists = Path(file_path).exists()
                results[f"file_{Path(file_path).name}"] = {
                    "passed": exists,
                    "details": f"{'Found' if exists else 'Missing'}: {file_path}"
                }
        
        # Check file contents
        if 'file_contains' in acceptance:
            for file_path, pattern in acceptance['file_contains'].items():
                if Path(file_path).exists():
                    content = Path(file_path).read_text()
                    found = pattern in content
                    results[f"contains_{pattern[:20]}"] = {
                        "passed": found,
                        "details": f"Pattern {'found' if found else 'not found'} in {file_path}"
                    }
                else:
                    results[f"contains_{pattern[:20]}"] = {
                        "passed": False,
                        "details": f"File not found: {file_path}"
                    }
        
        # Run commands
        if 'command_succeeds' in acceptance:
            for cmd in acceptance['command_succeeds']:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                    passed = result.returncode == 0
                    output = result.stdout.decode()[:100] if passed else result.stderr.decode()[:100]
                    results[f"cmd_{cmd.split()[0]}"] = {
                        "passed": passed,
                        "details": output.strip()
                    }
                except Exception as e:
                    results[f"cmd_{cmd.split()[0]}"] = {
                        "passed": False,
                        "details": str(e)
                    }
        
        # Check if tests pass
        if 'test_passes' in acceptance:
            passed, output = self.run_tests(acceptance['test_passes'])
            results['tests'] = {
                "passed": passed,
                "details": output[:200]
            }
        
        # Generate verification proof
        if all(r['passed'] for r in results.values()):
            self.save_verification_proof(task_id, results)
        
        all_passed = all(r['passed'] for r in results.values())
        return all_passed, results
    
    def save_verification_proof(self, task_id: str, results: Dict[str, Any]):
        """Save cryptographic proof of task completion"""
        proof_dir = Path("docs/_MANIFESTO/tasks")
        proof_dir.mkdir(parents=True, exist_ok=True)
        
        proof = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "file_hashes": {}
        }
        
        # Hash relevant files
        for t in self.manifest.get('tasks', []):
            if t['id'] == task_id:
                for f in t.get('acceptance', {}).get('file_exists', []):
                    if Path(f).exists():
                        proof['file_hashes'][f] = self.hash_file(f)
        
        with open(proof_dir / f"{task_id}_proof.json", "w") as f:
            json.dump(proof, f, indent=2)
    
    @abstractmethod
    def run_tests(self, test_spec: str) -> Tuple[bool, str]:
        """Run language-specific tests"""
        pass
    
    def hash_file(self, file_path: str) -> str:
        """Generate SHA256 hash of file"""
        try:
            return hashlib.sha256(Path(file_path).read_bytes()).hexdigest()
        except:
            return "error"
