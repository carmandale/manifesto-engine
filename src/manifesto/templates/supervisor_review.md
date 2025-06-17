# SUPERVISOR REVIEW TEMPLATE

## TASK UNDER REVIEW
**Task ID:** {{ task_id }}  
**Title:** {{ task_title }}  
**Worker:** {{ worker_name }}  
**Timestamp:** {{ completion_time }}

## ORIGINAL REQUEST
{{ task_description }}

## WORKER'S EXECUTION SUMMARY
{{ worker_summary }}

## REVIEW CHECKLIST

### 1. Core Requirements
- [ ] All acceptance criteria met?
- [ ] Task description requirements fulfilled?
- [ ] No missing functionality?

### 2. Proof Verification
- [ ] Adequate proof provided?
- [ ] Outputs/files verifiable?
- [ ] Tests passing (if applicable)?
- [ ] Commands executed successfully?

### 3. Vision Alignment
- [ ] Work supports stated vision link?
- [ ] No mission drift detected?
- [ ] Advances north star metric?

### 4. Quality & Safety
- [ ] Code follows project conventions?
- [ ] No harmful side effects?
- [ ] Security best practices followed?
- [ ] No unnecessary complexity added?

### 5. Process Compliance
- [ ] Followed PLAN→EXECUTE workflow?
- [ ] Documented deviations properly?
- [ ] Summary comprehensive?

## SUPERVISOR VERDICT

**VERDICT:** [APPROVED / NEEDS_REVISION / REJECTED]

### Specific Feedback
{{ feedback }}

### Required Revisions (if NEEDS_REVISION)
1. {{ revision_1 }}
2. {{ revision_2 }}
3. {{ revision_3 }}

### Drift Warnings (if any)
{{ drift_warnings }}

### Commendations (if any)
{{ commendations }}

## NEXT STEPS
{{ next_steps }}

---

## RESPONSE FORMAT FOR SUPERVISOR

```
## SUPERVISOR REVIEW: {{ task_id }}

**VERDICT: APPROVED** ✅
- Core requirement met: Yes
- Proof verified: Yes
- Vision aligned: Yes
- Quality acceptable: Yes

**Feedback:**
[Specific observations about the work]

**Commendations:**
- [What was done particularly well]

**Next Steps:**
- [What should happen next]

---
Signed: SUPERVISOR
Time: [timestamp]
```

OR

```
## SUPERVISOR REVIEW: {{ task_id }}

**VERDICT: NEEDS_REVISION** ⚠️

**Issues Found:**
1. [Specific issue]
2. [Another issue]

**Required Revisions:**
1. [Exact change needed]
2. [Another required change]

**Resubmit with:**
- [What to include in revision]

---
Signed: SUPERVISOR
Time: [timestamp]
```

OR

```
## SUPERVISOR REVIEW: {{ task_id }}

**VERDICT: REJECTED** ❌

**Reason for Rejection:**
[Clear explanation of why task cannot proceed]

**Mission Drift Detected:**
[How this deviates from vision]

**Recommendation:**
[What should be done instead]

---
Signed: SUPERVISOR
Time: [timestamp]
```