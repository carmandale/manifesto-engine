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
