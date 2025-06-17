import yaml
from pathlib import Path
from typing import Dict, Any, List
from ..core.task_loader import load_tasks

class ManifestoPlanner:
    """Generate, validate, and execute a project PLAN.
    This first iteration focuses on enforcing plan constraints and
    ensuring the human-in-the-loop checkpoint before execution.
    """

    MAX_TASKS = 8
    MAX_DESC_WORDS = 12

    # ---------------------------------------------------------------------
    # PLAN STAGE
    # ---------------------------------------------------------------------
    def generate_plan(self, manifest_path: str | Path) -> Dict[str, Any]:
        """Read the manifesto.yaml and return a PLAN dict containing tasks."""
        path = Path(manifest_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Manifesto not found at {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        # Load tasks from directory or manifest
        manifest_dir = str(path.parent)
        tasks = load_tasks(manifest_dir)
        plan = {
            "prd_id": data.get("prd_id"),
            "title": data.get("title"),
            "tasks": [
                {
                    "id": t["id"],
                    "description": t["description"],
                    "depends_on": t.get("depends_on", []),
                    "owner_role": t.get("owner_role"),
                    "acceptance": t.get("acceptance", {}),
                }
                for t in tasks
            ],
        }
        return plan

    # ------------------------------------------------------------------
    # VALIDATION RULES (Radical Clarity)
    # ------------------------------------------------------------------
    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Return True if plan meets radical constraints, else False."""
        tasks: List[Dict[str, Any]] = plan.get("tasks", [])

        # 1. Hard cap on number of tasks
        if len(tasks) > self.MAX_TASKS:
            print(f"Plan invalid: contains {len(tasks)} tasks (max {self.MAX_TASKS}).")
            return False

        # 2. Each description ≤ MAX_DESC_WORDS words
        for t in tasks:
            words = t["description"].strip().split()
            if len(words) > self.MAX_DESC_WORDS:
                print(
                    f"Plan invalid: task {t['id']} description has {len(words)} words (> {self.MAX_DESC_WORDS})."
                )
                return False

        # TODO: Additional binary-success checks can go here
        return True

    # ------------------------------------------------------------------
    # EXECUTE STAGE (Stub)
    # ------------------------------------------------------------------
    def execute_plan(self, plan: Dict[str, Any]) -> bool:
        """Simple executor stub – iterates tasks sequentially.
        Real implementation will invoke agent workers.
        Returns True if all tasks reported success.
        """
        print("⚡ EXECUTION BEGIN – STOPS ON FIRST FAILURE ⚡")
        for task in plan.get("tasks", []):
            task_id = task["id"]
            desc = task["description"]
            print(f"→ {task_id}: {desc} … [SKIPPED – stub executor]")
            # In a future version, actual task execution happens here.
            # For now we assume success.
        print("✅ All tasks reported success (stub mode).")
        return True 