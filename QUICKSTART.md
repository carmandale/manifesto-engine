# Manifesto Engine Quick Start Guide

Zero-ambiguity project orchestration in 15 minutes.

## Table of Contents
1. [Installation](#installation)
2. [Adding to Your Project](#adding-to-your-project)
3. [Creating Tasks](#creating-tasks)
4. [Using Claude Code](#using-claude-code)
5. [Verification & Proof](#verification--proof)
6. [Advanced Workflows](#advanced-workflows)

## Plan → Execute Pattern

NEVER skip planning. ALWAYS:
1. Run `manifesto plan` – Agent outputs PLAN only
2. Review `docs/_MANIFESTO/plan.json`
3. Approve by typing `manifesto execute`
4. Agent executes tasks in order – stops on first failure

## Installation

### Prerequisites
- Python 3.11+
- [uv](https://astral.sh/uv) (for fast package management)
- Git

### Clone and Setup

```bash
# Clone the manifesto engine
git clone https://github.com/carmandale/manifesto-engine.git
cd manifesto-engine

# Activate the environment
./activate.sh

# Verify installation
./manifesto --help
```

## Adding to Your Project

### Step 1: Initialize Manifesto in Your Project

```bash
# Navigate to your project
cd /path/to/your/project

# Initialize manifesto (example: Vision Pro app)
/path/to/manifesto-engine/manifesto init --type visionos --name "My App"

# This creates:
# docs/
# └── _MANIFESTO/
#     ├── manifesto.yaml    # Your project contract
#     ├── tasks/           # Task completion proofs
#     └── reviews/         # Code review results
```

### Step 2: Review Generated Manifesto

Open `docs/_MANIFESTO/manifesto.yaml`:

```yaml
prd_id: "PRD-2025-MYA-APP"
title: "My App"
status: "Draft"
owner: "AI Orchestrator"

metrics:
  north_star: "User engagement rate"
  guardrails:
    - name: "Load time"
      target: "< 2s"
      measurement: "Time to first interactive frame"

tasks:
  - id: "TASK-001"
    description: "Initialize visionos project structure"
    owner_role: "DEV-AGENT"
    depends_on: []
    acceptance:
      file_exists:
        - "Package.swift"
        - "Sources/My App/App.swift"
```

## Creating Tasks

### Task Anatomy

Every task MUST have:
1. **Unique ID**: `TASK-XXX` format
2. **Description**: ≤ 120 characters
3. **Owner Role**: Who should complete it
4. **Dependencies**: Other tasks that must complete first
5. **Acceptance Criteria**: Verifiable proof of completion

### Example: Create a RealityKit Scene Task

Edit `docs/_MANIFESTO/manifesto.yaml` and add:

```yaml
  - id: "TASK-004"
    description: "Create Honda vehicle 3D scene with RealityKit"
    owner_role: "DEV-AGENT"
    depends_on: ["TASK-003"]  # Depends on immersive space setup
    acceptance:
      file_exists:
        - "Sources/HondaAVP/VehicleScene.swift"
        - "Sources/HondaAVP/Models/HondaVehicle.swift"
      file_contains:
        "Sources/HondaAVP/VehicleScene.swift": "ModelEntity"
        "Sources/HondaAVP/VehicleScene.swift": "AnchorEntity"
      command_succeeds:
        - "swift build"
      performance_metric:
        scene_load_time: 1.5  # Max 1.5 seconds
```

### Task Best Practices

1. **One Acceptance Test Per Requirement**
   ```yaml
   # GOOD: Single, measurable test
   performance_metric:
     api_response_time: 0.1  # 100ms

   # BAD: Vague or multiple tests
   description: "Make it fast and reliable"
   ```

2. **Atomic Tasks** (< 1 day of work)
   ```yaml
   # GOOD: Specific, completable
   description: "Implement user authentication with OAuth"

   # BAD: Too broad
   description: "Build entire app"
   ```

3. **Clear Dependencies**
   ```yaml
   depends_on: ["TASK-001", "TASK-002"]  # Must complete first
   ```

## Using Claude Code

### Step 1: Give Claude Code the Context

Create a prompt file `prompts/task-004.md`:

```markdown
# Task Assignment: TASK-004

Please complete TASK-004 from the manifesto located at:
`docs/_MANIFESTO/manifesto.yaml`

## Your Mission
1. Read the manifesto and understand TASK-004's acceptance criteria
2. Create all required files
3. Ensure all acceptance tests pass
4. Run verification: `manifesto verify TASK-004`
5. Show me the verification output

## Context
- Project: Honda AVP (Apple Vision Pro)
- Tech Stack: Swift, visionOS, RealityKit
- Dependencies: TASK-003 must already be complete

## Deliverables
1. All files created per acceptance criteria
2. Passing verification output
3. Brief explanation of implementation choices
```

### Step 2: Execute with Claude Code

```bash
# Give the task to Claude Code
claude-code --model claude-sonnet-4 --file prompts/task-004.md

# Or interactively:
claude-code --model claude-sonnet-4
> Complete TASK-004 from docs/_MANIFESTO/manifesto.yaml and show verification
```

### Step 3: Claude Code Response Example

Claude Code will:

```swift
// 1. Create Sources/HondaAVP/VehicleScene.swift
import RealityKit
import SwiftUI

struct VehicleScene: View {
    var body: some View {
        RealityView { content in
            // Create anchor at floor level
            let anchor = AnchorEntity(.plane(.horizontal, classification: .floor))
            
            // Load Honda vehicle model
            let vehicle = HondaVehicle.createModel()
            anchor.addChild(vehicle)
            
            content.add(anchor)
        }
    }
}

// 2. Create Sources/HondaAVP/Models/HondaVehicle.swift
import RealityKit

struct HondaVehicle {
    static func createModel() -> ModelEntity {
        // Create a placeholder vehicle (replace with actual model)
        let mesh = MeshResource.generateBox(size: [4, 1.5, 2])
        let material = SimpleMaterial(color: .red, isMetallic: true)
        let model = ModelEntity(mesh: mesh, materials: [material])
        
        // Position and scale
        model.position = [0, 0.75, 0]
        
        return model
    }
}

// 3. Run verification
$ manifesto verify TASK-004

[bold blue]Verifying task TASK-004...[/bold blue]

Task TASK-004 Verification
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check                      ┃ Status   ┃ Details                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ file_VehicleScene.swift    │ ✅ PASS  │ Found: Sources/HondaAVP/Vehicl... │
│ file_HondaVehicle.swift    │ ✅ PASS  │ Found: Sources/HondaAVP/Models... │
│ contains_ModelEntity       │ ✅ PASS  │ Pattern found in VehicleScene... │
│ contains_AnchorEntity      │ ✅ PASS  │ Pattern found in VehicleScene... │
│ cmd_swift                  │ ✅ PASS  │ Build succeeded                   │
│ scene_load_time           │ ✅ PASS  │ 0.89s < 1.5s target              │
└────────────────────────────┴──────────┴──────────────────────────────────┘

✅ Task TASK-004 completed successfully!
Proof saved to: docs/_MANIFESTO/tasks/TASK-004_proof.json
```

## Verification & Proof

### Understanding Verification

Every completed task generates cryptographic proof:

```bash
# View the proof
cat docs/_MANIFESTO/tasks/TASK-004_proof.json
```

```json
{
  "task_id": "TASK-004",
  "timestamp": "2025-06-17T10:30:45.123456",
  "results": {
    "file_VehicleScene.swift": {
      "passed": true,
      "details": "Found: Sources/HondaAVP/VehicleScene.swift"
    }
  },
  "file_hashes": {
    "Sources/HondaAVP/VehicleScene.swift": "sha256:a7f9e3b2c4d5...",
    "Sources/HondaAVP/Models/HondaVehicle.swift": "sha256:b8g0f4c3d5e6..."
  }
}
```

### Manual Verification

```bash
# Verify any task
manifesto verify TASK-001

# Check project status
manifesto status

# Verify all tasks
for i in {001..008}; do 
  manifesto verify TASK-$(printf "%03d" $i)
done
```

## Advanced Workflows

### 1. Parallel Task Execution

Create `orchestrate.sh`:

```bash
#!/bin/bash
# Run multiple Claude Code instances in parallel

# Tasks that can run in parallel (no dependencies on each other)
parallel_tasks=("TASK-005" "TASK-006" "TASK-007")

for task in "${parallel_tasks[@]}"; do
  echo "Assigning $task to Claude Code..."
  claude-code --model claude-sonnet-4 \
    --prompt "Complete $task from docs/_MANIFESTO/manifesto.yaml" \
    --output "outputs/$task.log" &
done

wait
echo "All parallel tasks completed!"

# Verify all
for task in "${parallel_tasks[@]}"; do
  manifesto verify $task
done
```

### 2. Supervisor Agent Pattern

Create `supervisor-prompt.md`:

```markdown
You are the Supervisor Agent for the Honda AVP project.

1. Read the manifesto at docs/_MANIFESTO/manifesto.yaml
2. Identify all incomplete tasks
3. Create an execution plan respecting dependencies
4. Generate individual prompts for each task
5. Report on overall project status

Output format:
- Execution order with reasoning
- Individual task assignments
- Risk assessment
- Suggested optimizations
```

### 3. GitHub Integration

After task completion:

```bash
# Create task completion issue
gh issue create \
  --title "[TASK-004] Completion Report" \
  --body-file docs/_MANIFESTO/tasks/TASK-004_proof.json \
  --label "task-completion"

# Create PR with task implementation
git checkout -b task-004-vehicle-scene
git add .
git commit -m "Complete TASK-004: Honda vehicle 3D scene"
git push origin task-004-vehicle-scene

gh pr create \
  --title "TASK-004: Honda vehicle 3D scene" \
  --body "Implements RealityKit scene per manifesto acceptance criteria"
```

### 4. Custom Verifiers

Add support for new languages by creating `src/manifesto/verify/javascript.py`:

```python
from .base import BaseVerifier
import subprocess
from typing import Tuple

class JavaScriptVerifier(BaseVerifier):
    def run_tests(self, test_spec: str) -> Tuple[bool, str]:
        """Run JavaScript tests"""
        cmd = ["npm", "test", "--", f"--grep={test_spec}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
```

## Troubleshooting

### Common Issues

1. **"Task not found"**
   - Ensure task ID matches format: `TASK-XXX`
   - Check manifesto.yaml is in `docs/_MANIFESTO/`

2. **"Verification failed"**
   - Run each check manually
   - Ensure all file paths are correct
   - Check command output for errors

3. **"Claude Code can't find manifesto"**
   - Provide full path in prompt
   - Include relevant section of manifesto in prompt

### Debug Mode

```bash
# Verbose output
MANIFESTO_DEBUG=1 manifesto verify TASK-001

# Check specific acceptance criteria
python -c "
import yaml
with open('docs/_MANIFESTO/manifesto.yaml') as f:
    m = yaml.safe_load(f)
    task = next(t for t in m['tasks'] if t['id'] == 'TASK-001')
    print(yaml.dump(task, default_flow_style=False))
"
```

## Next Steps

1. **Customize for Your Project**: Edit the manifesto template
2. **Define Your Tasks**: Break down your project into verifiable chunks
3. **Set Up CI/CD**: Use GitHub Actions to verify all contributions
4. **Scale Up**: Add more sophisticated verifiers and orchestration

## Resources

- [Manifesto Engine Repo](https://github.com/carmandale/manifesto-engine)
- [Example Manifestos](https://github.com/carmandale/manifesto-engine/tree/main/examples)
- [Custom Verifier Guide](https://github.com/carmandale/manifesto-engine/wiki/Custom-Verifiers)

---

Remember: **Every task must have proof. No exceptions.**