
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


# ---------------------------------------------------------------
# The 5 criteria used to judge a debate
# ---------------------------------------------------------------
CRITERIA = [
    "Content / Arguments",
    "Confidence",
    "Communication Skills",
    "Rebuttal",
    "Time Management"
]

MAX_MARK_PER_CRITERION = 10  # each criterion is scored out of 10


# ---------------------------------------------------------------
# GAME TREE NODE
# A very small building block that represents one "round" (one
# criterion) of the debate game tree.
# ---------------------------------------------------------------
class GameTreeNode:
    def __init__(self, criterion_name, score_a, score_b):
        self.criterion_name = criterion_name
        self.score_a = score_a
        self.score_b = score_b

    def evaluate(self):
        """
        This is the core Game Tree (Minimax-style) step.
        For this round/node, we look at BOTH possible branches:
            branch_a = value if Team A is the maximizer
            branch_b = value if Team B is the maximizer
        We choose the branch with the MAXIMUM value - the same
        principle used in a Minimax game tree search - to decide
        which team "wins" this particular round/node.
        Returns: "A", "B", or "Tie"
        """
        branch_a = self.score_a   # value of choosing Team A at this node
        branch_b = self.score_b   # value of choosing Team B at this node

        best_branch_value = max(branch_a, branch_b)  # MAX step of the tree

        if branch_a == branch_b:
            return "Tie"
        elif best_branch_value == branch_a:
            return "A"
        else:
            return "B"


# ---------------------------------------------------------------
# GAME TREE SCORING ENGINE
# Builds one node per criterion and walks through the whole tree
# to work out how many rounds each team won.
# ---------------------------------------------------------------
class GameTreeScorer:
    def __init__(self, scores_a, scores_b):
        self.nodes = []
        for i, criterion in enumerate(CRITERIA):
            node = GameTreeNode(criterion, scores_a[i], scores_b[i])
            self.nodes.append(node)

    def run(self):
        rounds_won_a = 0
        rounds_won_b = 0
        round_results = []  # store per-criterion result for display

        for node in self.nodes:
            result = node.evaluate()
            round_results.append((node.criterion_name, result))
            if result == "A":
                rounds_won_a += 1
            elif result == "B":
                rounds_won_b += 1

        return rounds_won_a, rounds_won_b, round_results


# ---------------------------------------------------------------
# MAIN APPLICATION WINDOW
# ---------------------------------------------------------------
class DebateJudgeHelper(QWidget):
    def __init__(self):
        super().__init__()
        self.entries_a = []
        self.entries_b = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Debate Judge Helper - Game Tree Scoring")
        self.setMinimumWidth(640)

        main_layout = QVBoxLayout()

        # ---------- Title ----------
        title = QLabel("🏆 Debate Judge Helper")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        subtitle = QLabel("Score speeches objectively using Game Tree Scoring")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        main_layout.addWidget(subtitle)

        # ---------- Score entry section ----------
        scores_layout = QHBoxLayout()
        scores_layout.addWidget(self.build_team_box("Team A", self.entries_a))
        scores_layout.addWidget(self.build_team_box("Team B", self.entries_b))
        main_layout.addLayout(scores_layout)

        # ---------- Evaluate button ----------
        self.evaluate_btn = QPushButton("Evaluate Debate")
        self.evaluate_btn.setStyleSheet(
            "background-color: #2E86AB; color: white; padding: 10px; "
            "font-size: 14px; font-weight: bold; border-radius: 6px;"
        )
        self.evaluate_btn.clicked.connect(self.evaluate_debate)
        main_layout.addWidget(self.evaluate_btn)

        # ---------- Separator ----------
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line)

        # ---------- Result section ----------
        self.result_label = QLabel("Enter scores above and click 'Evaluate Debate'.")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        result_font = QFont()
        result_font.setPointSize(13)
        self.result_label.setFont(result_font)
        main_layout.addWidget(self.result_label)

        self.breakdown_label = QLabel("")
        self.breakdown_label.setAlignment(Qt.AlignLeft)
        self.breakdown_label.setWordWrap(True)
        self.breakdown_label.setStyleSheet("color: #444;")
        main_layout.addWidget(self.breakdown_label)

        self.setLayout(main_layout)

    def build_team_box(self, team_name, entry_list):
        """Creates a boxed group of input fields for one team."""
        box = QGroupBox(team_name)
        grid = QGridLayout()

        for row, criterion in enumerate(CRITERIA):
            label = QLabel(f"{criterion} (0-{MAX_MARK_PER_CRITERION}):")
            field = QLineEdit()
            field.setPlaceholderText("0-10")
            grid.addWidget(label, row, 0)
            grid.addWidget(field, row, 1)
            entry_list.append(field)

        box.setLayout(grid)
        return box

    def read_scores(self, entry_list, team_label):
        """Reads and validates the 5 scores entered for a team."""
        scores = []
        for field, criterion in zip(entry_list, CRITERIA):
            text = field.text().strip()
            if text == "":
                raise ValueError(f"{team_label}: please enter a score for '{criterion}'.")
            try:
                value = float(text)
            except ValueError:
                raise ValueError(f"{team_label}: '{criterion}' must be a number.")
            if value < 0 or value > MAX_MARK_PER_CRITERION:
                raise ValueError(
                    f"{team_label}: '{criterion}' must be between 0 and {MAX_MARK_PER_CRITERION}."
                )
            scores.append(value)
        return scores

    def evaluate_debate(self):
        # ---- Step 1: Validate and read input ----
        try:
            scores_a = self.read_scores(self.entries_a, "Team A")
            scores_b = self.read_scores(self.entries_b, "Team B")
        except ValueError as err:
            QMessageBox.warning(self, "Invalid Input", str(err))
            return

        # ---- Step 2: Calculate totals ----
        total_a = sum(scores_a)
        total_b = sum(scores_b)

        # ---- Step 3: Run the Game Tree Scoring algorithm ----
        scorer = GameTreeScorer(scores_a, scores_b)
        rounds_won_a, rounds_won_b, round_results = scorer.run()

        # ---- Step 4: Decide the final winner ----
        # Priority 1: whoever won more rounds in the game tree.
        # Priority 2 (tie-breaker): whoever has the higher total score.
        if rounds_won_a > rounds_won_b:
            winner = "Team A"
        elif rounds_won_b > rounds_won_a:
            winner = "Team B"
        else:
            if total_a > total_b:
                winner = "Team A"
            elif total_b > total_a:
                winner = "Team B"
            else:
                winner = "It's a Tie"

        # ---- Step 5: Display the result clearly ----
        if winner == "It's a Tie":
            result_text = (
                f"🤝 Result: It's a Tie!\n"
                f"Final Score: Team A = {total_a:.1f} | Team B = {total_b:.1f}"
            )
        else:
            result_text = (
                f"🏆 Winner: {winner}\n"
                f"Final Score: Team A = {total_a:.1f} | Team B = {total_b:.1f}"
            )
        self.result_label.setText(result_text)

        breakdown_lines = [f"Game Tree round-by-round result "
                            f"(Team A won {rounds_won_a} round(s), "
                            f"Team B won {rounds_won_b} round(s)):"]
        for criterion, result in round_results:
            if result == "A":
                breakdown_lines.append(f"  • {criterion}: Team A wins this round")
            elif result == "B":
                breakdown_lines.append(f"  • {criterion}: Team B wins this round")
            else:
                breakdown_lines.append(f"  • {criterion}: Tie")
        self.breakdown_label.setText("\n".join(breakdown_lines))


def main():
    app = QApplication(sys.argv)
    window = DebateJudgeHelper()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
