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
        
        # Determine template path and load content
        template_dir = Path(__file__).parent.parent / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        custom_template_path = template_dir / "manifesto.yaml.j2"

        if custom_template_path.exists():
            template_content = custom_template_path.read_text()
        else:
            # Fallback to legacy built-in template
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
