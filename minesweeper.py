import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

class MinesweeperBoard(QWidget):
    cell_clicked = pyqtSignal(int, int, str) # row, col, action('reveal' or 'flag')

    def __init__(self, rows=10, cols=10, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.cell_size = 32
        self.margin = 15
        self.setFixedSize(self.cols * self.cell_size + self.margin * 2, 
                          self.rows * self.cell_size + self.margin * 2)
        self.setMouseTracking(True)
        self.hover_cell = None
        
        self.mines = [[False]*cols for _ in range(rows)]
        self.revealed = [[False]*cols for _ in range(rows)]
        self.flagged = [[False]*cols for _ in range(rows)]
        self.neighbors = [[0]*cols for _ in range(rows)]
        self.game_over = False

    def mouseMoveEvent(self, event):
        x = event.position().x() - self.margin
        y = event.position().y() - self.margin
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if not self.revealed[row][col]:
                self.hover_cell = (row, col)
            else:
                self.hover_cell = None
        else:
            self.hover_cell = None
        self.update()

    def leaveEvent(self, event):
        self.hover_cell = None
        self.update()

    def mousePressEvent(self, event):
        if self.game_over: return
        x = event.position().x() - self.margin
        y = event.position().y() - self.margin
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if event.button() == Qt.MouseButton.LeftButton:
                self.cell_clicked.emit(row, col, 'reveal')
            elif event.button() == Qt.MouseButton.RightButton:
                self.cell_clicked.emit(row, col, 'flag')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Draw background
        board_rect = QRectF(0.0, 0.0, float(self.width()), float(self.height()))
        painter.setBrush(QBrush(QColor("#f0f8ff")))
        painter.setPen(QPen(QColor("#93c5fd"), 3))
        painter.drawRoundedRect(board_rect, 10.0, 10.0)
        
        font = QFont("PingFang SC", 14, QFont.Weight.Bold)
        painter.setFont(font)
        
        colors = ["", "#2563eb", "#16a34a", "#dc2626", "#9333ea", "#ea580c", "#0d9488", "#475569", "#000000"]

        for r in range(self.rows):
            for c in range(self.cols):
                cx = self.margin + c * self.cell_size
                cy = self.margin + r * self.cell_size
                rect = QRectF(cx, cy, self.cell_size, self.cell_size)
                
                if self.revealed[r][c]:
                    if self.mines[r][c]:
                        painter.setBrush(QBrush(QColor("#fca5a5"))) # Red background for mine
                        painter.setPen(QPen(QColor("#ef4444"), 1))
                        painter.drawRect(rect)
                        painter.setPen(QColor("#000000"))
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "💣")
                    else:
                        painter.setBrush(QBrush(QColor("#ffffff")))
                        painter.setPen(QPen(QColor("#bfdbfe"), 1))
                        painter.drawRect(rect)
                        num = self.neighbors[r][c]
                        if num > 0:
                            painter.setPen(QColor(colors[num]))
                            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(num))
                else:
                    # Unrevealed
                    if self.hover_cell == (r, c) and not self.game_over:
                        painter.setBrush(QBrush(QColor("#bfdbfe")))
                    else:
                        painter.setBrush(QBrush(QColor("#dbeafe")))
                    painter.setPen(QPen(QColor("#93c5fd"), 1))
                    painter.drawRect(rect)
                    
                    if self.flagged[r][c]:
                        painter.setPen(QColor("#dc2626"))
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "🚩")
                    elif self.game_over and self.mines[r][c]:
                        # Show unflagged mines at game over
                        painter.setPen(QColor("#000000"))
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "💣")

