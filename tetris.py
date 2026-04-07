import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QKeyEvent

# Tetris shapes (Tetrominoes)
SHAPES = [
    [], # NoShape
    [[0, -1], [0, 0], [-1, 0], [-1, 1]], # ZShape
    [[0, -1], [0, 0], [1, 0], [1, 1]],   # SShape
    [[0, -1], [0, 0], [0, 1], [0, 2]],   # LineShape
    [[-1, 0], [0, 0], [1, 0], [0, 1]],   # TShape
    [[0, 0], [1, 0], [0, 1], [1, 1]],    # SquareShape
    [[-1, -1], [0, -1], [0, 0], [0, 1]], # LShape
    [[1, -1], [0, -1], [0, 0], [0, 1]]   # MirroredLShape
]

COLORS = [
    "#f0f8ff", # background (NoShape)
    "#ef4444", # red
    "#22c55e", # green
    "#3b82f6", # blue
    "#a855f7", # purple
    "#eab308", # orange
    "#ec4899", # pink
    "#14b8a6"  # teal
]

class TetrisBoard(QWidget):
    score_changed = pyqtSignal(int)
    game_over_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_width = 10
        self.board_height = 20
        self.cell_size = 28
        self.setFixedSize(self.board_width * self.cell_size, self.board_height * self.cell_size)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        
        self.is_paused = False
        self.is_started = False
        self.board = []
        self.clear_board()
        
        self.cur_piece = []
        self.cur_x = 0
        self.cur_y = 0
        self.cur_shape_id = 0
        
        self.score = 0
        self.speed = 500

    def start_game(self):
        self.clear_board()
        self.is_started = True
        self.is_paused = False
        self.score = 0
        self.speed = 500
        self.score_changed.emit(self.score)
        self.new_piece()
        self.timer.start(self.speed)

    def pause_game(self):
        if not self.is_started: return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer.stop()
        else:
            self.timer.start(self.speed)
        self.update()

    def clear_board(self):
        self.board = [[0] * self.board_width for _ in range(self.board_height)]

    def new_piece(self):
        self.cur_shape_id = random.randint(1, 7)
        self.cur_piece = [list(p) for p in SHAPES[self.cur_shape_id]]
        self.cur_x = self.board_width // 2
        self.cur_y = 1
        
        if not self.try_move(self.cur_piece, self.cur_x, self.cur_y):
            self.is_started = False
            self.timer.stop()
            self.game_over_signal.emit()

    def try_move(self, piece, new_x, new_y):
        for i in range(4):
            x = new_x + piece[i][0]
            y = new_y + piece[i][1]
            if x < 0 or x >= self.board_width or y < 0 or y >= self.board_height:
                return False
            if self.board[y][x] != 0:
                return False
        
        self.cur_piece = piece
        self.cur_x = new_x
        self.cur_y = new_y
        self.update()
        return True

    def rotate_left(self):
        if self.cur_shape_id == 5: return # Square doesn't rotate
        new_piece = [[-p[1], p[0]] for p in self.cur_piece]
        self.try_move(new_piece, self.cur_x, self.cur_y)

    def drop_down(self):
        while self.try_move(self.cur_piece, self.cur_x, self.cur_y + 1):
            pass
        self.piece_dropped()

    def one_line_down(self):
        if not self.try_move(self.cur_piece, self.cur_x, self.cur_y + 1):
            self.piece_dropped()

    def piece_dropped(self):
        for i in range(4):
            x = self.cur_x + self.cur_piece[i][0]
            y = self.cur_y + self.cur_piece[i][1]
            self.board[y][x] = self.cur_shape_id
            
        self.remove_full_lines()
        if self.is_started:
            self.new_piece()

    def remove_full_lines(self):
        lines_removed = 0
        y = self.board_height - 1
        while y >= 0:
            if all(self.board[y][x] != 0 for x in range(self.board_width)):
                lines_removed += 1
                for yy in range(y, 0, -1):
                    for x in range(self.board_width):
                        self.board[yy][x] = self.board[yy - 1][x]
                for x in range(self.board_width):
                    self.board[0][x] = 0
            else:
                y -= 1
                
        if lines_removed > 0:
            points = [0, 10, 30, 60, 100]
            self.score += points[lines_removed]
            self.score_changed.emit(self.score)
            
            # Increase speed
            new_speed = max(100, 500 - (self.score // 100) * 50)
            if new_speed != self.speed:
                self.speed = new_speed
                self.timer.setInterval(self.speed)

    def game_loop(self):
        if self.is_paused: return
        self.one_line_down()

    def keyPressEvent(self, event: QKeyEvent):
        if not self.is_started or self.cur_shape_id == 0:
            super().keyPressEvent(event)
            return

        key = event.key()
        if key == Qt.Key.Key_P:
            self.pause_game()
            return
            
        if self.is_paused: return
        
        if key == Qt.Key.Key_Left:
            self.try_move(self.cur_piece, self.cur_x - 1, self.cur_y)
        elif key == Qt.Key.Key_Right:
            self.try_move(self.cur_piece, self.cur_x + 1, self.cur_y)
        elif key == Qt.Key.Key_Down:
            self.one_line_down()
        elif key == Qt.Key.Key_Up:
            self.rotate_left()
        elif key == Qt.Key.Key_Space:
            self.drop_down()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Background
        painter.fillRect(self.rect(), QColor("#f0f8ff"))
        
        # Grid lines
        painter.setPen(QPen(QColor("#dbeafe"), 1))
        for x in range(self.board_width):
            painter.drawLine(x * self.cell_size, 0, x * self.cell_size, self.height())
        for y in range(self.board_height):
            painter.drawLine(0, y * self.cell_size, self.width(), y * self.cell_size)
            
        # Draw placed blocks
        for y in range(self.board_height):
            for x in range(self.board_width):
                shape_id = self.board[y][x]
                if shape_id != 0:
                    self.draw_square(painter, x * self.cell_size, y * self.cell_size, shape_id)
                    
        # Draw current piece
        if self.cur_shape_id != 0:
            for i in range(4):
                x = self.cur_x + self.cur_piece[i][0]
                y = self.cur_y + self.cur_piece[i][1]
                self.draw_square(painter, x * self.cell_size, y * self.cell_size, self.cur_shape_id)
                
        # Draw pause overlay
        if self.is_paused:
            painter.setBrush(QColor(255, 255, 255, 150))
            painter.drawRect(self.rect())
            painter.setPen(QColor("#1e3a8a"))
            painter.setFont(QFont("PingFang SC", 20, QFont.Weight.Bold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "PAUSED")

    def draw_square(self, painter, x, y, shape_id):
        color = QColor(COLORS[shape_id])
        painter.fillRect(x + 1, y + 1, self.cell_size - 2, self.cell_size - 2, color)
        
        painter.setPen(color.lighter(120))
        painter.drawLine(x, y + self.cell_size - 1, x, y)
        painter.drawLine(x, y, x + self.cell_size - 1, y)
        
        painter.setPen(color.darker(120))
        painter.drawLine(x + 1, y + self.cell_size - 1, x + self.cell_size - 1, y + self.cell_size - 1)
        painter.drawLine(x + self.cell_size - 1, y + self.cell_size - 1, x + self.cell_size - 1, y + 1)


class TetrisWindow(QWidget):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.ticket_price = 10
        self.init_ui()
        
    def init_ui(self):
        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle("猫猫鲨俄罗斯方块")
        self.setStyleSheet(
            "QWidget { background-color: #f0f8ff; color: #1e3a8a; font-family: 'PingFang SC', 'Microsoft YaHei'; }"
            "QLabel { color: #1e3a8a; }"
            "QPushButton { background-color: #dbeafe; border: 2px solid #93c5fd; border-radius: 8px; padding: 8px 16px; font-size: 14px; font-weight: bold; color: #1e3a8a; }"
            "QPushButton:hover { background-color: #bfdbfe; border-color: #60a5fa; }"
            "QPushButton:pressed { background-color: #93c5fd; }"
        )
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left side: Board
        self.board = TetrisBoard(self)
        self.board.score_changed.connect(self.update_score)
        self.board.game_over_signal.connect(self.on_game_over)
        
        board_container = QVBoxLayout()
        
        # 加上精致的边框
        board_wrapper = QWidget()
        board_wrapper.setStyleSheet("background-color: #ffffff; border: 3px solid #93c5fd; border-radius: 5px;")
        board_layout = QVBoxLayout(board_wrapper)
        board_layout.setContentsMargins(5, 5, 5, 5)
        board_layout.addWidget(self.board)
        
        board_container.addWidget(board_wrapper)
        main_layout.addLayout(board_container)
        
        # Right side: Info and Controls
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        title = QLabel("俄罗斯方块 🧱")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2563eb;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(title)
        
        info_label = QLabel("门票: 10 金币\n结算: 1分 = 1金币\n(消除越多奖励越高)")
        info_label.setStyleSheet("font-size: 13px; background-color: #ffffff; border: 2px solid #bfdbfe; border-radius: 8px; padding: 10px;")
        right_panel.addWidget(info_label)
        
        self.score_label = QLabel("得分: 0")
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #16a34a;")
        right_panel.addWidget(self.score_label)
        
        controls = QLabel("操作说明：\n↑: 旋转\n↓: 加速\n← →: 移动\n空格: 秒降\nP: 暂停/继续")
        controls.setStyleSheet("font-size: 13px; background-color: #e0f2fe; border: 2px solid #93c5fd; border-radius: 8px; padding: 10px;")
        right_panel.addWidget(controls)
        
        right_panel.addStretch()
        
        self.start_btn = QPushButton("开始游戏 (-10金币)")
        self.start_btn.clicked.connect(self.try_start)
        right_panel.addWidget(self.start_btn)
        
        main_layout.addLayout(right_panel)
        self.adjustSize()
        
    def try_start(self):
        if self.pet.coins < self.ticket_price:
            QMessageBox.warning(self, "金币不足", "你的金币不够支付门票哦，快去打工吧！")
            return
            
        self.pet.coins -= self.ticket_price
        self.pet.save_data()
        if self.pet.chat_window: self.pet.chat_window.update_aff_ui()
        
        self.start_btn.setEnabled(False)
        self.score_label.setText("得分: 0")
        self.board.start_game()
        self.board.setFocus()
        
    def update_score(self, score):
        self.score_label.setText(f"得分: {score}")
        
    def on_game_over(self):
        self.start_btn.setEnabled(True)
        final_score = self.board.score
        
        # Calculate coins: 1 score = 1 coin
        coins_earned = final_score
        
        if coins_earned > 0:
            self.pet.coins += coins_earned
            self.pet.save_data()
            if self.pet.chat_window: self.pet.chat_window.update_aff_ui()
            msg = f"游戏结束！你获得了 {final_score} 分。\n\n根据 1分=1金币 的汇率，\n你赚到了 {coins_earned} 金币！"
        else:
            msg = "游戏结束！你获得了 0 分...\n门票打水漂啦，下次加油！"
            
        QMessageBox.information(self, "游戏结束", msg)