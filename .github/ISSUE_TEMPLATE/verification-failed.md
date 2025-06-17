---
name: Verification Failed
about: Report when task verification fails
title: '[TASK-XXX] Verification Failed'
labels: 'verification-failed', 'bug'
assignees: ''
---

## Task Information
- **Task ID**: TASK-XXX
- **Expected Result**: PASS
- **Actual Result**: FAIL

## Verification Output
```
<!-- Paste the output of: manifesto verify TASK-XXX -->
```

## Failed Checks
<!-- Which specific checks failed? -->
- [ ] `file_exists`: <!-- file path -->
- [ ] `file_contains`: <!-- pattern not found -->
- [ ] `command_succeeds`: <!-- command and error -->
- [ ] `test_passes`: <!-- test name and output -->
- [ ] `performance_metric`: <!-- metric and value -->

## Investigation
<!-- What might be causing the failure? -->

## Proposed Fix
<!-- How should this be resolved? -->
