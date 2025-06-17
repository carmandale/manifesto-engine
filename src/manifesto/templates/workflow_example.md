# WORKFLOW EXAMPLE: Complete Task Execution

This example demonstrates the full PLAN→EXECUTE→SUMMARIZE→SUPERVISE workflow using a real task.

## Example Task: TASK-006 - Add Logging System

### Phase 1: Worker Receives Task

**Given Prompt:**
```markdown
# TASK EXECUTION TEMPLATE

## TASK IDENTIFICATION
**Task ID:** TASK-006
**Title:** Add comprehensive logging system
**Description:** Add logging to track task execution, errors, and performance metrics

## VISION CONTEXT
**Project Vision:** Creative at the speed of thought - from vision to verified execution
**North Star Metric:** Time from idea to verified implementation
**Task Vision Link:** Enables faster debugging and performance optimization, reducing time to identify and fix issues

## ACCEPTANCE CRITERIA
- file_exists: ["src/manifesto/core/logger.py"]
- test_passes: "test_logger"
- file_contains: {"src/manifesto/__main__.py": "import logger"}

BEGIN: Output your PLAN only.
```

### Phase 2: Worker Outputs Plan

**Worker Response:**
```markdown
## PLAN for TASK-006

1. Create logger module at src/manifesto/core/logger.py
   - Design logger with levels (DEBUG, INFO, WARNING, ERROR)
   - Include timestamp and task context
   - Support file and console output

2. Implement core logging functions
   - setup_logger() - Initialize with config
   - log_task_start() - Track task beginning
   - log_task_complete() - Track task success
   - log_error() - Capture failures
   - Expected outcome: Clean API for logging

3. Integrate logger into CLI commands
   - Import in __main__.py
   - Add logging to verify command
   - Add logging to add command
   - Add logging to check-alignment command

4. Create tests for logger
   - Test file: tests/test_logger.py
   - Test log levels
   - Test file output
   - Test context capture

5. Update existing modules
   - Add logging to task_parser.py
   - Add logging to task_loader.py
   - Verification: grep for logger imports

**Estimated Time:** 20 minutes
**Risks:** May need to handle concurrent writes if multiple tasks run
**Dependencies:** Python logging module (built-in)

---
⏸️ **AWAITING APPROVAL** - I will proceed only after you type "EXECUTE"
```

### Phase 3: Human Approves

**Human:** EXECUTE

### Phase 4: Worker Executes

**Worker Actions:**
```python
# Creates src/manifesto/core/logger.py
import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """Setup logger with file and console handlers."""
    # ... implementation ...

# Updates __main__.py
from .core import logger

# Creates tests/test_logger.py
def test_logger():
    # ... test implementation ...
```

### Phase 5: Worker Summarizes

**Worker Summary:**
```markdown
## EXECUTION SUMMARY for TASK-006

### Actions Taken:
1. ✅ Created src/manifesto/core/logger.py (87 lines)
   - Implemented setup_logger, log_task_start, log_task_complete, log_error
   - Added rotation support for log files
   
2. ✅ Updated src/manifesto/__main__.py
   - Added logger import
   - Integrated logging into verify, add, and check-alignment commands
   
3. ✅ Created tests/test_logger.py (45 lines)
   - Tests for all log levels
   - Tests for file output
   - Tests for context preservation

4. ✅ Updated 3 existing modules with logging
   - task_parser.py: Added operation logging
   - task_loader.py: Added file loading logs
   - validator.py: Added validation error logs

### Proof of Completion:
- File created: `src/manifesto/core/logger.py`
- Test passing: `pytest tests/test_logger.py` (3 tests, all passed)
- Import verified: `grep "import logger" src/manifesto/__main__.py` ✓
- Log output sample:
  ```
  2024-01-15 10:23:45 [INFO] Task TASK-006 started
  2024-01-15 10:24:12 [INFO] Created logger.py module
  2024-01-15 10:25:33 [INFO] Task TASK-006 completed
  ```

### Vision Alignment:
This logging system directly supports "speed of thought" by:
- Reducing debug time from minutes to seconds with clear logs
- Tracking performance metrics to identify bottlenecks
- Providing audit trail for task execution

### Metrics Impact:
- Expected 40% reduction in debugging time
- Performance bottlenecks now visible in logs
- Task execution history preserved

### Issues Encountered:
- Initially forgot to create logs directory - added auto-creation
- Had to handle Unicode in log messages - fixed with encoding='utf-8'

---
⏸️ **AWAITING SUPERVISOR REVIEW**
```

### Phase 6: Supervisor Reviews

**Supervisor Review:**
```markdown
## SUPERVISOR REVIEW: TASK-006

**VERDICT: APPROVED** ✅
- Core requirement met: Yes - comprehensive logging system implemented
- Proof verified: Yes - tests pass, imports confirmed
- Vision aligned: Yes - directly reduces debugging time
- Quality acceptable: Yes - follows Python logging best practices

**Feedback:**
Excellent implementation. The logging system is well-structured and provides
exactly the visibility needed for faster debugging. Good decision to add
automatic log directory creation.

**Commendations:**
- Thoughtful API design with task-specific methods
- Comprehensive test coverage
- Proactive handling of Unicode issues

**Next Steps:**
- Consider adding log aggregation in future task
- May want to add performance profiling decorator later

---
Signed: SUPERVISOR
Time: 2024-01-15 10:30:00
```

## Key Observations

1. **Clear Phases:** Each phase has a definite start and stop
2. **Human Control:** Execution only happens after explicit approval
3. **Verification:** Proof is provided for all claims
4. **Vision Focus:** Every phase references the vision
5. **Quality Loop:** Supervisor ensures standards are met

## Using This Workflow

1. Copy the appropriate template (worker or supervisor)
2. Fill in the template variables
3. Give to AI agent
4. Follow the phases strictly
5. Document everything

This workflow ensures quality, maintains vision alignment, and provides full accountability for all task execution.