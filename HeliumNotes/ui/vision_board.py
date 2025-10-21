"""
Vision Board widget

Contains:
- Goals list (QListWidget)
- Projects list (QListWidget)
- Metrics (total tasks, completed tasks)
- Simple API: load_from_db(db), refresh()
"""

from PyQt6.QtWidgets import (
    QWidget,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGroupBox,
    QFormLayout,
    QListWidgetItem,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from data.database import get_connection
import logging

logger = logging.getLogger(__name__)


class VisionBoardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout()

        # Goals box
        self.goals_list = QListWidget()
        goals_group = QGroupBox("Goals")
        gb_l = QVBoxLayout()
        gb_l.addWidget(self.goals_list)
        self.btn_add_goal = QPushButton("Add Goal from Selected Note")
        gb_l.addWidget(self.btn_add_goal)
        goals_group.setLayout(gb_l)

        # Projects box
        self.projects_list = QListWidget()
        proj_group = QGroupBox("Projects")
        pg_l = QVBoxLayout()
        pg_l.addWidget(self.projects_list)
        self.btn_add_project = QPushButton("Add Project from Selected Note")
        pg_l.addWidget(self.btn_add_project)
        proj_group.setLayout(pg_l)

        # Metrics
        metrics_group = QGroupBox("Key Metrics")
        mf = QFormLayout()
        self.label_total = QLabel("0")
        self.label_completed = QLabel("0")
        mf.addRow(QLabel("Total tasks:"), self.label_total)
        mf.addRow(QLabel("Completed:"), self.label_completed)
        metrics_group.setLayout(mf)

        layout.addWidget(goals_group, 2)
        layout.addWidget(proj_group, 2)
        layout.addWidget(metrics_group, 1)

        self.setLayout(layout)

        # Default handlers (can be overridden by MainWindow wiring)
        self.btn_add_goal.clicked.connect(self._add_goal_stub)
        self.btn_add_project.clicked.connect(self._add_project_stub)

    def load_from_db(self):
        """
        Load goals/projects and metrics from DB.
        We treat notes tagged with 'goal' and 'project' in tags field as items.
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, title, tags FROM notes")
            rows = cur.fetchall()
            self.goals_list.clear()
            self.projects_list.clear()
            for r in rows:
                tags = (r["tags"] or "").lower()
                item_text = r["title"] or f"Untitled — {r['id']}"
                if "goal" in [t.strip() for t in tags.split(",") if t.strip()]:
                    it = QListWidgetItem(item_text)
                    it.setData(Qt.ItemDataRole.UserRole, {"id": r["id"], "type": "goal"})
                    self.goals_list.addItem(it)
                if "project" in [t.strip() for t in tags.split(",") if t.strip()]:
                    it = QListWidgetItem(item_text)
                    it.setData(Qt.ItemDataRole.UserRole, {"id": r["id"], "type": "project"})
                    self.projects_list.addItem(it)
            # metrics
            cur.execute("SELECT COUNT(*) as total FROM tasks")
            total = cur.fetchone()["total"] or 0
            cur.execute("SELECT COUNT(*) as done FROM tasks WHERE status IN ('done','completed','closed')")
            done = cur.fetchone()["done"] or 0
            self.label_total.setText(str(total))
            self.label_completed.setText(str(done))
            conn.close()
        except Exception:
            logger.exception("Failed to load vision board data")

    def _add_goal_stub(self):
        QMessageBox.information(self, "Add Goal", "Use the main Notes list to tag a note with 'goal' and refresh.")

    def _add_project_stub(self):
        QMessageBox.information(self, "Add Project", "Use the main Notes list to tag a note with 'project' and refresh.")