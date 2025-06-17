# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**manifesto-engine** is a zero-ambiguity project orchestration system designed for AI agents. It creates cryptographic proofs of task completion with binary success criteria.

**Core Philosophy**: Radical clarity - every task must have measurable acceptance criteria with no room for interpretation.

## Critical Workflow Pattern: PLAN → EXECUTE

**ALWAYS follow this two-phase approach:**
1. Generate a PLAN first
2. Wait for human approval (user types "EXECUTE")
3. Only then proceed with implementation

Never skip the planning phase or execute without approval.

## Development Commands

```bash
# Environment setup
./activate.sh                            # Activate virtual environment
uv pip install -r requirements.txt       # Install dependencies
pip install -e .                         # Editable install for development

# Testing
pytest tests/ -v                         # Run all tests
pytest tests/test_manifesto.py -v        # Run specific test

# CLI usage
manifesto init --type visionos --name "Project Name"   # Initialize project
manifesto plan --manifest docs/_MANIFESTO/manifesto.yaml    # Generate plan
manifesto execute --manifest docs/_MANIFESTO/manifesto.yaml  # Execute after approval
manifesto verify TASK-XXX --manifest docs/_MANIFESTO/manifesto.yaml  # Verify task
manifesto status                         # Check project status
```

## Architecture Overview

The system enforces extreme discipline through:
- **Binary Success**: Tasks either completely pass or fail - no partial success
- **8-Task Maximum**: Manifestos limited to 8 focused tasks
- **Cryptographic Proof**: Every completed task generates verifiable proof
- **Dependency Management**: Tasks can depend on other tasks

### Key Components

1. **Core Module** (`src/manifesto/core/`)
   - `injector.py`: Project initialization and manifesto injection
   - `validator.py`: Manifesto schema validation

2. **Orchestration** (`src/manifesto/orchestrate/`)
   - `planner.py`: Generates execution plans respecting dependencies

3. **Verification** (`src/manifesto/verify/`)
   - `base.py`: Base verifier class for extensibility
   - `swift.py`: Swift-specific task verification

4. **Templates** (`src/manifesto/templates/`)
   - Jinja2 templates for different project types

## Working with Manifestos

Manifestos live in `docs/_MANIFESTO/manifesto.yaml` and define:
- Project metadata
- Tasks with IDs (TASK-001, TASK-002, etc.)
- Acceptance criteria for each task
- Task dependencies

### Acceptance Criteria Types
- `file_exists`: Verify file presence
- `file_contains`: Check file content patterns
- `command_succeeds`: Ensure commands run successfully
- `performance_metric`: Numeric performance targets
- `test_passes`: Test specifications

## Task Verification Workflow

When completing a task:
1. Read the manifesto to understand requirements
2. Implement ALL acceptance criteria
3. Run `manifesto verify TASK-XXX`
4. Include verification output in your response
5. Stop if verification fails

## Agent Guidelines

- **Focus**: Work only on the assigned task
- **Verification**: Always run and show verification output
- **Dependencies**: Respect task dependencies
- **Atomic Tasks**: Each task should be < 1 day of work
- **Clear Criteria**: Use measurable, numeric acceptance tests

## Project Structure

```
docs/_MANIFESTO/
├── manifesto.yaml    # Project contract
├── tasks/           # Completion proofs (JSON)
├── reviews/         # Code review results
└── plan.json        # Generated execution plan
```

## Common Patterns

- Use `manifesto verify` after completing any task
- Check `manifesto status` to see project progress
- Read existing verifiers in `src/manifesto/verify/` before creating new ones
- Follow the PLAN → EXECUTE pattern for all major changes