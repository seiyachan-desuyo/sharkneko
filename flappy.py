import os
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QKeyEvent, QMouseEvent

class FlappyBoard(QWidget):
    score_changed = pyqtSignal(int)
    game_over_signal = pyqtSignal()

    def __init__(self, pet, parent=None):
        super().__init__(parent)
        self.pet = pet
        self.setFixedSize(400, 500)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # 加载图片并水平翻转（原本可能朝左，现在改成朝右飞）
        from PyQt6.QtGui import QTransform
        img_fly_raw = QPixmap(os.path.join(self.pet.image_dir, "fly.png"))
        img_fall_raw = QPixmap(os.path.join(self.pet.image_dir, "fall.png"))
        
        if not img_fly_raw.isNull():
            self.img_fly = img_fly_raw.transformed(QTransform().scale(-1, 1))
        else:
            self.img_fly = img_fly_raw
            
        if not img_fall_raw.isNull():
            self.img_fall = img_fall_raw.transformed(QTransform().scale(-1, 1))
        else:
            self.img_fall = img_fall_raw
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        
        self.is_started = False
        self.game_over = False
        self.score = 0
        
        self.reset_game_state()

    def reset_game_state(self):
        self.bird_x = 60
        self.bird_y = 220
        self.bird_size = 46
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -7.5
        
        self.pipes = []
        self.pipe_width = 56
        self.pipe_gap = 160
        self.pipe_speed = 3
        self.spawn_timer = 0
        
        self.score = 0
        self.score_changed.emit(self.score)
        
        self.game_over = False
        self.is_started = False
        self.update()

    def start_game(self):
        self.reset_game_state()
        self.is_started = True
        self.timer.start(16) # 约 60 FPS

    def jump(self):
        if not self.is_started and not self.game_over:
            # 第一次按键自动开始
            self.start_game()
        
        if self.is_started and not self.game_over:
            self.velocity = self.jump_strength

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.jump()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self.jump()

    def update_game(self):
        if not self.is_started or self.game_over:
            return

        # 物理计算 (重力)
        self.velocity += self.gravity
        self.bird_y += self.velocity
        
        # 生成水管
        self.spawn_timer += 1
        if self.spawn_timer > 95: # 每约 1.5 秒生成一个水管
            self.spawn_timer = 0
            top_h = random.randint(50, self.height() - self.pipe_gap - 50)
            self.pipes.append({
                'x': self.width(),
                'top_h': top_h,
                'bottom_y': top_h + self.pipe_gap,
                'passed': False
            })
            
        # 移动水管
        for p in self.pipes:
            p['x'] -= self.pipe_speed
            
            # 加分判定
            if not p['passed'] and p['x'] + self.pipe_width < self.bird_x:
                p['passed'] = True
                self.score += 1
                self.score_changed.emit(self.score)
                
        # 移除移出屏幕的水管
        if self.pipes and self.pipes[0]['x'] < -self.pipe_width:
            self.pipes.pop(0)

        # 碰撞检测
        bird_rect = QRectF(self.bird_x, self.bird_y, self.bird_size, self.bird_size)
        
        # 上下边缘检测
        if self.bird_y < 0 or self.bird_y + self.bird_size > self.height():
            self.trigger_game_over()
            
        # 管道检测 (为了手感稍微缩小一点 hitbox)
        hitbox = bird_rect.adjusted(6, 6, -6, -6)
        for p in self.pipes:
            rect_top = QRectF(p['x'], 0, self.pipe_width, p['top_h'])
            rect_bottom = QRectF(p['x'], p['bottom_y'], self.pipe_width, self.height() - p['bottom_y'])
            
            if hitbox.intersects(rect_top) or hitbox.intersects(rect_bottom):
                self.trigger_game_over()
                
        self.update()

    def trigger_game_over(self):
        self.game_over = True
        self.timer.stop()
        self.update()
        self.game_over_signal.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 绘制天空背景 (清晨的渐变蓝)
        painter.fillRect(self.rect(), QColor("#e0f2fe"))
        
        # 画点简单的花花草草点缀 (底部地面和远处景色)
        painter.setBrush(QBrush(QColor("#a7f3d0")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.width() - 100, self.height() - 40, 150, 80)
        painter.drawEllipse(-20, self.height() - 60, 180, 100)
        
        painter.setBrush(QBrush(QColor("#fca5a5")))
        painter.drawEllipse(30, self.height() - 50, 20, 20)
        painter.drawEllipse(self.width() - 50, self.height() - 30, 15, 15)
        
        # 绘制水管 (深海蓝系，符合猫猫鲨主题)
        painter.setPen(QPen(QColor("#1e3a8a"), 3)) # 深蓝描边
        painter.setBrush(QBrush(QColor("#3b82f6"))) # 漂亮的主题蓝
        for p in self.pipes:
            # 上水管
            painter.drawRect(int(p['x']), 0, self.pipe_width, int(p['top_h']))
            # 上水管管口加粗部分
            painter.drawRect(int(p['x']) - 2, int(p['top_h']) - 20, self.pipe_width + 4, 20)
            
            # 下水管
            painter.drawRect(int(p['x']), int(p['bottom_y']), self.pipe_width, int(self.height() - p['bottom_y']))
            # 下水管管口加粗部分
            painter.drawRect(int(p['x']) - 2, int(p['bottom_y']), self.pipe_width + 4, 20)
            
        # 绘制猫猫鲨
        if self.game_over:
            img = self.img_fall
        else:
            img = self.img_fly
            
        if not img.isNull():
            # 缩放并绘制图片
            painter.drawPixmap(int(self.bird_x), int(self.bird_y), self.bird_size, self.bird_size, img)
        else:
            # 如果图片没找到，画个粉色圆圈代替
            painter.setBrush(QBrush(QColor("#ff9ec4")))
            painter.drawEllipse(int(self.bird_x), int(self.bird_y), self.bird_size, self.bird_size)

        # 游戏未开始提示
        if not self.is_started and not self.game_over:
            painter.setPen(QColor("#1e3a8a"))
            painter.setFont(QFont("PingFang SC", 18, QFont.Weight.Bold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "点击左/右键 或 按空格 起飞")

class FlappyWindow(QWidget):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.ticket_price = 10
        self.init_ui()
        
    def init_ui(self):
        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle("飞翔猫猫鲨")
        self.setStyleSheet(
            "QWidget { background-color: #f0f8ff; color: #1e3a8a; font-family: 'PingFang SC', 'Microsoft YaHei'; }"
            "QLabel { color: #1e3a8a; }"
            "QPushButton { background-color: #dbeafe; border: 2px solid #93c5fd; border-radius: 8px; padding: 8px 16px; font-size: 14px; font-weight: bold; color: #1e3a8a; }"
            "QPushButton:hover { background-color: #bfdbfe; border-color: #60a5fa; }"
            "QPushButton:pressed { background-color: #93c5fd; }"
            "QPushButton:disabled { background-color: #f1f5f9; color: #9ca3af; border-color: #cbd5e1; }"
        )
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 左侧：游戏区域
        board_wrapper = QWidget()
        board_wrapper.setStyleSheet("background-color: #ffffff; border: 3px solid #93c5fd; border-radius: 5px;")
        board_layout = QVBoxLayout(board_wrapper)
        board_layout.setContentsMargins(5, 5, 5, 5)
        
        self.board = FlappyBoard(self.pet, self)
        self.board.score_changed.connect(self.update_score)
        self.board.game_over_signal.connect(self.on_game_over)
        board_layout.addWidget(self.board)
        main_layout.addWidget(board_wrapper)
        
        # 右侧：面板
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        title = QLabel("飞翔猫猫鲨 🦅")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2563eb;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(title)
        
        info_label = QLabel("门票: 10 金币\n结算: 1个水管 = 1金币\n\n(注意: 飞太高、掉地上、\n撞水管都会导致坠落哦)")
        info_label.setStyleSheet("font-size: 13px; background-color: #ffffff; border: 2px solid #bfdbfe; border-radius: 8px; padding: 10px;")
        right_panel.addWidget(info_label)
        
        self.score_label = QLabel("得分: 0")
        self.score_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #16a34a;")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.score_label)
        
        controls = QLabel("操作说明：\n鼠标左右键 或 【空格】\n可以给猫猫鲨向上动力")
        controls.setStyleSheet("font-size: 13px; background-color: #e0f2fe; border: 2px solid #93c5fd; border-radius: 8px; padding: 10px;")
        right_panel.addWidget(controls)
        
        right_panel.addStretch()
        
        self.start_btn = QPushButton("交门票 (-10金币)")
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
        self.start_btn.setText("游戏中...")
        self.score_label.setText("得分: 0")
        self.board.reset_game_state()
        self.board.setFocus()
        
    def update_score(self, score):
        self.score_label.setText(f"得分: {score}")
        
    def on_game_over(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("再飞一次 (-10金币)")
        
        coins_earned = self.board.score
        
        if coins_earned > 0:
            self.pet.coins += coins_earned
            self.pet.save_data()
            if self.pet.chat_window: self.pet.chat_window.update_aff_ui()
            msg = f"哎呀，摔倒啦！\n你成功飞过了 {self.board.score} 根水管。\n\n根据 1水管=1金币 的汇率，\n你赚到了 {coins_earned} 金币！"
        else:
            msg = "哎呀，刚起飞就摔倒啦！\n你获得了 0 分...\n门票打水漂啦，下次加油！"
            
        QMessageBox.information(self, "游戏结束", msg)