"""
reflection_assistant.py
Generates daily focus and weekly reflection summaries.
"""

from datetime import datetime, timedelta
from models.task_model import TaskModel
from models.plan_model import PlanModel
from models.pattern_model import PatternModel
from models.reflection_model import ReflectionModel
from core.ai_engines import AIEngines


class ReflectionAssistant:
    """Supports daily and weekly reflection features."""

    @staticmethod
    def generate_daily_focus():
        """Summarize top 3 tasks/goals from recent days."""
        tasks = TaskModel.get_all()[:3]
        focus_text = "\n".join([t["task"] for t in tasks])
        summary = AIEngines.summarize_text(focus_text)
        return f"🌞 Daily Focus:\n{summary}"

    @staticmethod
    def generate_weekly_reflection():
        """Create weekly report and save to DB."""
        completed = TaskModel.get_all()[:5]
        ongoing = PlanModel.get_all()[:3]
        issues = PatternModel.get_top(3)

        entries = [
            f"Completed tasks: {len(completed)}",
            f"Ongoing plans: {len(ongoing)}",
            f"Top issues: {', '.join([i['issue'] for i in issues])}"
        ]

        summary = AIEngines.generate_reflection_report(entries)
        ReflectionModel.create(
            week_start=datetime.now().date().isoformat(),
            completed_tasks=str(completed),
            ongoing_plans=str(ongoing),
            issues=str(issues),
            summary=summary
        )
        return summary