

```markdown
EXECUTE the migration command implementation:

1. Add migrate-tasks command to src/manifesto/__main__.py:
   - @cli.command() with --dry-run option
   - Backs up to manifesto.yaml.backup-{timestamp}
   - Extracts tasks and writes to individual files
   - Updates manifesto.yaml without tasks section

2. Task file format (for tasks/TASK-XXX.yaml):
   ```yaml
   id: "TASK-001"
   title: "Refactor tasks to individual files"
   description: |
     Move from monolithic manifesto.yaml to:
     - manifesto.yaml (PRD + vision)
     - tasks/TASK-XXX.yaml (individual tasks)
     - epics/EPIC-XXX/README.md (epic vision)
   acceptance:
     migration_complete: "All existing tasks in separate files"
     backward_compatible: "Old format still loads"
   ```

3. Preserve YAML formatting:
   - Use yaml.dump with proper settings to maintain multi-line strings
   - Keep description formatting intact

4. Success criteria:
   - manifesto migrate-tasks --dry-run shows what will happen
   - manifesto migrate-tasks creates 3 task files
   - manifesto status still shows 3 tasks
   - manifesto verify TASK-001 works after migration

Show the implementation and run the migration.
```

## 🎯 Post-Migration Test Plan

After Claude Code completes:

```bash
# 1. Dry run first
manifesto migrate-tasks --dry-run

# 2. Actual migration
manifesto migrate-tasks

# 3. Verify results
ls -la docs/_MANIFESTO/tasks/TASK-*.yaml
cat docs/_MANIFESTO/tasks/TASK-001.yaml

# 4. Check manifesto.yaml no longer has tasks
grep -A 3 "tasks:" docs/_MANIFESTO/manifesto.yaml

# 5. Verify everything still works
manifesto status
manifesto verify TASK-001
```

This completes TASK-001! Ready to see the magic happen? 🎩✨