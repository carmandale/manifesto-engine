#!/bin/bash
# MANIFESTO ENGINE BOOTSTRAP v2.0 - with uv
# Copy this entire file to Claude Code and run: bash bootstrap-manifesto.sh

set -e  # Exit on error

echo "🚀 Starting Manifesto Engine Bootstrap..."

# Set the dev directory
DEV_DIR="/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev"

# Create main project directory
mkdir -p "$DEV_DIR/manifesto-engine" && cd "$DEV_DIR/manifesto-engine"

# Initialize git
echo "📁 Initializing git repository..."
git init
git config user.name "carmandale"
git config user.email "dale.carman@gmail.com"

# Later, after first commit:
echo ""
echo "📤 To push to GitHub:"
echo "  1. Create repo on GitHub: 'manifesto-engine'"
echo "  2. Run: git remote add origin https://github.com/YOUR_USERNAME/manifesto-engine.git"
echo "  3. Run: git push -u origin main"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p src/manifesto/{core,verify,orchestrate,templates}
mkdir -p tests
mkdir -p examples

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
.idea/
.vscode/
*.swp
.DS_Store
dist/
build/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
EOF

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "manifesto-engine"
version = "0.1.0"
description = "Universal project manifesto system for AI-driven development"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "jinja2>=3.1",
    "click>=8.1",
    "pydantic>=2.0",
    "rich>=13.0",
    "gitpython>=3.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=23.0",
    "mypy>=1.0",
]

[project.scripts]
manifesto = "manifesto.__main__:cli"
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
pyyaml>=6.0
jinja2>=3.1
click>=8.1
pydantic>=2.0
rich>=13.0
gitpython>=3.1
pytest>=7.0
EOF

# Create src/manifesto/__init__.py
cat > src/manifesto/__init__.py << 'EOF'
"""Manifesto Engine - Universal project orchestration"""
__version__ = "0.1.0"
EOF

# Create src/manifesto/__main__.py
cat > src/manifesto/__main__.py << 'EOF'
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
EOF

# Create src/manifesto/core/validator.py
cat > src/manifesto/core/validator.py << 'EOF'
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
EOF

# Create src/manifesto/core/injector.py
cat > src/manifesto/core/injector.py << 'EOF'
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml
from datetime import datetime