class MinesweeperWindow(QWidget):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.rows = 10
        self.cols = 10
        self.num_mines = 15
        
        self.first_click = True
        self.flags_placed = 0
        
        self.init_ui()
        self.start_new_game()

    def init_ui(self):
        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle("猫猫鲨扫雷大作战")
        self.setStyleSheet(
            "QWidget { background-color: #f0f8ff; color: #1e3a8a; font-family: 'PingFang SC', 'Microsoft YaHei'; }"
            "QLabel { color: #1e3a8a; }"
            "QPushButton { background-color: #dbeafe; border: 2px solid #93c5fd; border-radius: 8px; padding: 6px 12px; font-size: 13px; font-weight: bold; color: #1e3a8a; }"
            "QPushButton:hover { background-color: #bfdbfe; border-color: #60a5fa; }"
            "QPushButton:pressed { background-color: #93c5fd; }"
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("猫猫鲨扫雷大作战 💣")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563eb;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        self.status_label = QLabel("门票: 20 金币 | 奖金: 100 金币")
        self.status_label.setStyleSheet("font-weight: bold;")
        self.mine_label = QLabel(f"剩余地雷: {self.num_mines}")
        self.mine_label.setStyleSheet("font-weight: bold; color: #dc2626;")
        
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
        info_layout.addWidget(self.mine_label)
        layout.addLayout(info_layout)
        
        self.board = MinesweeperBoard(self.rows, self.cols, self)
        self.board.cell_clicked.connect(self.on_cell_clicked)
        layout.addWidget(self.board, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        btn_layout = QHBoxLayout()
        self.restart_btn = QPushButton("重新开始 (-20金币)")
        self.restart_btn.clicked.connect(self.try_start_game)
        btn_layout.addStretch()
        btn_layout.addWidget(self.restart_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.result_label = QLabel("左键翻开，右键插旗！第一步绝对安全哦~")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 13px; color: #3b82f6;")
        layout.addWidget(self.result_label)
        
        self.adjustSize()

    def try_start_game(self):
        if self.pet.coins < 20:
            QMessageBox.warning(self, "金币不足", "你的金币不够支付20金币的门票哦，快去打工吧！")
            return
        self.pet.coins -= 20
        self.pet.save_data()
        if self.pet.chat_window: self.pet.chat_window.update_aff_ui()
        self.start_new_game()

    def start_new_game(self):
        self.first_click = True
        self.flags_placed = 0
        self.mine_label.setText(f"剩余地雷: {self.num_mines}")
        self.result_label.setText("游戏开始！加油哦！")
        self.result_label.setStyleSheet("font-size: 13px; color: #3b82f6;")
        
        self.board.mines = [[False]*self.cols for _ in range(self.rows)]
        self.board.revealed = [[False]*self.cols for _ in range(self.rows)]
        self.board.flagged = [[False]*self.cols for _ in range(self.rows)]
        self.board.neighbors = [[0]*self.cols for _ in range(self.rows)]
        self.board.game_over = False
        self.board.update()

    def place_mines(self, first_r, first_c):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) != (first_r, first_c)]
        mines_pos = random.sample(positions, self.num_mines)
        for r, c in mines_pos:
            self.board.mines[r][c] = True
            
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board.mines[r][c]: continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board.mines[nr][nc]:
                            count += 1
                self.board.neighbors[r][c] = count

    def on_cell_clicked(self, r, c, action):
        if self.board.game_over: return
        
        if action == 'flag':
            if not self.board.revealed[r][c]:
                self.board.flagged[r][c] = not self.board.flagged[r][c]
                self.flags_placed += 1 if self.board.flagged[r][c] else -1
                self.mine_label.setText(f"剩余地雷: {self.num_mines - self.flags_placed}")
                self.board.update()
        
        elif action == 'reveal':
            if self.board.flagged[r][c] or self.board.revealed[r][c]: return
            
            if self.first_click:
                self.place_mines(r, c)
                self.first_click = False
                
            if self.board.mines[r][c]:
                self.board.revealed[r][c] = True
                self.game_over(False)
            else:
                self.flood_fill(r, c)
                self.check_win()
            self.board.update()

    def flood_fill(self, r, c):
        stack = [(r, c)]
        while stack:
            curr_r, curr_c = stack.pop()
            if not (0 <= curr_r < self.rows and 0 <= curr_c < self.cols): continue
            if self.board.revealed[curr_r][curr_c] or self.board.flagged[curr_r][curr_c]: continue
            
            self.board.revealed[curr_r][curr_c] = True
            if self.board.neighbors[curr_r][curr_c] == 0:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr != 0 or dc != 0:
                            stack.append((curr_r + dr, curr_c + dc))

    def check_win(self):
        revealed_count = sum(1 for r in range(self.rows) for c in range(self.cols) if self.board.revealed[r][c])
        if revealed_count == self.rows * self.cols - self.num_mines:
            self.game_over(True)

    def game_over(self, win):
        self.board.game_over = True
        if win:
            self.pet.coins += 100
            self.pet.save_data()
            if self.pet.chat_window: self.pet.chat_window.update_aff_ui()
            self.result_label.setText("🎉 扫雷成功！奖金 100 金币已到账！")
            self.result_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #16a34a;")
            
            # Flag all remaining mines
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board.mines[r][c]:
                        self.board.flagged[r][c] = True
            self.mine_label.setText("剩余地雷: 0")
        else:
            self.result_label.setText("💥 踩到地雷了！呜呜呜门票打水漂了...")
            self.result_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #dc2626;")