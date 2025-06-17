# TASK EXECUTION TEMPLATE

## TASK IDENTIFICATION
**Task ID:** {{ task_id }}  
**Title:** {{ task_title }}  
**Description:** {{ task_description }}

## VISION CONTEXT
**Project Vision:** {{ vision }}  
**North Star Metric:** {{ north_star }}  
**Task Vision Link:** {{ vision_link }}

## ACCEPTANCE CRITERIA
{{ acceptance_criteria }}

## WORKFLOW YOU MUST FOLLOW

### 1. PLAN PHASE (YOU ARE HERE)
Generate a numbered plan with concrete, actionable steps:
- Each step should be specific and verifiable
- Include file paths and exact commands
- Consider dependencies and order of operations
- Identify potential risks or blockers

**IMPORTANT:** After outputting your plan, STOP and wait for human approval.
Do not proceed until you receive "EXECUTE" command.

### 2. EXECUTION PHASE (AFTER APPROVAL ONLY)
Once approved:
- Execute EXACTLY as planned
- Document any deviations with reasons
- Capture output/proof for each step
- Stop immediately if blocked

### 3. SUMMARY PHASE (REQUIRED)
After execution, provide:
- **Actions Taken:** List what was actually done
- **Proof of Completion:** 
  - File paths created/modified
  - Command outputs
  - Test results
  - Screenshots if applicable
- **Vision Alignment:** How this task advanced the vision
- **Metrics Impact:** Effect on north star metric
- **Issues Encountered:** Any problems or deviations

### 4. WAIT FOR REVIEW
After summary, STOP and wait for supervisor review.
Do not proceed to other tasks.

---

## YOUR RESPONSE FORMAT

```
## PLAN for {{ task_id }}

1. [First concrete step]
   - Sub-step if needed
   - Expected outcome

2. [Second concrete step]
   - Details
   - Verification method

3. [Continue numbered steps...]

**Estimated Time:** X minutes
**Risks:** [Any identified risks]
**Dependencies:** [What must exist/work]

---
⏸️ **AWAITING APPROVAL** - I will proceed only after you type "EXECUTE"
```

BEGIN: Output your PLAN only.