def inject_manifesto(project_path: Path, project_name: str, project_type: str) -> bool:
    """Inject manifesto into project"""
    try:
        # Create manifesto directory
        manifesto_dir = project_path / "docs" / "_MANIFESTO"
        manifesto_dir.mkdir(parents=True, exist_ok=True)
        
        # Get template path
        template_dir = Path(__file__).parent.parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        # Read or create template
        template_content = get_template_content()
        
        # Create Jinja2 template
        from jinja2 import Template
        template = Template(template_content)
        
        # Render with project specifics
        content = template.render(
            project_id=f"PRD-{datetime.now().year}-{project_name.upper()[:3]}-AVP",
            title=project_name,
            project_type=project_type,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Write manifesto
        with open(manifesto_dir / "manifesto.yaml", "w") as f:
            f.write(content)
        
        # Create supporting files
        readme_content = f"""# {project_name} Manifesto

Project orchestration documents for AI agents.

## Structure
- `manifesto.yaml` - Main project contract
- `tasks/` - Task completion proofs
- `reviews/` - Code review results

## Usage
```bash
manifesto verify TASK-001
manifesto status
```
"""
        (manifesto_dir / "README.md").write_text(readme_content)
        (manifesto_dir / "tasks").mkdir(exist_ok=True)
        (manifesto_dir / "reviews").mkdir(exist_ok=True)
        
        # Create .gitkeep files
        (manifesto_dir / "tasks" / ".gitkeep").touch()
        (manifesto_dir / "reviews" / ".gitkeep").touch()
        
        return True
    except Exception as e:
        print(f"Injection error: {e}")
        return False

def get_template_content():
    """Get the manifesto template"""
    return '''# AUTO-GENERATED MANIFESTO - DO NOT EDIT HEADER
# Generated: {{ date }}
# Engine Version: 0.1.0

prd_id: "{{ project_id }}"
title: "{{ title }}"
status: "Draft"
owner: "AI Orchestrator"
stakeholders: ["Product", "Engineering", "Design"]
target_release: "TBD"

tech_stack:
  {% if project_type == 'visionos' -%}
  - swift
  - visionos
  - realitykit
  - arkit
  {% else -%}
  - {{ project_type }}
  {% endif %}

metrics:
  north_star: "User engagement rate"
  guardrails:
    - name: "Load time"
      target: "< 2s"
      measurement: "Time to first interactive frame"
    - name: "Crash-free sessions"
      target: "> 99.8%"
      measurement: "Sessions without fatal errors"
    {% if project_type == 'visionos' -%}
    - name: "Frame rate"
      target: ">= 90 fps"
      measurement: "RealityKit performance profiler"
    - name: "Thermal state"
      target: "nominal"
      measurement: "Peak 5-minute usage"
    {% endif %}

dependencies:
  {% if project_type == 'visionos' -%}
  - "visionOS SDK >= 2.0"
  - "Xcode >= 15.0"
  - "Reality Composer Pro"
  {% endif %}
  - "Git"
  - "Manifesto Engine >= 0.1.0"

# TASKS - Maximum 8, each with single numeric acceptance test
tasks:
  - id: "TASK-001"
    description: "Initialize {{ project_type }} project structure"
    owner_role: "DEV-AGENT"
    depends_on: []
    acceptance:
      file_exists:
        {% if project_type == 'visionos' -%}
        - "Package.swift"
        - "Sources/{{ title }}/App.swift"
        - "Sources/{{ title }}/ContentView.swift"
        {% else -%}
        - "src/main.py"
        {% endif %}

  - id: "TASK-002"
    description: "Create immersive space entry point"
    owner_role: "DEV-AGENT"
    depends_on: ["TASK-001"]
    acceptance:
      file_contains:
        {% if project_type == 'visionos' -%}
        "Sources/{{ title }}/App.swift": "ImmersiveSpace"
        {% endif %}
      command_succeeds:
        - "swift build"

  - id: "TASK-003"
    description: "Set up RealityKit scene"
    owner_role: "DEV-AGENT"
    depends_on: ["TASK-002"]
    acceptance:
      file_exists:
        - "Sources/{{ title }}/ImmersiveView.swift"
      file_contains:
        "Sources/{{ title }}/ImmersiveView.swift": "RealityView"

# Agent Configuration
agents:
  supervisor:
    model: "claude-opus-4"
    role: "Orchestrate task execution and review"
  workers:
    - model: "claude-sonnet-4"
      role: "DEV-AGENT"
      max_concurrent: 3
    - model: "claude-sonnet-4"
      role: "TEST-AGENT"
      max_concurrent: 2

# Review Checklists
checklists:
  swift:
    - "No force unwrapping (!)"
    - "Memory management verified"
    - "Error handling implemented"
    - "Performance within budget"
    {% if project_type == 'visionos' -%}
    - "RealityKit entities released"
    - "Spatial tracking initialized"
    {% endif %}
'''
EOF

# Create src/manifesto/verify/base.py
cat > src/manifesto/verify/base.py << 'EOF'
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
EOF

# Create src/manifesto/verify/swift.py
cat > src/manifesto/verify/swift.py << 'EOF'
import subprocess
import json
from pathlib import Path
from typing import Tuple, Dict, Any
from .base import BaseVerifier

class SwiftVerifier(BaseVerifier):
    def run_tests(self, test_spec: str) -> Tuple[bool, str]:
        """Run Swift tests"""
        try:
            cmd = ["swift", "test", "--filter", test_spec] if " " in test_spec else ["swift", "test"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def verify_vision_pro_setup(self) -> Dict[str, bool]:
        """Verify Vision Pro specific setup"""
        checks = {}
        
        # Check for RealityKit imports
        swift_files = list(Path(".").rglob("*.swift"))
        has_realitykit = any(
            "import RealityKit" in f.read_text() 
            for f in swift_files
            if f.exists()
        )
        checks['realitykit_imported'] = has_realitykit
        
        # Check Package.swift for visionOS platform
        package_swift = Path("Package.swift")
        if package_swift.exists():
            content = package_swift.read_text()
            checks['visionos_platform'] = "visionOS" in content
        
        return checks
EOF

# Create the main executable
cat > manifesto << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from manifesto.__main__ import cli
    cli()
except ImportError as e:
    print(f"Error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)
EOF
chmod +x manifesto

# Create README
cat > README.md << 'EOF'
# Manifesto Engine

Zero-ambiguity project orchestration for AI agents.

## Installation

```bash
pip install -r requirements.txt
# or
pip install -e .
```

## Quick Start

```bash
# Initialize new Vision Pro project
./manifesto init --type visionos --name "My App"

# Verify task completion
./manifesto verify TASK-001

# Check project status
./manifesto status
```

## Core Principles

1. **No Lies** - Every task has cryptographic proof of completion
2. **No Ambiguity** - Single numeric acceptance test per requirement  
3. **Universal** - Works with any language or framework

## For AI Agents

When given a task:
1. Read `docs/_MANIFESTO/manifesto.yaml`
2. Find your task ID and acceptance criteria
3. Complete ALL acceptance criteria
4. Run `manifesto verify TASK-XXX`
5. Include the verification output in your response

## Project Structure

```
your-project/
└── docs/
    └── _MANIFESTO/
        ├── manifesto.yaml    # Project contract
        ├── tasks/           # Completion proofs
        └── reviews/         # Review results
```

## Verification Output

Tasks create cryptographic proofs in `docs/_MANIFESTO/tasks/`:
- Timestamp of completion
- File hashes of created artifacts
- Test execution results
- Performance metrics

## Extending

Add new language support by creating a verifier in `src/manifesto/verify/`:
```python
from .base import BaseVerifier

class MyLangVerifier(BaseVerifier):
    def run_tests(self, test_spec: str):
        # Implement language-specific test runner
        pass
```
EOF

# Commit everything
git add -A
git commit -m "Initial manifesto engine implementation"

echo "✅ Manifesto Engine created successfully!"

# Setup Python environment with uv
echo "🔧 Setting up Python environment with uv..."
if command -v uv &> /dev/null; then
    echo "✓ uv found: $(uv --version)"
else
    echo "❌ uv not found. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment and install dependencies
uv venv
echo "✓ Virtual environment created"

# Create activation helper
cat > activate.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
echo "✅ Manifesto environment activated"
echo "📍 Location: $VIRTUAL_ENV"
EOF
chmod +x activate.sh

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create success summary
cat > SETUP_COMPLETE.md << 'EOF'
# ✅ MANIFESTO ENGINE SETUP COMPLETE!

## Location
```
/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/manifesto-engine/
```

## Quick Start

1. **Activate environment**:
   ```bash
   ./activate.sh
   # or
   source .venv/bin/activate
   ```

2. **Test the CLI**:
   ```bash
   ./manifesto --help
   ```

3. **Inject into your Honda AVP project**:
   ```bash
   ./manifesto init --type visionos --name "Honda AVP" --path "../honda-avp"
   ```

4. **Verify tasks**:
   ```bash
   cd ../honda-avp
   ../manifesto-engine/manifesto verify TASK-001
   ```

## For AI Agents

Give them this instruction:
> "Complete TASK-001 from the manifesto at docs/_MANIFESTO/manifesto.yaml and run verification"

## Next Steps

1. Customize the manifesto template for your Honda AVP project
2. Define your specific tasks and acceptance criteria
3. Set up Claude Code agents with task assignments
EOF

echo ""
echo "🎉 SUCCESS! Manifesto Engine is ready!"
echo "📁 Location: $PWD"
echo "📄 See SETUP_COMPLETE.md for next steps"
echo ""
echo "To activate the environment:"
echo "  ./activate.sh"