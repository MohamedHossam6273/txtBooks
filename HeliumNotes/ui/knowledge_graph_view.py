"""
Knowledge Graph widget

- Builds a NetworkX graph from notes/plans/tasks/patterns and relations.
- Lays out graph using spring_layout and renders with pyqtgraph.
- Clicking nodes will emit a signal (or you can call back into MainWindow).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
import pyqtgraph as pg
import networkx as nx
from data.database import get_connection
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphWidget(QWidget):
    # signal emitted when user clicks on a node: (entity_type, entity_id)
    node_clicked = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.btn_refresh = QPushButton("Refresh Graph")
        layout.addWidget(self.btn_refresh)

        self.view = pg.GraphicsLayoutWidget()
        self.plot = self.view.addPlot()
        self.plot.hideAxis("bottom")
        self.plot.hideAxis("left")
        self.plot.setAspectLocked(True)

        layout.addWidget(self.view)
        self.setLayout(layout)

        self.btn_refresh.clicked.connect(self.refresh)

    def refresh(self):
        """
        Recreate the graph from DB and draw it.
        This is synchronous and intended for small graphs (suitable for prototype).
        """
        try:
            conn = get_connection()
            cur = conn.cursor()

            G = nx.Graph()

            # Notes
            cur.execute("SELECT id, title FROM notes")
            for r in cur.fetchall():
                key = f"note:{r['id']}"
                G.add_node(key, label=r["title"] or f"Note {r['id']}", type="note", ref_id=r["id"])

            # Tasks
            cur.execute("SELECT id, task, note_id FROM tasks")
            for r in cur.fetchall():
                key = f"task:{r['id']}"
                G.add_node(key, label=(r["task"] or "")[:40], type="task", ref_id=r["id"])
                # link task -> note
                if r["note_id"]:
                    G.add_edge(key, f"note:{r['note_id']}")

            # Plans
            cur.execute("SELECT id, objectives, note_id FROM plans")
            for r in cur.fetchall():
                key = f"plan:{r['id']}"
                label = (r["objectives"] or "")[:40] if r["objectives"] else f"Plan {r['id']}"
                G.add_node(key, label=label, type="plan", ref_id=r["id"])
                if r["note_id"]:
                    G.add_edge(key, f"note:{r['note_id']}")

            # Patterns
            cur.execute("SELECT id, pattern_text FROM patterns")
            for r in cur.fetchall():
                key = f"pattern:{r['id']}"
                G.add_node(key, label=(r["pattern_text"] or "")[:40], type="pattern", ref_id=r["id"])

            # Relations
            cur.execute("SELECT * FROM relations")
            for r in cur.fetchall():
                a = f"{r['from_type']}:{r['from_id']}"
                b = f"{r['to_type']}:{r['to_id']}"
                if not G.has_node(a):
                    G.add_node(a, label=a, type=r["from_type"], ref_id=r["from_id"])
                if not G.has_node(b):
                    G.add_node(b, label=b, type=r["to_type"], ref_id=r["to_id"])
                G.add_edge(a, b)

            conn.close()

            # Clear previous plot
            self.plot.clear()

            if G.number_of_nodes() == 0:
                self.plot.addItem(pg.TextItem("No graph data. Add notes/tasks/plans to create nodes.", anchor=(0.5, 0.5)))
                return

            pos = nx.spring_layout(G, seed=42, k=1.2 / max(1, G.number_of_nodes()))

            node_list = list(G.nodes())
            xs = [pos[n][0] for n in node_list]
            ys = [pos[n][1] for n in node_list]

            brushes = []
            sizes = []
            labels = []
            for n in node_list:
                typ = G.nodes[n].get("type", "note")
                color_map = {
                    "note": (100, 149, 237),
                    "task": (60, 179, 113),
                    "plan": (255, 165, 0),
                    "pattern": (220, 20, 60),
                    "client": (147, 112, 219),
                    "issue": (255, 69, 0),
                }
                c = color_map.get(typ, (180, 180, 180))
                brushes.append(pg.mkBrush(c[0], c[1], c[2], 200))
                sizes.append(18 if typ == "note" else 12)
                labels.append(G.nodes[n].get("label", n))

            # draw edges
            for e in G.edges():
                a, b = e
                x0, y0 = pos[a]
                x1, y1 = pos[b]
                line = pg.PlotDataItem([x0, x1], [y0, y1], pen=pg.mkPen((180, 180, 180), width=1))
                self.plot.addItem(line)

            scatter = pg.ScatterPlotItem(x=xs, y=ys, size=sizes, brush=brushes, pen=pg.mkPen("w"))
            # attach click handler to scatter; map clicked point back to node_list
            def on_clicked(plot_item, points):
                if not points:
                    return
                p = points[0]
                # find closest index by coordinates
                px = p.pos().x(); py = p.pos().y()
                idx = None
                tol = 1e-6
                for i, (xx, yy) in enumerate(zip(xs, ys)):
                    if abs(xx - px) < 1e-6 and abs(yy - py) < 1e-6:
                        idx = i
                        break
                if idx is None:
                    # fallback: ignore
                    return
                node_key = node_list[idx]
                # parse node_key format 'type:id'
                if ":" in node_key:
                    typ, sid = node_key.split(":", 1)
                    try:
                        sid = int(sid)
                    except Exception:
                        sid = None
                    if sid is not None:
                        # emit a signal so the parent can react and open the note/task/plan
                        self.node_clicked.emit(typ, sid)

            scatter.sigClicked.connect(on_clicked)
            self.plot.addItem(scatter)

            # labels
            for i, lbl in enumerate(labels):
                ti = pg.TextItem(lbl, anchor=(0.5, -1.0))
                ti.setPos(xs[i], ys[i])
                self.plot.addItem(ti)

        except Exception:
            logger.exception("Failed to render knowledge graph")