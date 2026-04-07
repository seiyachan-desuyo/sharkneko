import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QKeyEvent

class SudokuBoard(QWidget):
    win_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cell_size = 46
        self.margin = 20
        self.board_size = 9
        self.setFixedSize(self.board_size * self.cell_size + self.margin * 2, 
                          self.board_size * self.cell_size + self.margin * 2)
        # To receive key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.solution = []
        self.grid = []      # Current state
        self.locked = []    # Given numbers
        self.selected = None
        self.game_over = True

    def generate_puzzle(self):
        # Generate valid full grid
        def pattern(r, c): return (3 * (r % 3) + r // 3 + c) % 9
        def shuffle(s): return random.sample(list(s), len(s))
        
        rBase = range(3)
        rows  = [g * 3 + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols  = [g * 3 + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums  = shuffle(range(1, 10))
        
        self.solution = [[nums[pattern(r, c)] for c in cols] for r in rows]
        self.grid = [[self.solution[r][c] for c in range(9)] for r in range(9)]
        self.locked = [[True] * 9 for _ in range(9)]
        
        # Remove numbers to create puzzle (45 empty spaces is a moderate difficulty)
        squares = self.board_size * self.board_size
        empties = 45 
        for p in random.sample(range(squares), empties):
            self.grid[p // 9][p % 9] = 0
            self.locked[p // 9][p % 9] = False
            
        self.selected = None
        self.game_over = False
        self.update()

    def mousePressEvent(self, event):
        if self.game_over: return
        x = event.position().x() - self.margin
        y = event.position().y() - self.margin
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            self.selected = (row, col)
            self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if self.game_over or not self.selected: return
        r, c = self.selected
        if self.locked[r][c]: return
        
        if Qt.Key.Key_1 <= event.key() <= Qt.Key.Key_9:
            self.grid[r][c] = event.key() - Qt.Key.Key_0
        elif event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_0):
            self.grid[r][c] = 0
            
        self.update()
        self.check_win()

    def check_win(self):
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.grid[r][c] != self.solution[r][c]:
                    return
        self.game_over = True
        self.win_signal.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Background
        board_rect = QRectF(0.0, 0.0, float(self.width()), float(self.height()))
        painter.setBrush(QBrush(QColor("#f0f8ff")))
        painter.setPen(QPen(QColor("#93c5fd"), 3))
        painter.drawRoundedRect(board_rect, 10.0, 10.0)
        
        # Draw Cells
        font = QFont("PingFang SC", 20, QFont.Weight.Bold)
        painter.setFont(font)
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                cx = self.margin + c * self.cell_size
                cy = self.margin + r * self.cell_size
                rect = QRectF(cx, cy, self.cell_size, self.cell_size)
                
                if self.selected == (r, c) and not self.game_over:
                    painter.setBrush(QBrush(QColor("#bfdbfe")))
                else:
                    painter.setBrush(QBrush(QColor("#ffffff")))
                    
                painter.setPen(QPen(QColor("#dbeafe"), 1))
                painter.drawRect(rect)
                
                val = self.grid[r][c]
                if val != 0:
                    if self.locked[r][c]:
                        painter.setPen(QColor("#1e3a8a")) # Dark blue for given numbers
                    else:
                        # Color for user input numbers
                        # Red if wrong, Light Blue if correct?
                        # For pure Sudoku, usually we don't instantly show wrong/right, just blue
                        painter.setPen(QColor("#3b82f6")) 
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(val))
                    
        # Draw bold grid lines
        for i in range(self.board_size + 1):
            thickness = 3 if i % 3 == 0 else 1
            painter.setPen(QPen(QColor("#3b82f6" if thickness == 3 else "#93c5fd"), thickness))
            # Horizontal
            y = self.margin + i * self.cell_size
            painter.drawLine(self.margin, y, self.margin + self.board_size * self.cell_size, y)
            # Vertical
            x = self.margin + i * self.cell_size
            painter.drawLine(x, self.margin, x, self.margin + self.board_size * self.cell_size)

class SudokuWindow(QWidget):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.init_ui()
        
    def init_ui(self):
        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle("猫猫鲨数独挑战")
        self.setStyleSheet(
            "QWidget { background-color: #f0f8ff; color: #1e3a8a; font-family: 'PingFang SC', 'Microsoft YaHei'; }"
            "QLabel { color: #1e3a8a; }"
            "QPushButton { background-color: #dbeafe; border: 2px solid #93c5fd; border-radius: 8px; padding: 8px 16px; font-size: 14px; font-weight: bold; color: #1e3a8a; }"
            "QPushButton:hover { background-color: #bfdbfe; border-color: #60a5fa; }"
            "QPushButton:pressed { background-color: #93c5fd; }"
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("猫猫鲨数独挑战 🔢")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2563eb;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.status_label = QLabel("门票: 30 金币 | 奖金: 150 金币")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.board = SudokuBoard(self)
        self.board.win_signal.connect(self.on_win)
        layout.addWidget(self.board, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.tip_label = QLabel("需要花门票开局哦。点击空格，使用键盘输入 1-9。按 0 清除。")
        self.tip_label.setStyleSheet("font-size: 13px; color: #3b82f6;")
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tip_label)
        
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始新一局 (-30金币)")
        self.start_btn.clicked.connect(self.try_start)
        btn_layout.addStretch()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.adjustSize()
        
    def try_start(self):
        if self.pet.coins < 30:
            QMessageBox.warning(self, "金币不足", "你的金币不够支付30金币的门票哦，快去打工吧！")
            return
        self.pet.coins -= 30
        self.pet.save_data()
        if self.pet.chat_window: self.pet.chat_window.update_aff_ui()
        
        self.board.generate_puzzle()
        self.tip_label.setText("游戏开始！加油填满所有格子！全填对自动发奖。")
        self.tip_label.setStyleSheet("font-size: 13px; color: #3b82f6;")
        self.board.setFocus()
        
    def start_new_game(self):
        self.try_start()
        
    def on_win(self):
        self.pet.coins += 150
        self.pet.save_data()
        if self.pet.chat_window: self.pet.chat_window.update_aff_ui()
        self.tip_label.setText("🎉 挑战成功！奖金 150 金币已到账！太聪明啦！")
        self.tip_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #16a34a;")
