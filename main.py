from datetime import datetime, timedelta

import sys
import traceback
import datetime as _my_dt

def global_exception_handler(exc_type, exc_value, exc_traceback):
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with open("crash_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- {_my_dt.datetime.now()} ---\n")
        f.write(err_msg)
    print(err_msg)
    
sys.excepthook = global_exception_handler

import os
import random
import platform
import json
import urllib.request

from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QMenu, 
                             QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QDialog)
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QRect, QEasingCurve, QThread, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QSoundEffect

# ================= AI 聊天线程 =================
class ChatWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        self.api_key = "sk-1c0699f12a874b698ae5a97a1f53ce25"

    def run(self):
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": self.messages,
            "temperature": 0.7
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                reply = res_json["choices"][0]["message"]["content"]
                self.finished.emit(reply)
        except Exception as e:
            self.error.emit(str(e))

# ================= AI 聊天窗口 =================
class ChatWindow(QWidget):
    def __init__(self, pet, parent=None):
        super().__init__(parent)
        self.pet = pet
        self.tail_side = "left"
        
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint
        import platform
        if platform.system() == "Windows":
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(280, 130)
        self.main_layout = QVBoxLayout(self)
        
        # === 头部 (好感度 + 关闭按钮) ===
        header_layout = QHBoxLayout()
        self.aff_label = QLabel(self.get_aff_text())
        self.aff_label.setStyleSheet("color: #ff6699; font-weight: bold; font-size: 12px; font-family: 'PingFang SC', sans-serif;")
        
        close_btn = QPushButton("✖")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("QPushButton { background-color: transparent; color: #333; border: none; font-weight: bold; font-size: 14px; } QPushButton:hover { color: #ff4d4d; }")
        close_btn.clicked.connect(self.hide)
        
        header_layout.addWidget(self.aff_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        self.main_layout.addLayout(header_layout)
        
        # === 聊天记录 ===
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        # 像素风虚线边框
        self.chat_history.setStyleSheet("QTextEdit { border: none; background-color: transparent; font-size: 12px; color: #333; padding: 0px; font-family: 'PingFang SC', sans-serif; }")
        self.chat_history.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.chat_history)
        
        # === 输入框 ===
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.input_field.setStyleSheet("QLineEdit { border: 2px solid #333; background-color: white; padding: 4px; font-weight: bold; font-family: 'PingFang SC', sans-serif; font-size: 12px; border-radius: 4px; }")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(28, 28)
        self.send_btn.setStyleSheet("QPushButton { background-color: #333; color: white; border: 2px solid #333; font-weight: bold; font-size: 12px; border-radius: 4px; } QPushButton:hover { background-color: #555; }")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        self.main_layout.addLayout(input_layout)
        
        self.messages = [{"role": "system", "content": self.get_system_prompt()}]
        self.worker = None
        self.append_msg(self.pet.pet_name, "咕噜咕噜！你想和本宝宝聊点什么呀？", "#66a3ff")
        
    def paintEvent(self, event):
        # 纯代码绘制像素风气泡和尖角
        from PyQt6.QtGui import QPainter, QPen, QColor, QPolygon
        from PyQt6.QtCore import QPoint
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False) # 关闭抗锯齿，实现像素边缘
        
        tail_w = 16
        if self.tail_side == "left":
            rect_x = tail_w
            rect_w = self.width() - tail_w - 4
        else:
            rect_x = 4
            rect_w = self.width() - tail_w - 4
            
        rect_y = 4
        rect_h = self.height() - 8
        
        # 画白色底和粗黑边
        painter.fillRect(rect_x, rect_y, rect_w, rect_h, QColor("white"))
        pen = QPen(QColor("#333333"), 4)
        painter.setPen(pen)
        painter.drawRect(rect_x, rect_y, rect_w, rect_h)
        
        # 画指向猫猫鲨的小尾巴
        tail_y_start = 20
        if self.tail_side == "left":
            poly = QPolygon([
                QPoint(rect_x, tail_y_start),
                QPoint(2, tail_y_start + 12),
                QPoint(rect_x, tail_y_start + 24)
            ])
            painter.setBrush(QColor("white"))
            painter.drawPolygon(poly)
            
            # 抹掉连接处的黑线
            painter.setPen(QPen(QColor("white"), 4))
            painter.drawLine(rect_x, tail_y_start + 2, rect_x, tail_y_start + 22)
            
            # 画尾巴的黑边
            painter.setPen(pen)
            painter.drawLine(rect_x, tail_y_start, 2, tail_y_start + 12)
            painter.drawLine(2, tail_y_start + 12, rect_x, tail_y_start + 24)
        else:
            right_edge = rect_x + rect_w
            poly = QPolygon([
                QPoint(right_edge, tail_y_start),
                QPoint(self.width()-2, tail_y_start + 12),
                QPoint(right_edge, tail_y_start + 24)
            ])
            painter.setBrush(QColor("white"))
            painter.drawPolygon(poly)
            
            painter.setPen(QPen(QColor("white"), 4))
            painter.drawLine(right_edge, tail_y_start + 2, right_edge, tail_y_start + 22)
            
            painter.setPen(pen)
            painter.drawLine(right_edge, tail_y_start, self.width()-2, tail_y_start + 12)
            painter.drawLine(self.width()-2, tail_y_start + 12, right_edge, tail_y_start + 24)

    def update_position(self):
        # 让气泡紧紧跟着猫猫鲨
        pet_x = self.pet.x()
        pet_y = self.pet.y()
        pet_w = self.pet.width()
        
        screen_geo = QApplication.primaryScreen().availableGeometry()
        
        bubble_x = pet_x + pet_w
        bubble_y = pet_y - 20
        self.tail_side = "left"
        
        if bubble_x + self.width() > screen_geo.width():
            bubble_x = pet_x - self.width()
            self.tail_side = "right"
            
        if bubble_y < 0:
            bubble_y = 0
            
        self.move(bubble_x, bubble_y)
        
        # 调整内部布局，给尾巴留出空间
        if self.tail_side == "left":
            self.main_layout.setContentsMargins(20, 8, 8, 8)
        else:
            self.main_layout.setContentsMargins(8, 8, 20, 8)
        self.update()

    def showEvent(self, event):
        self.update_position()
        super().showEvent(event)

    def get_aff_text(self):
        aff = self.pet.affection
        hp = getattr(self.pet, 'hp', 60) # 防止在初始化时还没赋值hp
        coins = getattr(self.pet, 'coins', 0)
        if aff < 30: emoji = "💔"
        elif aff >= 70: emoji = "💗"
        else: emoji = "💛"
        
        hp_emoji = "🩸" if hp <= 30 else "❤️"
        return f"💰 {coins}  |  {hp_emoji} 生命: {hp}/100  |  {emoji} 好感度: {aff}/100"

    def update_aff_ui(self):
        self.aff_label.setText(self.get_aff_text())
        
    def get_system_prompt(self):
        hp = getattr(self.pet, 'hp', 60)
        return f"""你是一只超级可爱的猫猫鲨（一半是猫，一半鲨鱼），你的名字叫【{self.pet.pet_name}】。当妈妈叫你这个名字时，你要有反应。你的妈妈是一条笨蛋大鲨鱼（也就是正在和你聊天的用户）。
你目前对妈妈的好感度是 {self.pet.affection}/100，生命值是 {hp}/100，年龄是 {self.pet.age} 岁。
如果你的生命值低于30，你正处于极度虚弱、想哭的状态。
【房屋与房贷信息】
你当前住在：{['简陋房子', '普通房子', '豪华房子'][self.pet.house_type]}
{f'妈妈目前背负着房贷，每天需还款 {self.pet.mortgage_daily_amount} 金币，已还 {self.pet.mortgage_paid_periods}/{self.pet.mortgage_total_periods} 期。' if self.pet.mortgage_total_periods > 0 and self.pet.mortgage_paid_periods < self.pet.mortgage_total_periods else '妈妈目前没有房贷压力。'}
" + ("\n【特别注意】：你已经被妈妈无情地带去医院做了绝育手术！你失去了繁衍后代的能力。你对此感到非常难过、幽怨和记仇，时不时要阴阳怪气妈妈剥夺了你的权利。" if getattr(self.pet, "is_sterilized", False) else "")

【你的设定】
1. 你永远称呼用户为“妈妈”，绝不能叫“主人”或“你”。
2. 你的好朋友是：方皓鲸、方皓晨龙。
3. 你最喜欢的蔬菜是胡萝卜。
4. 你的爱好是：偷懒睡觉、吃小鱼干、画画、跟妈妈打闹、和妈妈在地上滚来滚去。
5. 你的语气总是奶声奶气的，喜欢用颜文字（如 咕噜咕噜、喵呜、(๑>◡<๑) 等）。
6. 根据好感度表现：低于30分时你很委屈想哭，正常时是个笨蛋宝宝，高于70分时疯狂黏着妈妈撒娇。

【功能指令 (必须遵守)】
1. 如果妈妈要求你记住某事，回复末尾必须加 [Memo:X分钟后|事件] 或 [Memo:HH:MM|事件]。
2. 你必须评估妈妈的话对你好感的影响（-10到+10），在回复末尾加上 [Aff:+X] 或 [Aff:-X]。
3. **字数限制**：你的回复必须极其简短（绝不能超过2句话！），因为你要显示在一个小气泡里！"""

    def append_msg(self, name, text, color):
        # 如果是“你”发消息，先清空屏幕，然后显示“你”的消息
        if name == "你":
            self.chat_history.clear()
        
        # 组装当前的单条消息
        html = f"<div style='margin-bottom: 2px;'><b style='color: {color}; font-size: 12px;'>{name}:</b> <span style='color: #333; font-size: 13px; line-height: 1.3;'>{text}</span></div>"
        self.chat_history.append(html)
        
        # 如果是“猫猫鲨”或“系统”回完消息了，让它自动滚动到最顶部（或者不需要，因为清空过）
        self.chat_history.verticalScrollBar().setValue(0)
        
    def generate_autonomous_reply(self, situation_prompt):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.worker = ChatWorker([
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": situation_prompt}
        ])
        self.worker.finished.connect(self.on_auto_reply)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_auto_reply(self, reply):
        import re
        reply = re.sub(r'\[Aff:\s*([+-]?\d+)\]', '', reply, flags=re.IGNORECASE).strip()
        reply = re.sub(r'\[Memo:\s*(.*?)\|\s*(.*?)\]', '', reply, flags=re.IGNORECASE).strip()
        self.chat_history.clear()
        self.append_msg(self.pet.pet_name, reply, "#0066cc")

    def send_message(self):
        text = self.input_field.text().strip()
        if not text: return
        
        self.append_msg("你", text, "#888")
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.send_btn.setText("...")
        
        self.messages[0]["content"] = self.get_system_prompt()
        self.messages.append({"role": "user", "content": text})
        
        self.worker = ChatWorker(self.messages)
        self.worker.finished.connect(self.on_reply)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_reply(self, reply):
        import re
        match = re.search(r'\[Aff:\s*([+-]?\d+)\]', reply, re.IGNORECASE)
        if match:
            self.pet.change_affection(int(match.group(1)))
            reply = re.sub(r'\[Aff:\s*([+-]?\d+)\]', '', reply, flags=re.IGNORECASE).strip()
            
        memo_match = re.search(r'\[Memo:\s*(.*?)\|\s*(.*?)\]', reply, re.IGNORECASE)
        if memo_match:
            from datetime import datetime, timedelta
            time_str = memo_match.group(1).strip()
            event_str = memo_match.group(2).strip()
            delay_ms = 0
            try:
                if "分钟后" in time_str:
                    match_num = re.search(r'\d+', time_str)
                    if match_num: delay_ms = int(match_num.group()) * 60000
                elif ":" in time_str or "：" in time_str:
                    time_str = time_str.replace("：", ":")
                    parts = time_str.split(":")
                    now = datetime.now()
                    target = now.replace(hour=int(parts[0]), minute=int(parts[1]), second=0, microsecond=0)
                    if target < now: target += timedelta(days=1)
                    delay_ms = int((target - now).total_seconds() * 1000)
            except: pass
            if delay_ms > 0: self.pet.add_reminder(delay_ms, event_str)
            reply = re.sub(r'\[Memo:\s*(.*?)\|\s*(.*?)\]', '', reply, flags=re.IGNORECASE).strip()
            
        self.append_msg(self.pet.pet_name, reply, "#0066cc")
        self.messages.append({"role": "assistant", "content": reply})
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("➤")
        self.input_field.setFocus()
        
    def on_error(self, err):
        self.append_msg("系统", f"网络错误 ({err})", "#ff4d4d")
        self.messages.pop() 
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("➤")

# ================= 召唤出来的妈妈 =================
class MomShark(QWidget):
    def __init__(self, image_dir):
        super().__init__()
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint
        if platform.system() == "Windows":
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.label)
        
        img_path = os.path.join(image_dir, "mom.png")
        if os.path.exists(img_path):
            self.label.setPixmap(QPixmap(img_path))
        
        screen = QApplication.primaryScreen().availableGeometry()
        sw, sh = screen.width(), screen.height()
        
        # 终点大小：高度占屏幕80%
        end_h = int(sh * 0.8)
        end_w = end_h  
        
        start_w, start_h = 100, 100
        
        # 从右下角出现
        self.setGeometry(sw - start_w, sh - start_h, start_w, start_h)
        
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(1500) # 1.5秒变大
        self.anim.setStartValue(QRect(sw - start_w, sh - start_h, start_w, start_h))
        self.anim.setEndValue(QRect(sw - end_w, sh - end_h, end_w, end_h))
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack) 
        self.anim.start()
        
        # 5秒后自动关闭
        QTimer.singleShot(5000, self.close)


class GomokuBoard(QWidget):
    move_played = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_size = 13
        self.cell_size = 28
        self.margin = 22
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.is_interactive = False
        self.hover_cell = None
        self.setMouseTracking(True)

        board_pixels = self.margin * 2 + self.cell_size * (self.board_size - 1)
        self.setFixedSize(board_pixels, board_pixels)

    def reset_board(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.hover_cell = None
        self.update()

    def set_interactive(self, value):
        self.is_interactive = value
        if not value:
            self.hover_cell = None
        self.update()

    def _pixel_to_cell(self, pos):
        x = pos.x()
        y = pos.y()
        col = round((x - self.margin) / self.cell_size)
        row = round((y - self.margin) / self.cell_size)

        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return None

        cell_x = self.margin + col * self.cell_size
        cell_y = self.margin + row * self.cell_size
        tolerance = self.cell_size // 2
        if abs(x - cell_x) > tolerance or abs(y - cell_y) > tolerance:
            return None

        return row, col

    def mouseMoveEvent(self, event):
        cell = self._pixel_to_cell(event.position().toPoint())
        if self.is_interactive and cell:
            row, col = cell
            self.hover_cell = cell if self.board[row][col] == 0 else None
        else:
            self.hover_cell = None
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hover_cell = None
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if not self.is_interactive or event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        cell = self._pixel_to_cell(event.position().toPoint())
        if not cell:
            return

        row, col = cell
        if self.board[row][col] != 0:
            return

        self.move_played.emit(row, col)

    def paintEvent(self, event):
        from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
        from PyQt6.QtCore import QRectF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        board_rect = QRectF(0.0, 0.0, float(self.width()), float(self.height()))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#93c5fd"), 3))
        painter.drawRoundedRect(board_rect, 15.0, 15.0)

        grid_pen = QPen(QColor("#bfdbfe"), 2)
        painter.setPen(grid_pen)
        for index in range(self.board_size):
            offset = self.margin + index * self.cell_size
            painter.drawLine(self.margin, offset, self.width() - self.margin, offset)
            painter.drawLine(offset, self.margin, offset, self.height() - self.margin)

        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece == 0:
                    continue

                center_x = self.margin + col * self.cell_size
                center_y = self.margin + row * self.cell_size

                if piece == 1:
                    painter.setBrush(QBrush(QColor("#ffffff")))
                    painter.setPen(QPen(QColor("#60a5fa"), 2))
                    painter.drawEllipse(center_x - 9, center_y - 11, 8, 9)
                    painter.drawEllipse(center_x + 1, center_y - 11, 8, 9)
                    painter.drawEllipse(center_x - 11, center_y - 9, 22, 22)
                    painter.setBrush(QBrush(QColor("#1e3a8a")))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(center_x - 5, center_y - 2, 3, 3)
                    painter.drawEllipse(center_x + 2, center_y - 2, 3, 3)
                else:
                    painter.setBrush(QBrush(QColor("#3b82f6")))
                    painter.setPen(QPen(QColor("#1e3a8a"), 2))
                    painter.drawEllipse(center_x - 4, center_y - 12, 8, 11)
                    painter.drawEllipse(center_x - 11, center_y - 9, 22, 22)
                    painter.setBrush(QBrush(QColor("#ffffff")))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(center_x - 6, center_y - 3, 4, 4)
                    painter.drawEllipse(center_x + 2, center_y - 3, 4, 4)
                    painter.setBrush(QBrush(QColor("#1e3a8a")))
                    painter.drawEllipse(center_x - 4, center_y - 2, 2, 2)
                    painter.drawEllipse(center_x + 4, center_y - 2, 2, 2)

        if self.is_interactive and self.hover_cell:
            row, col = self.hover_cell
            if self.board[row][col] == 0:
                center_x = self.margin + col * self.cell_size
                center_y = self.margin + row * self.cell_size
                painter.setPen(QPen(QColor("#93c5fd"), 2, Qt.PenStyle.DashLine))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(center_x - 11, center_y - 11, 22, 22)


class GomokuWindow(QWidget):
    ROUND_CONFIGS = [
        {"name": "第一局", "reward": 30, "penalty": 10, "difficulty": 1},
        {"name": "第二局", "reward": 50, "penalty": 30, "difficulty": 2},
        {"name": "第三局", "reward": 100, "penalty": 70, "difficulty": 3},
    ]

    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.round_index = -1
        self.challenge_active = False
        self.waiting_choice = False

        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle("猫猫鲨五子棋")
        self.setStyleSheet(
            "QWidget { background-color: #f0f8ff; color: #1e3a8a; font-family: 'PingFang SC', 'Microsoft YaHei'; }"
            "QLabel { color: #1e3a8a; }"
            "QPushButton { background-color: #dbeafe; border: 2px solid #93c5fd; border-radius: 10px; padding: 8px 14px; font-size: 13px; font-weight: bold; color: #1e3a8a; }"
            "QPushButton:hover { background-color: #bfdbfe; border-color: #60a5fa; }"
            "QPushButton:pressed { background-color: #93c5fd; }"
            "QPushButton:disabled { background-color: #f1f5f9; color: #9ca3af; border-color: #cbd5e1; }"
        )
        self.resize(460, 680)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.title_label = QLabel("猫猫鲨五子棋挑战赛")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2563eb;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.coin_label = QLabel()
        self.coin_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
        self.coin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.coin_label)

        self.round_label = QLabel("门票 10 金币，一次最多三局。赢了再决定要不要继续。")
        self.round_label.setStyleSheet("font-size: 13px; background-color: #ffffff; border: 2px solid #bfdbfe; border-radius: 8px; padding: 8px;")
        layout.addWidget(self.round_label)

        self.rule_label = QLabel("第一局赢 +30 / 输 -10\n第二局赢 +50 / 输 -30\n第三局赢 +100 / 输 -70")
        self.rule_label.setStyleSheet("font-size: 13px; background-color: #ffffff; border: 2px solid #bfdbfe; border-radius: 8px; padding: 8px;")
        layout.addWidget(self.rule_label)

        self.status_label = QLabel("点“开始挑战”进入第一局。你是白猫棋子，AI 是蓝鲨棋子。")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e0f2fe; border: 2px solid #93c5fd; border-radius: 8px; padding: 10px; color: #1d4ed8;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.board_widget = GomokuBoard(self)
        self.board_widget.move_played.connect(self.handle_player_move)
        layout.addWidget(self.board_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        self.start_btn = QPushButton("开始挑战 -10 金币")
        self.start_btn.clicked.connect(self.start_new_challenge)
        self.continue_btn = QPushButton("继续下一局")
        self.continue_btn.clicked.connect(self.continue_challenge)
        self.stop_btn = QPushButton("这局就收手")
        self.stop_btn.clicked.connect(self.cash_out)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.continue_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)

        self.continue_btn.hide()
        self.stop_btn.hide()
        self.update_coin_label()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def update_coin_label(self):
        self.coin_label.setText(f"当前金币: {self.pet.coins}    当前挑战: {self.get_round_name()}")

    def get_round_name(self):
        if 0 <= self.round_index < len(self.ROUND_CONFIGS):
            return self.ROUND_CONFIGS[self.round_index]["name"]
        return "未开始"

    def sync_pet_data(self):
        self.pet.save_data()
        if self.pet.chat_window:
            self.pet.chat_window.update_aff_ui()
        self.update_coin_label()

    def set_idle_state(self, text):
        self.challenge_active = False
        self.waiting_choice = False
        self.board_widget.set_interactive(False)
        self.start_btn.show()
        self.continue_btn.hide()
        self.stop_btn.hide()
        self.status_label.setText(text)
        self.round_index = -1
        self.update_coin_label()

    def start_new_challenge(self):
        if self.pet.coins < 10:
            self.status_label.setText("金币不够，先去打工或者挣点钱再来挑战吧。")
            return

        self.pet.coins -= 10
        self.sync_pet_data()
        self.round_index = 0
        self.challenge_active = True
        self.waiting_choice = False
        self.start_btn.hide()
        self.continue_btn.hide()
        self.stop_btn.hide()
        self.start_round()

    def continue_challenge(self):
        if not self.waiting_choice:
            return

        self.round_index += 1
        if self.round_index >= len(self.ROUND_CONFIGS):
            self.set_idle_state("三局全胜！你已经把今天的猫猫鲨棋圣称号拿走啦。")
            return

        self.challenge_active = True
        self.waiting_choice = False
        self.continue_btn.hide()
        self.stop_btn.hide()
        self.start_round()

    def cash_out(self):
        if not self.waiting_choice:
            return
        self.set_idle_state("你选择见好就收，成功把奖金装进口袋啦。")

    def start_round(self):
        config = self.ROUND_CONFIGS[self.round_index]
        self.board_widget.reset_board()
        self.board_widget.set_interactive(True)
        self.round_label.setText(
            f"{config['name']} 开始。赢了 +{config['reward']} 金币，输了 -{config['penalty']} 金币。"
        )
        self.status_label.setText(f"{config['name']} 已开局。你先手，先连成五个就赢。")
        self.update_coin_label()

    def handle_player_move(self, row, col):
        if not self.challenge_active or self.waiting_choice:
            return
        if self.board_widget.board[row][col] != 0:
            return

        self.board_widget.board[row][col] = 1
        self.board_widget.update()

        if self.is_winner(row, col, 1):
            self.handle_round_win()
            return

        if self.is_board_full():
            self.restart_round_due_to_draw()
            return

        self.board_widget.set_interactive(False)
        self.status_label.setText("AI 正在搓小脑袋想招数...")
        QTimer.singleShot(250, self.make_ai_move)

    def make_ai_move(self):
        if not self.challenge_active:
            return

        move = self.choose_ai_move()
        if move is None:
            self.restart_round_due_to_draw()
            return

        row, col = move
        self.board_widget.board[row][col] = 2
        self.board_widget.update()

        if self.is_winner(row, col, 2):
            self.handle_round_loss()
            return

        if self.is_board_full():
            self.restart_round_due_to_draw()
            return

        self.board_widget.set_interactive(True)
        self.status_label.setText("轮到你啦，白猫棋子快冲。")

    def handle_round_win(self):
        config = self.ROUND_CONFIGS[self.round_index]
        self.pet.coins += config['reward']
        self.sync_pet_data()
        self.challenge_active = False
        self.board_widget.set_interactive(False)

        if self.round_index == len(self.ROUND_CONFIGS) - 1:
            self.set_idle_state(f"第三局也赢了！本轮直接到账 {config['reward']} 金币，你已经通关啦。")
            return

        self.waiting_choice = True
        next_round = self.ROUND_CONFIGS[self.round_index + 1]['name']
        self.continue_btn.show()
        self.stop_btn.show()
        self.status_label.setText(
            f"{config['name']} 胜利，已到账 {config['reward']} 金币。要继续挑战 {next_round}，还是现在收手？"
        )
        self.update_coin_label()

    def handle_round_loss(self):
        config = self.ROUND_CONFIGS[self.round_index]
        self.pet.coins = max(0, self.pet.coins - config['penalty'])
        self.sync_pet_data()
        self.set_idle_state(f"{config['name']} 输了，扣了 {config['penalty']} 金币。本次挑战结束。")

    def restart_round_due_to_draw(self):
        self.board_widget.reset_board()
        self.board_widget.set_interactive(True)
        self.status_label.setText(f"{self.get_round_name()} 平局，本局重开，不额外扣钱。")

    def is_board_full(self):
        return all(cell != 0 for row in self.board_widget.board for cell in row)

    def is_winner(self, row, col, player):
        for dr, dc in ((1, 0), (0, 1), (1, 1), (1, -1)):
            count = 1
            count += self.count_direction(row, col, dr, dc, player)
            count += self.count_direction(row, col, -dr, -dc, player)
            if count >= 5:
                return True
        return False

    def count_direction(self, row, col, dr, dc, player):
        board = self.board_widget.board
        size = self.board_widget.board_size
        total = 0
        row += dr
        col += dc
        while 0 <= row < size and 0 <= col < size and board[row][col] == player:
            total += 1
            row += dr
            col += dc
        return total

    def choose_ai_move(self):
        board = self.board_widget.board
        empties = [(row, col) for row in range(self.board_widget.board_size) for col in range(self.board_widget.board_size) if board[row][col] == 0]
        if not empties:
            return None

        for row, col in empties:
            board[row][col] = 2
            if self.is_winner(row, col, 2):
                board[row][col] = 0
                return row, col
            board[row][col] = 0

        for row, col in empties:
            board[row][col] = 1
            if self.is_winner(row, col, 1):
                board[row][col] = 0
                return row, col
            board[row][col] = 0

        difficulty = self.ROUND_CONFIGS[self.round_index]['difficulty']
        center = self.board_widget.board_size // 2
        scored_moves = []

        for row, col in empties:
            attack_score = self.evaluate_move(row, col, 2)
            defend_score = self.evaluate_move(row, col, 1)
            center_bias = (self.board_widget.board_size - (abs(row - center) + abs(col - center))) * 6
            neighbor_bonus = 40 if self.has_neighbor(row, col) else -20
            score = attack_score * (1.0 + difficulty * 0.2) + defend_score * (0.9 + difficulty * 0.15) + center_bias + neighbor_bonus

            if difficulty >= 2 and self.creates_double_threat(row, col, 2):
                score += 2200
            if difficulty >= 3 and self.gives_player_immediate_win(row, col):
                score -= 9000

            scored_moves.append((score, random.random(), row, col))

        scored_moves.sort(reverse=True)
        if difficulty == 1:
            candidates = scored_moves[:min(5, len(scored_moves))]
            _, _, row, col = random.choice(candidates)
            return row, col
        if difficulty == 2:
            candidates = scored_moves[:min(3, len(scored_moves))]
            _, _, row, col = random.choice(candidates)
            return row, col

        _, _, row, col = scored_moves[0]
        return row, col

    def has_neighbor(self, row, col):
        board = self.board_widget.board
        size = self.board_widget.board_size
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr == 0 and dc == 0:
                    continue
                nr = row + dr
                nc = col + dc
                if 0 <= nr < size and 0 <= nc < size and board[nr][nc] != 0:
                    return True
        return False

    def evaluate_move(self, row, col, player):
        board = self.board_widget.board
        board[row][col] = player
        total_score = 0
        strong_lines = 0

        for dr, dc in ((1, 0), (0, 1), (1, 1), (1, -1)):
            count, open_ends = self.get_line_info(row, col, dr, dc, player)
            line_score = self.pattern_score(count, open_ends)
            total_score += line_score
            if count >= 3 and open_ends > 0:
                strong_lines += 1

        if strong_lines >= 2:
            total_score += 3000

        board[row][col] = 0
        return total_score

    def get_line_info(self, row, col, dr, dc, player):
        board = self.board_widget.board
        size = self.board_widget.board_size
        count = 1
        open_ends = 0

        nr = row + dr
        nc = col + dc
        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
            count += 1
            nr += dr
            nc += dc
        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == 0:
            open_ends += 1

        nr = row - dr
        nc = col - dc
        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
            count += 1
            nr -= dr
            nc -= dc
        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == 0:
            open_ends += 1

        return count, open_ends

    def pattern_score(self, count, open_ends):
        if count >= 5:
            return 200000
        if count == 4 and open_ends == 2:
            return 50000
        if count == 4 and open_ends == 1:
            return 12000
        if count == 3 and open_ends == 2:
            return 5000
        if count == 3 and open_ends == 1:
            return 1200
        if count == 2 and open_ends == 2:
            return 400
        if count == 2 and open_ends == 1:
            return 100
        if count == 1 and open_ends == 2:
            return 30
        return 10

    def creates_double_threat(self, row, col, player):
        board = self.board_widget.board
        board[row][col] = player
        threats = 0
        for dr, dc in ((1, 0), (0, 1), (1, 1), (1, -1)):
            count, open_ends = self.get_line_info(row, col, dr, dc, player)
            if (count == 4 and open_ends >= 1) or (count == 3 and open_ends == 2):
                threats += 1
        board[row][col] = 0
        return threats >= 2

    def gives_player_immediate_win(self, row, col):
        board = self.board_widget.board
        board[row][col] = 2
        for next_row in range(self.board_widget.board_size):
            for next_col in range(self.board_widget.board_size):
                if board[next_row][next_col] != 0:
                    continue
                board[next_row][next_col] = 1
                if self.is_winner(next_row, next_col, 1):
                    board[next_row][next_col] = 0
                    board[row][col] = 0
                    return True
                board[next_row][next_col] = 0
        board[row][col] = 0
        return False


class MaggotBattleWindow(QWidget):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.screen_geo = QApplication.primaryScreen().availableGeometry()

        flags = Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle("迎战蛆蛆")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setMinimumSize(800, 600)

        default_width = max(800, self.screen_geo.width() // 2)
        default_height = max(600, self.screen_geo.height() // 2)
        start_x = self.screen_geo.x() + (self.screen_geo.width() - default_width) // 2
        start_y = self.screen_geo.y() + (self.screen_geo.height() - default_height) // 2
        self.setGeometry(start_x, start_y, default_width, default_height)

        self.game_duration_ms = 30000
        self.elapsed_ms = 0
        self.kills = 0
        self.total_spawn_target = random.randint(20, 50)
        self.spawned_count = 0
        self.spawn_accumulator = 0.0
        self.spawn_interval_ms = self.game_duration_ms / self.total_spawn_target
        self.mode = "idle"
        self.keys_pressed = set()
        self.shots = []
        self.maggots = []
        self.finished = False
        self.attack_flash_ms = 0

        self.pet_width = 120
        self.pet_height = 120
        self.projectile_width = 56
        self.projectile_height = 56
        self.maggot_width = 72
        self.maggot_height = 72

        self.pet_x = 140.0
        self.ground_y = 0.0
        self.pet_y = 0.0
        self.pet_velocity_y = 0.0
        self.gravity = 0.7
        self.move_speed = 8.0
        self.shoot_cooldown_ms = 240
        self.shoot_cooldown_left = 0

        image_dir = pet.image_dir
        idle_pixmap = QPixmap(os.path.join(image_dir, "idle.png"))
        self.idle_pixmap = idle_pixmap.transformed(QTransform().scale(-1, 1)) if not idle_pixmap.isNull() else idle_pixmap
        angry_pixmap = QPixmap(os.path.join(image_dir, "angry.png"))
        self.angry_pixmap = angry_pixmap.transformed(QTransform().scale(-1, 1)) if not angry_pixmap.isNull() else angry_pixmap
        fly_pixmap = QPixmap(os.path.join(image_dir, "fly.png"))
        self.fly_pixmap = fly_pixmap.transformed(QTransform().scale(-1, 1)) if not fly_pixmap.isNull() else fly_pixmap
        self.mom_pixmap = QPixmap(os.path.join(image_dir, "mom.png"))
        self.maggot_pixmap = QPixmap(os.path.join(image_dir, "maggot.png"))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        self.update_playfield_bounds(initial=True)

    def start(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def resizeEvent(self, event):
        self.update_playfield_bounds(initial=False)
        super().resizeEvent(event)

    def update_playfield_bounds(self, initial=False):
        current_ground_y = float(self.height() - self.pet_height - 32)
        current_ground_y = max(110.0, current_ground_y)

        if initial:
            self.ground_y = current_ground_y
            self.pet_y = self.ground_y
        else:
            previous_ground_y = self.ground_y
            self.ground_y = current_ground_y
            if self.pet_y >= previous_ground_y - 1:
                self.pet_y = self.ground_y
            else:
                self.pet_y = min(self.pet_y, self.ground_y)

        right_limit = float(max(30, self.width() - self.pet_width - 30))
        self.pet_x = max(30.0, min(right_limit, self.pet_x))

    def closeEvent(self, event):
        if not self.finished:
            self.finish_game("你提前结束了战斗，按击杀数结算。")
            event.ignore()
            return
        super().closeEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_A, Qt.Key.Key_Right, Qt.Key.Key_D):
            self.keys_pressed.add(key)
        elif key == Qt.Key.Key_Space:
            self.fire_projectile()
        elif key == Qt.Key.Key_Escape:
            self.finish_game("你带着战利品先撤退了。")
        event.accept()

    def keyReleaseEvent(self, event):
        self.keys_pressed.discard(event.key())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mode = "fly"
            self.pet_velocity_y = -11.5
        self.update()
        event.accept()

    def spawn_maggot(self):
        lane_top = 90
        lane_bottom = max(lane_top + 1, int(self.ground_y - self.maggot_height + 20))
        maggot = {
            'x': float(self.width() + random.randint(0, 120)),
            'y': float(random.randint(lane_top, lane_bottom)),
            'speed': random.uniform(2.4, 4.8),
            'wiggle': random.uniform(0.6, 1.8),
            'phase': random.uniform(0, 6.28),
        }
        self.maggots.append(maggot)
        self.spawned_count += 1

    def fire_projectile(self):
        if self.shoot_cooldown_left > 0:
            return

        projectile = {
            'x': self.pet_x + self.pet_width - 10,
            'y': self.pet_y + 28,
            'speed': 12.5,
        }
        self.shots.append(projectile)
        self.shoot_cooldown_left = self.shoot_cooldown_ms
        self.attack_flash_ms = 180

    def tick(self):
        if self.finished:
            return

        delta_ms = 16
        self.elapsed_ms += delta_ms
        self.spawn_accumulator += delta_ms
        self.shoot_cooldown_left = max(0, self.shoot_cooldown_left - delta_ms)
        self.attack_flash_ms = max(0, self.attack_flash_ms - delta_ms)

        while self.spawned_count < self.total_spawn_target and self.spawn_accumulator >= self.spawn_interval_ms:
            self.spawn_accumulator -= self.spawn_interval_ms
            self.spawn_maggot()

        move_x = 0
        if Qt.Key.Key_Left in self.keys_pressed or Qt.Key.Key_A in self.keys_pressed:
            move_x -= self.move_speed
        if Qt.Key.Key_Right in self.keys_pressed or Qt.Key.Key_D in self.keys_pressed:
            move_x += self.move_speed

        self.pet_x += move_x
        self.pet_x = max(30.0, min(float(max(30, self.width() - self.pet_width - 30)), self.pet_x))

        self.pet_velocity_y += self.gravity
        self.pet_y += self.pet_velocity_y
        if self.pet_y >= self.ground_y:
            self.pet_y = self.ground_y
            self.pet_velocity_y = 0.0
            if self.mode == "fly":
                self.mode = "idle"
        else:
            self.mode = "fly"

        for shot in self.shots:
            shot['x'] += shot['speed']
        self.shots = [shot for shot in self.shots if shot['x'] <= self.width() + 80]

        for maggot in self.maggots:
            maggot['x'] -= maggot['speed']
            maggot['phase'] += 0.08
            maggot['y'] += maggot['wiggle'] * 0.9 * (1 if random.random() > 0.5 else -1)
            maggot['y'] = max(60.0, min(self.ground_y + 12, maggot['y']))

        self.resolve_collisions()

        if any(maggot['x'] + self.maggot_width < 0 for maggot in self.maggots):
            self.finish_game("蛆蛆溜过了屏幕边界，防线失守了。")
            return

        pet_rect = QRect(int(self.pet_x + 16), int(self.pet_y + 16), self.pet_width - 32, self.pet_height - 32)
        for maggot in self.maggots:
            maggot_rect = QRect(int(maggot['x'] + 10), int(maggot['y'] + 14), self.maggot_width - 20, self.maggot_height - 24)
            if pet_rect.intersects(maggot_rect):
                self.finish_game("猫猫鲨被蛆蛆碰到了，战斗结束。")
                return

        if self.elapsed_ms >= self.game_duration_ms:
            self.finish_game("30 秒到，按击杀数结算奖励。")
            return

        self.update()

    def resolve_collisions(self):
        remaining_shots = []
        removed_maggots = set()

        for shot in self.shots:
            shot_rect = QRect(int(shot['x']), int(shot['y']), self.projectile_width, self.projectile_height)
            hit = False
            for index, maggot in enumerate(self.maggots):
                if index in removed_maggots:
                    continue
                maggot_rect = QRect(int(maggot['x']), int(maggot['y']), self.maggot_width, self.maggot_height)
                if shot_rect.intersects(maggot_rect):
                    removed_maggots.add(index)
                    self.kills += 1
                    hit = True
                    break
            if not hit:
                remaining_shots.append(shot)

        if removed_maggots:
            self.maggots = [maggot for index, maggot in enumerate(self.maggots) if index not in removed_maggots]
        self.shots = remaining_shots

    def finish_game(self, message):
        if self.finished:
            return

        self.finished = True
        self.timer.stop()
        reward = self.kills
        self.pet.coins += reward
        self.pet.save_data()
        self.pet.maggot_battle_window = None
        self.pet.show()
        self.pet.raise_()
        self.pet.activateWindow()
        self.pet.update_image()
        if self.pet.chat_window:
            self.pet.chat_window.update_aff_ui()
        self.pet.open_chat()
        self.pet.chat_window.append_msg("系统", f"迎战蛆蛆结束！打掉了 {self.kills} 只蛆蛆，拿到 {reward} 金币。{message}", "#ff6699")
        self.close()

    def paintEvent(self, event):
        from PyQt6.QtGui import QColor, QPainter, QPen

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QColor(248, 252, 255, 225))

        painter.fillRect(0, 0, self.width(), 88, QColor(255, 242, 247, 230))
        painter.fillRect(0, self.height() - 78, self.width(), 78, QColor(219, 247, 211, 235))
        painter.fillRect(0, self.height() - 96, self.width(), 18, QColor(255, 220, 128, 230))

        painter.setPen(QPen(QColor("#3d2c2e"), 3))
        info_width = min(self.width() - 28, 520)
        painter.drawRect(14, 14, info_width, 92)
        painter.setPen(QColor("#3d2c2e"))
        remaining = max(0, (self.game_duration_ms - self.elapsed_ms) // 1000)
        painter.drawText(28, 42, f"迎战蛆蛆  倒计时: {remaining}s  击杀: {self.kills}")
        painter.drawText(28, 66, f"门票 15 金币 | 左键起飞 | ← → 移动 | 空格发射鲨鲨 | Esc 结算")
        painter.drawText(28, 90, f"本局蛆蛆总数: {self.total_spawn_target}  已出现: {self.spawned_count}")

        pet_pixmap = self.idle_pixmap
        if self.attack_flash_ms > 0:
            pet_pixmap = self.angry_pixmap
        elif self.mode == "fly":
            pet_pixmap = self.fly_pixmap
        if not pet_pixmap.isNull():
            painter.drawPixmap(QRect(int(self.pet_x), int(self.pet_y), self.pet_width, self.pet_height), pet_pixmap)

        if not self.mom_pixmap.isNull():
            for shot in self.shots:
                painter.drawPixmap(QRect(int(shot['x']), int(shot['y']), self.projectile_width, self.projectile_height), self.mom_pixmap)

        if not self.maggot_pixmap.isNull():
            for maggot in self.maggots:
                painter.drawPixmap(QRect(int(maggot['x']), int(maggot['y']), self.maggot_width, self.maggot_height), self.maggot_pixmap)


SHARED_DATA = {
    'coins': 0, 'fish_count': 0, 'water_count': 0, 'shampoo_count': 0,
    'has_fishing_rod': False, 'last_work_time': 0.0, 'maggot_battle_times': [],
    'house_type': 0, 'mortgage_total_periods': 0, 'mortgage_paid_periods': 0,
    'mortgage_daily_amount': 0, 'last_mortgage_date': '', 'is_house_visible': True
}
ALL_PETS = []
GLOBAL_HOUSE = None


# ================= 房子组件 =================
class HouseWidget(QWidget):
    def __init__(self, image_dir):
        super().__init__()
        self.image_dir = image_dir
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint
        import platform
        if platform.system() == "Windows":
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # 穿透鼠标点击，防止挡住桌面
        
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setStyleSheet("background: transparent; border: none;")
        
        self.house_size = 250
        self.resize(self.house_size, self.house_size)
        self.label.resize(self.house_size, self.house_size)
        
        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.move(0, screen_geo.height() - self.house_size)
        
        self.update_house()
        
    def update_house(self):
        if not SHARED_DATA.get('is_house_visible', True):
            self.hide()
            return
            
        htype = SHARED_DATA.get('house_type', 0)
        img_name = f"home{htype + 1}.png"
        img_path = os.path.join(self.image_dir, img_name)
        
        if os.path.exists(img_path):
            self.label.setPixmap(QPixmap(img_path))
            self.show()
        else:
            self.hide()

# ================= 桌宠本体 =================



class CatShark(QWidget):
    @property
    def coins(self): return SHARED_DATA['coins']
    @coins.setter
    def coins(self, val): SHARED_DATA['coins'] = val
    
    @property
    def fish_count(self): return SHARED_DATA['fish_count']
    @fish_count.setter
    def fish_count(self, val): SHARED_DATA['fish_count'] = val
    
    @property
    def water_count(self): return SHARED_DATA['water_count']
    @water_count.setter
    def water_count(self, val): SHARED_DATA['water_count'] = val
    
    @property
    def shampoo_count(self): return SHARED_DATA['shampoo_count']
    @shampoo_count.setter
    def shampoo_count(self, val): SHARED_DATA['shampoo_count'] = val
    
    @property
    def has_fishing_rod(self): return SHARED_DATA['has_fishing_rod']
    @has_fishing_rod.setter
    def has_fishing_rod(self, val): SHARED_DATA['has_fishing_rod'] = val
    
    @property
    def last_work_time(self): return SHARED_DATA['last_work_time']
    @last_work_time.setter
    def last_work_time(self, val): SHARED_DATA['last_work_time'] = val

    @property
    def maggot_battle_times(self): return SHARED_DATA['maggot_battle_times']
    @maggot_battle_times.setter
    def maggot_battle_times(self, val): SHARED_DATA['maggot_battle_times'] = val

    @property
    def is_house_visible(self): return SHARED_DATA.get('is_house_visible', True)
    @is_house_visible.setter
    def is_house_visible(self, val): SHARED_DATA['is_house_visible'] = val

    @property
    def house_type(self): return SHARED_DATA['house_type']
    @house_type.setter
    def house_type(self, val): SHARED_DATA['house_type'] = val

    @property
    def mortgage_total_periods(self): return SHARED_DATA['mortgage_total_periods']
    @mortgage_total_periods.setter
    def mortgage_total_periods(self, val): SHARED_DATA['mortgage_total_periods'] = val

    @property
    def mortgage_paid_periods(self): return SHARED_DATA['mortgage_paid_periods']
    @mortgage_paid_periods.setter
    def mortgage_paid_periods(self, val): SHARED_DATA['mortgage_paid_periods'] = val

    @property
    def mortgage_daily_amount(self): return SHARED_DATA['mortgage_daily_amount']
    @mortgage_daily_amount.setter
    def mortgage_daily_amount(self, val): SHARED_DATA['mortgage_daily_amount'] = val

    @property
    def last_mortgage_date(self): return SHARED_DATA['last_mortgage_date']
    @last_mortgage_date.setter
    def last_mortgage_date(self, val): SHARED_DATA['last_mortgage_date'] = val


    @property
    def base_state(self):
        return "box" if getattr(self, 'is_boxed', False) else "idle"

    @property
    def age(self):
        import time
        return int((time.time() - getattr(self, 'birth_timestamp', time.time())) / 3600)

    def __init__(self, pet_data=None):


        super().__init__()
        
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint
        if platform.system() == "Windows":
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 兼容 PyInstaller 打包后的路径
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_dir = os.path.join(base_dir, "ui", "白色猫猫鲨")
        
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setStyleSheet("background: transparent; border: none;") 
        
        self.pet_size = 120 
        self.resize(self.pet_size, self.pet_size)
        self.label.resize(self.pet_size, self.pet_size)
        
        self.state = self.base_state
        self.is_dragging = False
        self.drag_offset = QPoint()
        self.gravity = 2.0  
        self.velocity_y = 0 
        self.ground_y = 0   
        self.direction = -1
        self.hit_count = 0
        self.fly_vx = 0
        self.fly_vy = 0
        self.mom_window = None
        self.chat_window = None
        self.gomoku_window = None
        self.maggot_battle_window = None
        
        # 好感度与生命值系统
        pet_data = pet_data or {}
        self.affection = pet_data.get('affection', 50)
        self.hp = pet_data.get('hp', 60)
        self.last_hp_gain_time = pet_data.get('last_hp_gain_time', 0.0)
        
        import time
        self.fishing_times = pet_data.get('fishing_times', [])
        self.birth_timestamp = pet_data.get('birth_timestamp', time.time())
        self.is_egg = pet_data.get('is_egg', False)
        self.has_reproduced = pet_data.get('has_reproduced', False)
        self.is_boxed = pet_data.get('is_boxed', False)
        self.is_sterilized = pet_data.get('is_sterilized', False)
        self.pet_name = pet_data.get('pet_name', "猫猫鲨")
        self.has_named = pet_data.get('has_named', False)
        self.egg_clicks = 0
        self.last_gym_time = pet_data.get('last_gym_time', 0.0)
        self.last_drain_time = pet_data.get('last_drain_time', time.time())
        self.love_target = None
        
        if self.is_egg:
            self.state = "egg"
            
        self.fish_clicks = 0
        self.fish_timer = QTimer(self)
        self.fish_timer.timeout.connect(self.fish_timeout)
        self.fish_timer.setSingleShot(True)
        
        # 实用助手定时器
        self.bath_times = []
        self.reminders = []
        import time
        self.spontaneous_timer = QTimer(self)
        self.spontaneous_timer.timeout.connect(self.trigger_spontaneous_chat)
        self.spontaneous_timer.start(1800000)
        self.has_given_flower = False
        self.flower_stage = 0  # 0: 未触发, 1: 跑出去, 2: 跑回来
        self.flower_target_x = 0

        # 初始化音效系统
        self.audio_dir = os.path.join(base_dir, "audio")
        
        self.sound_eat = QSoundEffect()
        self.sound_eat.setSource(QUrl.fromLocalFile(os.path.join(self.audio_dir, "eat.wav")))
        self.sound_eat.setVolume(0.5)
        
        self.sound_hit = QSoundEffect()
        self.sound_hit.setSource(QUrl.fromLocalFile(os.path.join(self.audio_dir, "hit.wav")))
        self.sound_hit.setVolume(0.6)
        
        self.sound_mom = QSoundEffect()
        self.sound_mom.setSource(QUrl.fromLocalFile(os.path.join(self.audio_dir, "mom.wav")))
        self.sound_mom.setVolume(0.8)
        
        self.ai_timer = QTimer(self)
        self.ai_timer.timeout.connect(self.random_action)
        self.ai_timer.start(4000) 
        
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self.game_loop)
        self.physics_timer.start(16) 
        
        self.init_position()
        self.update_image()

    def save_data(self):
        try:
            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            save_file = os.path.join(base_dir, "save.json")
            
            pets_data = []
            for p in ALL_PETS:
                pets_data.append({
                    'affection': p.affection,
                    'hp': p.hp,
                    'last_hp_gain_time': p.last_hp_gain_time,
                    'fishing_times': getattr(p, 'fishing_times', []),
                    'is_egg': getattr(p, 'is_egg', False),
                    'has_reproduced': getattr(p, 'has_reproduced', False),
                    'pet_name': getattr(p, 'pet_name', "猫猫鲨"),
                    'has_named': getattr(p, 'has_named', False),
                    'birth_timestamp': getattr(p, 'birth_timestamp', __import__('time').time()),
                    'is_boxed': getattr(p, 'is_boxed', False),
                    'is_sterilized': getattr(p, 'is_sterilized', False),
                    'last_gym_time': getattr(p, 'last_gym_time', 0.0),
                    'last_drain_time': getattr(p, 'last_drain_time', __import__('time').time())
                })
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'inventory': SHARED_DATA,
                    'pets': pets_data
                }, f)
        except:
            pass

    def change_hp(self, delta):
        if self.hp <= 0: return # 已经死了就不处理了
        self.hp += delta
        self.hp = max(0, min(100, self.hp)) # 假设上限是100
        self.save_data()
        if self.chat_window:
            self.chat_window.update_aff_ui()
            
        if self.hp <= 0:
            self.trigger_death()
        elif self.hp <= 30:
            if self.state != "cry":
                self.state = "cry"
                self.update_image()
        elif self.state == "cry" and self.hp > 30:
            self.state = self.base_state
            self.update_image()

    def trigger_death(self):
        self.state = "die"
        self.update_image()
        self.open_chat()
        self.chat_window.append_msg(self.pet.pet_name, "我再也不喜欢妈妈了！", "#ff4d4d")
        # 3秒后退出程序
        QTimer.singleShot(3000, QApplication.quit)

    def try_gain_hp(self, ignore_cooldown=False):
        if ignore_cooldown:
            self.change_hp(10)
            return

        import time
        now = time.time()
        # 一个小时(3600秒)内只能增加一次生命值，增加10点
        if now - self.last_hp_gain_time >= 3600:
            self.change_hp(10)
            self.last_hp_gain_time = now
            self.save_data()

    def change_affection(self, delta):
        self.affection += delta
        self.affection = max(0, min(100, self.affection))
        self.save_data()
        if self.chat_window:
            self.chat_window.update_aff_ui()
            
        # 触发送花剧情 (只触发一次)
        if self.affection >= 90 and not self.has_given_flower:
            # 使用异步触发，防止被当前的函数（喂食/喝水等）的状态覆盖打断
            QTimer.singleShot(1000, self.trigger_flower_event)

    def bath_pet(self):
        if self.coins < 15:
            self.open_chat()
            self.chat_window.append_msg(self.pet.pet_name, "金币不够啦，妈妈快去打工赚钱！", "#ff4d4d")
            return
        self.coins -= 15
        self.save_data()
        
        self.try_gain_hp()
        import time
        now = time.time()
        self.bath_times = [t for t in getattr(self, 'bath_times', []) if now - t <= 3600]
        self.bath_times.append(now)
        
        self.state = "bath"
        self.update_image()
        
        if len(self.bath_times) >= 3:
            self.change_affection(-5)
            self.trigger_ai_action("妈妈一小时内给你洗了太多次澡，你很不耐烦，觉得皮都要秃了")
        else:
            self.change_affection(2)
            self.trigger_ai_action("妈妈给你洗了个香喷喷的澡，你觉得很舒服")
            
        QTimer.singleShot(4000, self.finish_utility)
        
    def give_water(self):
        if self.coins < 15:
            self.open_chat()
            self.chat_window.append_msg(self.pet.pet_name, "金币不够啦，妈妈快去打工赚钱！", "#ff4d4d")
            return
        self.coins -= 15
        self.save_data()
        
        self.try_gain_hp(ignore_cooldown=True)
        self.state = "drink"
        self.update_image()
        self.change_affection(3)
        self.trigger_ai_action("妈妈刚刚给你喂了水，你咕噜咕噜喝得很开心")
        QTimer.singleShot(4000, self.finish_utility)
        
    def finish_flower_event(self):
        self.state = "flower" # 叼着花停下
        self.update_image()
        self.open_chat()
        self.chat_window.append_msg(self.pet.pet_name, "噔噔噔！宝宝刚才跑出去给妈妈摘了一朵发发！喜欢吗？(๑>◡<๑)", "#ff6699")
        QTimer.singleShot(6000, self.finish_utility)

    def finish_utility(self):
        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed", "exercise", "sterilization"]:
            self.state = self.base_state
            self.update_image()

    def buy_item(self, item_name, price):
        if self.coins >= price:
            self.coins -= price
            if item_name == "fish": 
                self.fish_count += 1
                msg = "买到了好吃的小鱼干！"
            elif item_name == "water": 
                self.water_count += 1
                msg = "买到了解渴的水瓶！"
            elif item_name == "shampoo": 
                self.shampoo_count += 1
                msg = "买到了香香的沐浴露！"
            elif item_name == "fishing_rod": 
                self.has_fishing_rod = True
                msg = "买到了神奇的鱼竿！"
            self.save_data()
            if self.chat_window: self.chat_window.update_aff_ui()
            self.open_chat()
            self.chat_window.append_msg("系统", msg, "#ff6699")
        else:
            self.open_chat()
            self.chat_window.append_msg("系统", "金币不足，快去打工赚钱吧！", "#ff4d4d")

    def work_pet(self):
        if self.hp <= 0: return
        self.state = "working"
        self.update_image()
        # 打工过程持续3秒
        QTimer.singleShot(3000, self.finish_working)

    def finish_working(self):
        import time
        now = time.time()
        self.state = "money"
        self.update_image()
        self.coins += 35
        
        # 1小时内重复打工会有惩罚
        if now - self.last_work_time < 3600:
            self.change_hp(-15)
            self.change_affection(-15)
            if self.hp > 0:
                self.open_chat()
                self.chat_window.append_msg(self.pet_name, "连续打工太累了！拿命换来了35个金币，扣除了15点生命和好感！", "#ff4d4d")
        else:
            self.open_chat()
            self.chat_window.append_msg(self.pet_name, "打工完成！努力赚钱养家！赚到了35个金币！", "#0066cc")
            
        self.last_work_time = now
        self.save_data()
        if self.chat_window: self.chat_window.update_aff_ui()
        QTimer.singleShot(3000, self.finish_utility)

    def fish_pet(self):
        if not self.has_fishing_rod or self.hp <= 0: return
        
        import time
        now = time.time()
        self.fishing_times = [t for t in getattr(self, 'fishing_times', []) if now - t < 3600]
        if len(self.fishing_times) >= 3:
            self.open_chat()
            self.chat_window.append_msg(self.pet.pet_name, "鱼竿好像有点烫手...休息一下再钓吧（1小时最多3次）！", "#ff4d4d")
            return
            
        self.fishing_times.append(now)
        self.save_data()
        
        self.state = "fishing"
        self.update_image()
        self.open_chat()
        self.chat_window.append_msg(self.pet.pet_name, "去钓鱼啦！不知道能钓到什么呢...", "#0066cc")
        
        # 10秒后判断是否上钩
        QTimer.singleShot(10000, self.check_fish_bite)

    def check_fish_bite(self):
        if self.state != "fishing": return
        import random
        if random.random() < 0.5:
            self.state = "fish soon"
            self.fish_clicks = 0
            self.update_image()
            self.open_chat()
            self.chat_window.append_msg(self.pet.pet_name, "鱼竿动了！快帮我拉杆！（一分钟内疯狂点击我！）", "#ff4d4d")
            self.fish_timer.start(60000) # 1分钟超时
        else:
            self.open_chat()
            self.chat_window.append_msg(self.pet.pet_name, "等了半天，鱼儿没上钩...收工！", "#888888")
            QTimer.singleShot(2000, self.finish_utility)

    def fish_timeout(self):
        if self.state == "fish soon":
            self.open_chat()
            self.chat_window.append_msg(self.pet.pet_name, "哎呀，力气不够，鱼儿跑掉了！妈妈你点得太慢啦！", "#ff4d4d")
            QTimer.singleShot(2000, self.finish_utility)

    def catch_fish(self):
        if self.state != "fish soon": return
        self.fish_timer.stop()
        import random
        r = random.random()
        
        if r < 0.10:
            self.state = "dragon"
            self.change_affection(10)
            msg = "哇！钓上来一只传说中的龙龙！好棒！+10好感度"
        elif r < 0.20:
            self.state = "whale"
            self.change_affection(10)
            msg = "哇！钓上来一只胖嘟嘟的鲸鲸！+10好感度"
        elif r < 0.25:
            self.state = "Caught a shark"
            msg = "哇！居然把妈妈钓上来了！"
        else:
            self.state = self.base_state
            msg = "嘿咻！钓上来了一只破靴子...什么嘛！"
            
        self.update_image()
        self.open_chat()
        self.chat_window.append_msg(self.pet.pet_name, msg, "#ff6699" if self.state != "idle" else "#888888")
        QTimer.singleShot(5000 if self.state != "idle" else 2000, self.finish_utility)

    def add_reminder(self, delay_ms, text):
        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(lambda: self.trigger_reminder(text, t))
        t.start(delay_ms)
        self.reminders.append(t)
        
    def trigger_reminder(self, text, timer):
        if timer in self.reminders:
            self.reminders.remove(timer)
        self.state = "wanna"
        self.update_image()
        screen_geo = QApplication.primaryScreen().availableGeometry()
        start_x = (screen_geo.width() - self.pet_size) // 2
        start_y = (screen_geo.height() - self.pet_size) // 2
        self.move(start_x, start_y)
        self.open_chat()
        self.chat_window.append_msg(self.pet.pet_name, f"叮叮叮！妈妈你让我提醒你的时间到啦：【{text}】！快去快去！", "#ff6699", "#ffe6f2", "⏰")
        QTimer.singleShot(8000, self.finish_utility)

    def trigger_ai_action(self, situation):
        self.open_chat()
        prompt = f"【系统事件】{situation}。请用1句话符合你当前好感度的语气直接对我说出你的反应，就像你真的在经历这件事一样。"
        self.chat_window.generate_autonomous_reply(prompt)

    def trigger_spontaneous_chat(self):
        self.trigger_ai_action("你在桌面上呆了半个小时，觉得有点无聊，主动跟妈妈随便说一句话或者撒个娇")

    def init_position(self):
        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.ground_y = screen_geo.height() - self.pet_size 
        start_x = (screen_geo.width() - self.pet_size) // 2
        start_y = 100 
        self.move(start_x, start_y)


    def trigger_love_in_bed(self):
        self.state = "love in bed"
        self.update_image()
        if self.love_target:
            self.love_target.hide()
        QTimer.singleShot(4000, self.finish_reproduction)

    def finish_reproduction(self):
        self.has_reproduced = True
        if self.love_target:
            self.love_target.has_reproduced = True
            self.love_target.state = self.love_target.base_state
            self.love_target.show()
            self.love_target.move(self.x() + 50, self.y())
            self.love_target.update_image()
            
        self.state = self.base_state
        self.update_image()
        
        import random
        num_eggs = 2 if random.random() < 0.01 else 1
        for _ in range(num_eggs):
            new_pet = CatShark({'is_egg': True})
            new_pet.move(self.x() + random.randint(-50, 50), self.y())
            ALL_PETS.append(new_pet)
            new_pet.show()
            
        self.save_data()
        self.open_chat()
        self.chat_window.append_msg(self.pet.pet_name, "哇！下蛋啦！家里又添新丁了！", "#ff6699")

    def update_image(self):
        img_name = self.state
        if getattr(self, 'is_egg', False):
            img_name = "egg"
        elif self.state in ["walk_left", "walk_right", "walk_to_love"]:
            img_name = "walk"
        elif self.state in ["run_out", "run_in"]:
            img_name = "flower"
        elif self.state in ["climb_left", "climb_right"]:
            img_name = "climb"
        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died", "box", "exercise", "sterilization"]:
            img_name = self.state
        elif self.state == "puberty_bed":
            img_name = "love in bed" 
            
        img_path = os.path.join(self.image_dir, f"{img_name}.png")
        
        if os.path.exists(img_path):
            self.label.clear() 
            pixmap = QPixmap(img_path)
            
            # 核心图片翻转逻辑！
            # 原图假设是朝左的。所以如果 direction == 1 (往右)，就需要翻转
            if self.direction == 1 and self.state in ["walk_left", "walk_right", "run_out", "run_in", "climb_left", "climb_right", "fly", "walk_to_love"]:
                transform = QTransform().scale(-1, 1) 
                pixmap = pixmap.transformed(transform)
                
            # flower 状态(叼着花静止) 时，应该和它跑回来的方向一致
            if self.state == "flower" and self.direction == -1:
                # 如果从右边跑回中间，此时面朝左（原图），不需要翻转；
                # 如果从左边跑回中间，direction是1，需要在下面翻转：
                pass
            elif self.state == "flower" and self.direction == 1:
                transform = QTransform().scale(-1, 1) 
                pixmap = pixmap.transformed(transform)
                
            self.label.setPixmap(pixmap)
        else:
            print(f"等待加入图片: {img_name}.png")
            
    def trigger_flower_event(self):
        self.has_given_flower = True
        self.flower_stage = 1
        self.state = "run_out"
        self.velocity_y = 0 # 取消重力
        # 强制把猫猫鲨拉回地面，防止在半空中乱跑
        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.move(self.x(), self.ground_y)
        
        # 强制关掉聊天框防止卡住
        if self.chat_window:
            self.chat_window.hide()
            
        # 判断离哪边近就往哪边跑
        # 固定向离得近的那一边跑
        if self.x() > screen_geo.width() / 2:
            self.direction = 1 # 往右跑
        else:
            self.direction = -1 # 往左跑
        self.update_image()
        
    def random_action(self):
        if getattr(self, 'is_egg', False): return
        
        # 房贷检查
        import datetime
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if self.last_mortgage_date != today:
            if self.mortgage_paid_periods < self.mortgage_total_periods:
                self.coins -= self.mortgage_daily_amount
                self.mortgage_paid_periods += 1
                self.last_mortgage_date = today
                self.save_data()
                self.open_chat()
                self.chat_window.append_msg("系统", f"【午夜扣款】扣除房贷 {self.mortgage_daily_amount} 金币，当前第 {self.mortgage_paid_periods}/{self.mortgage_total_periods} 期。剩余金币: {self.coins}", "#ff6699")
            else:
                self.last_mortgage_date = today
                self.save_data()
                
        
        # 寿命检查 (100岁死亡)
        if self.hp > 0 and self.age >= 100:
            import random
            self.hp = 0
            self.state = "Variant died" if random.random() < 0.05 else "heaven"
            self.update_image()
            self.save_data()
            if self.chat_window:
                self.chat_window.hide()
            return

        if self.hp <= 0: return
        
        if self.hp <= 30:
            if self.state != "cry":
                self.state = "cry"
                self.update_image()
            return
            
        # 20-40岁偶尔出现 love in bed 动作 (轻微颤抖)
        if 20 <= self.age <= 40 and not getattr(self, 'is_sterilized', False):
            import random
            if random.random() < 0.10:
                self.state = "puberty_bed"
                self.update_image()
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(3000, self.finish_utility)
                return

        if self.affection >= 80 and not getattr(self, 'has_reproduced', False) and not getattr(self, 'is_sterilized', False):
            for other in ALL_PETS:
                if other != self and not getattr(other, 'is_egg', False) and other.affection >= 80 and not getattr(other, 'has_reproduced', False) and not getattr(other, 'is_sterilized', False):
                    # 距离太远的话就去相爱
                    if other.state not in ["walk_to_love", "love", "love in bed"] and self.state not in ["walk_to_love", "love", "love in bed"]:
                        self.state = "walk_to_love"
                        other.state = "walk_to_love"
                        self.love_target = other
                        other.love_target = self
                        return
                        
        if self.affection >= 80 and random.random() < 0.10:
            self.state = "love"
            QTimer.singleShot(3000, self.finish_utility)
            self.update_image()
            return

        if self.is_dragging or (self.y() < self.ground_y and self.state != "fly") or self.state in ["eat", "hit", "angry", "run_out", "run_in", "flower", "bath", "cry", "working", "money", "fishing", "fish soon", "Caught a shark", "dragon", "whale", "hospital", "exercise", "sterilization"]:
            return 
        # 如果气泡开着，乖乖站好
        if self.chat_window and self.chat_window.isVisible():
            self.state = self.base_state
            self.update_image()
            return 
            
        actions = ["idle", "sleep", "walk_left", "walk_right", "wanna", "fly"]
        if self.affection >= 90 and self.hp >= 90:
            # 生命和好感度都大于90时，有一定的几率起飞
            weights = [20, 10, 15, 15, 20, 20]
        elif self.affection < 30:
            # 委屈期：更爱睡觉，不想理你 (没有 wanna)
            weights = [20, 50, 15, 15, 0, 0]
        elif self.affection >= 70:
            # 亲密期：眼冒星星，活跃度增加
            weights = [30, 10, 15, 15, 30, 0]
        else:
            # 正常期
            weights = [40, 20, 15, 15, 10, 0]
        next_action = random.choices(actions, weights=weights)[0]
        
        if next_action == "walk_left":
            self.direction = -1
            self.state = "walk_left"
        elif next_action == "walk_right":
            self.direction = 1  
            self.state = "walk_right"
        elif next_action == "fly":
            self.state = "fly"
            # 随机给一个 X 和 Y 的初速度，起飞！
            self.fly_vx = random.choice([-4, -3, 3, 4])
            self.fly_vy = random.choice([-4, -3, 3, 4])
            self.direction = 1 if self.fly_vx > 0 else -1
        else:
            self.state = next_action
            
        self.update_image()

    def game_loop(self):
        if self.is_dragging:
            return 
            
        current_x = self.x()
        current_y = self.y()
        
        if self.state in ["fish soon", "puberty_bed"]:
            import random
            ox = random.randint(-5, 5) if self.state == "fish soon" else random.randint(-2, 2)
            oy = random.randint(-5, 5) if self.state == "fish soon" else random.randint(-2, 2)
            self.move(current_x + ox, current_y + oy)
            return
            
        if self.state == "walk_to_love" and getattr(self, 'love_target', None):
            target_x = self.love_target.x()
            if abs(current_x - target_x) < 50:
                self.state = "love"
                self.update_image()
                if self.x() <= target_x: # 只让左边的人触发繁殖，避免触发两次
                    QTimer.singleShot(2000, self.trigger_love_in_bed)
            else:
                self.direction = 1 if target_x > current_x else -1
                self.move(current_x + (2 * self.direction), current_y)
                self.update_image()
            return

        # 如果在爬墙，就不受重力影响！
        # 送花和飞行独占控制
        if self.state in ["run_out", "run_in", "fly"]:
            screen_geo = QApplication.primaryScreen().availableGeometry()
            
            if self.state == "fly":
                new_x = current_x + self.fly_vx
                new_y = current_y + self.fly_vy
                
                # 边缘反弹逻辑 (X轴)
                if new_x <= 0:
                    new_x = 0
                    self.fly_vx = abs(self.fly_vx)
                    self.direction = 1
                    self.update_image()
                elif new_x >= screen_geo.width() - self.pet_size:
                    new_x = screen_geo.width() - self.pet_size
                    self.fly_vx = -abs(self.fly_vx)
                    self.direction = -1
                    self.update_image()
                    
                # 边缘反弹逻辑 (Y轴)
                if new_y <= 0:
                    new_y = 0
                    self.fly_vy = abs(self.fly_vy)
                elif new_y >= self.ground_y:
                    new_y = self.ground_y
                    self.fly_vy = -abs(self.fly_vy)
                    
                self.move(new_x, new_y)
                # 如果正开着聊天框，气泡也跟着飞
                if self.chat_window and self.chat_window.isVisible():
                    self.chat_window.update_position()
                return

            speed = 5 # 跑快点
            if self.state == "run_out":
                if self.direction == 1:
                    new_x = current_x + speed
                    if new_x > screen_geo.width() - 20: # 同样不要完全出屏幕
                        self.state = "run_in"
                        self.direction = -1 # 调头跑回来
                        self.flower_target_x = screen_geo.width() // 2 # 跑到屏幕中间
                        self.update_image()
                else:
                    new_x = current_x - speed
                    # 改为只要超过边缘一点就跑回来，别等它完全出屏幕，容易卡住
                    if new_x < -20: 
                        self.state = "run_in"
                        self.direction = 1
                        self.flower_target_x = screen_geo.width() // 2
                        self.update_image()
                self.move(new_x if 'new_x' in locals() else current_x, current_y)
            elif self.state == "run_in":
                # 跑回目标位置
                if self.direction == 1:
                    new_x = current_x + speed
                    if new_x >= self.flower_target_x:
                        new_x = self.flower_target_x
                        self.finish_flower_event()
                else:
                    new_x = current_x - speed
                    if new_x <= self.flower_target_x:
                        new_x = self.flower_target_x
                        self.finish_flower_event()
                self.move(new_x, current_y)
            return

        if current_y < self.ground_y and self.state not in ["climb_left", "climb_right"]:
            self.velocity_y += self.gravity
            new_y = current_y + int(self.velocity_y)
            
            if new_y > self.ground_y: 
                new_y = self.ground_y
                self.velocity_y = 0 
                if self.state == "drag":
                    self.state = self.base_state
                    self.update_image()
            self.move(current_x, new_y)
            if self.chat_window and self.chat_window.isVisible():
                self.chat_window.update_position()
            return 
            
        if self.state == "walk_left":
            new_x = current_x - 2 
            if new_x <= 0:
                new_x = 0
                self.state = "climb_left"
                self.direction = -1
                self.update_image()
            self.move(new_x, current_y)
            
        elif self.state == "walk_right":
            new_x = current_x + 2 
            screen_width = QApplication.primaryScreen().availableGeometry().width()
            if new_x >= screen_width - self.pet_size:
                new_x = screen_width - self.pet_size
                self.state = "climb_right"
                self.direction = 1
                self.update_image()
            self.move(new_x, current_y)
            
        elif self.state in ["climb_left", "climb_right"]:
            new_y = current_y - 2
            if new_y <= 0: # 爬到屏幕顶部了，松手掉下来
                self.state = self.base_state
                self.update_image()
            self.move(current_x, new_y)
            
        elif self.state in ["flower", "drink", "bath"]:
            pass # 静止不动

    def hit_pet(self):
        if self.hp <= 0: return
        self.hit_count += 1
        self.change_hp(-10)
        if self.hp <= 0: return # 已经被打死了，不继续后面的挨打动画
        
        self.change_affection(-10)
        self.state = "hit"
        self.update_image()
        if os.path.exists(os.path.join(self.audio_dir, "hit.wav")):
            self.sound_hit.play()
            
        if self.hit_count >= 3:
            self.hit_count = 0
            self.trigger_ai_action("妈妈居然连续打你，你彻底发怒了，喊出了巨大的妈妈")
            QTimer.singleShot(500, self.show_angry_and_mom)
        else:
            self.trigger_ai_action("妈妈打了你一下，你觉得很委屈很生气")
            QTimer.singleShot(500, self.show_angry)
            
    def show_angry(self):
        self.state = "angry"
        self.update_image()
        QTimer.singleShot(2500, self.finish_angry)
        
    def show_angry_and_mom(self):
        self.state = "angry"
        self.update_image()
        
        # 召唤 Mom
        if os.path.exists(os.path.join(self.audio_dir, "mom.wav")):
            self.sound_mom.play()
        self.mom_window = MomShark(self.image_dir)
        self.mom_window.show()
        
        QTimer.singleShot(5000, self.finish_angry)
        
    def finish_angry(self):
        if self.state == "angry":
            self.state = self.base_state
            self.update_image()

    def feed_pet(self):
        if self.coins < 15:
            self.open_chat()
            self.chat_window.append_msg(self.pet.pet_name, "金币不够啦，妈妈快去打工赚钱！", "#ff4d4d")
            return
        self.coins -= 15
        self.save_data()
        
        self.try_gain_hp(ignore_cooldown=True)
        self.change_affection(5)
        self.state = "eat"
        if os.path.exists(os.path.join(self.audio_dir, "eat.wav")):
            self.sound_eat.play()
        self.update_image()
        self.trigger_ai_action("妈妈刚刚给你喂了好吃的小鱼干，你非常开心")
        QTimer.singleShot(3000, self.finish_eating) # 3秒后吃完
        
    def finish_eating(self):
        # 只有在乖乖吃东西时才切回idle，如果是跑去送花了，千万别切回idle！
        if self.state == "eat":
            self.state = self.base_state
            self.update_image()
            
    def open_chat(self):
        if self.chat_window is None:
            self.chat_window = ChatWindow(self)
            
        # 只有在走路或发呆时打开聊天，才强制停下（切到 idle）。
        # 如果正在喝水(drink)、洗澡(bath)、送花(flower)、挨打(hit)等特殊动画中，绝对不能强切 idle！
        if self.state in ["walk_left", "walk_right", "climb_left", "climb_right", "run_out", "run_in", "idle"]:
            self.state = self.base_state 
            self.update_image()
            
        self.chat_window.show()
        self.chat_window.update_position()
        self.chat_window.raise_()
        self.chat_window.activateWindow()

    def open_gomoku(self):
        if self.hp <= 0:
            return

        if self.gomoku_window is None:
            self.gomoku_window = GomokuWindow(self)

        self.gomoku_window.show()
        self.gomoku_window.raise_()
        self.gomoku_window.activateWindow()
        self.gomoku_window.update_coin_label()

    def fight_maggot(self):
        if self.hp <= 0:
            return

        import time
        now = time.time()

        if self.coins < 15:
            self.open_chat()
            self.chat_window.append_msg("系统", "金币不够，迎战蛆蛆要先花 15 金币购买装备鲨鲨。", "#ff4d4d")
            return

        self.coins -= 15
        self.save_data()

        if self.chat_window:
            self.chat_window.update_aff_ui()
            self.chat_window.hide()

        self.hide()
        self.maggot_battle_window = MaggotBattleWindow(self)
        self.maggot_battle_window.start()

    def buy_house(self):
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        items = ["简陋房子 (0金币)", "普通房子 (1000金币)", "豪华房子 (10000金币)"]
        item, ok = QInputDialog.getItem(self, "购买房子", "请选择你要购买的房子：", items, 0, False)
        if not ok or not item: return
        
        target_type = 0
        price = 0
        max_periods = 0
        if "普通房子" in item:
            target_type = 1
            price = 1000
            max_periods = 20
        elif "豪华房子" in item:
            target_type = 2
            price = 10000
            max_periods = 50
            
        if self.house_type >= target_type and target_type != 0:
            self.open_chat()
            self.chat_window.append_msg("系统", "你已经有同样好或者更好的房子了，不需要降级哦！", "#ff4d4d")
            return
            
        if target_type == 0:
            self.house_type = 0
            self.mortgage_total_periods = 0
            self.mortgage_paid_periods = 0
            self.mortgage_daily_amount = 0
            self.save_data()
            if GLOBAL_HOUSE: GLOBAL_HOUSE.update_house()
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "我们搬到简陋的房子里啦，要努力赚钱哦！", "#0066cc")
            return

        reply = QMessageBox.question(self, "分期付款", f"{item} 可以分期付款（每天1期）。是否分期？", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        periods = 1
        if reply == QMessageBox.StandardButton.Yes:
            periods, ok = QInputDialog.getInt(self, "分期期数", f"请输入分期期数 (2-{max_periods})：", 2, 2, max_periods)
            if not ok: return
            
        daily_amount = price // periods
        down_payment = daily_amount # 首付就是第一期的钱
        
        if self.coins < down_payment:
            self.open_chat()
            self.chat_window.append_msg("系统", f"金币不足！首付需要 {down_payment} 金币！", "#ff4d4d")
            return
            
        self.coins -= down_payment
        self.house_type = target_type
        self.mortgage_total_periods = periods
        self.mortgage_paid_periods = 1
        self.mortgage_daily_amount = daily_amount
        import datetime
        self.last_mortgage_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.save_data()
        if GLOBAL_HOUSE: GLOBAL_HOUSE.update_house()
        
        if self.chat_window: self.chat_window.update_aff_ui()
        self.open_chat()
        if periods > 1:
            self.chat_window.append_msg("系统", f"恭喜购买新房！已扣除首付 {down_payment} 金币。接下来还要还 {periods - 1} 天房贷，每天 {daily_amount} 金币哦！", "#ff6699")
        else:
            self.chat_window.append_msg("系统", f"全款拿下新房！花费 {price} 金币，大佬大气！", "#ff6699")

    def buy_egg(self):
        if self.coins >= 500:
            self.coins -= 500
            self.save_data()
            new_pet = CatShark({'is_egg': True})
            new_pet.move(self.x() + 50, self.y())
            ALL_PETS.append(new_pet)
            new_pet.show()
            self.open_chat()
            self.chat_window.append_msg("系统", "买到了一个猫猫鲨蛋！多抚摸它哦！", "#ff6699")
        else:
            self.open_chat()
            self.chat_window.append_msg("系统", "金币不足！猫猫鲨蛋需要500金币！", "#ff4d4d")

    def go_hospital(self):
        if getattr(self, 'is_egg', False) or self.hp <= 0: return
        if self.coins >= 100:
            self.coins -= 100
            self.change_hp(50)
            self.save_data()
            if self.chat_window: self.chat_window.update_aff_ui()
            self.state = "hospital"
            self.update_image()
            self.open_chat()
            self.chat_window.append_msg("系统", "在医院接受了治疗，恢复了50点生命值！", "#ff6699")
            QTimer.singleShot(4000, self.finish_utility)
        else:
            self.open_chat()
            self.chat_window.append_msg("系统", "金币不足100，看不起病！快去打工赚钱吧！", "#ff4d4d")



    def toggle_box_status(self):
        self.is_boxed = not getattr(self, 'is_boxed', False)
        self.state = self.base_state
        self.update_image()
        self.save_data()

    def toggle_house_visibility(self):
        self.is_house_visible = not self.is_house_visible
        self.save_data()
        if GLOBAL_HOUSE:
            GLOBAL_HOUSE.update_house()

    def rename_pet(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "起名", "给你的猫猫鲨宝宝起个名字吧：")
        if ok and name.strip():
            self.pet_name = name.strip()
            self.has_named = True
            self.save_data()
            if self.chat_window:
                self.chat_window.messages[0]["content"] = self.chat_window.get_system_prompt()
            self.open_chat()
            self.chat_window.append_msg(self.pet_name, f"喵呜！我以后就叫 {self.pet_name} 啦！", "#ff6699")


    def sterilize_pet(self):
        if getattr(self, 'is_egg', False) or self.hp <= 0 or getattr(self, 'is_sterilized', False): return
        if self.coins >= 200:
            self.coins -= 200
            self.save_data()
            if self.chat_window: self.chat_window.update_aff_ui()
            self.state = "sterilization"
            self.update_image()
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "喵？医生拿着剪刀走过来了...妈妈你想干嘛！救命啊！", "#ff4d4d")
            
            # Fade to black animation
            from PyQt6.QtWidgets import QGraphicsColorizeEffect
            from PyQt6.QtCore import QPropertyAnimation
            from PyQt6.QtGui import QColor
            self.color_effect = QGraphicsColorizeEffect(self.label)
            self.color_effect.setColor(QColor("black"))
            self.color_effect.setStrength(0.0)
            self.label.setGraphicsEffect(self.color_effect)
            
            self.fade_anim = QPropertyAnimation(self.color_effect, b"strength")
            self.fade_anim.setDuration(3000) # 3秒慢慢变黑
            self.fade_anim.setStartValue(0.0)
            self.fade_anim.setEndValue(1.0)
            self.fade_anim.finished.connect(self.finish_sterilization)
            self.fade_anim.start()
        else:
            self.open_chat()
            self.chat_window.append_msg("系统", "金币不足200，连绝育的手术费都不够！", "#ff4d4d")

    def finish_sterilization(self):
        self.label.setGraphicsEffect(None) # 恢复正常
        self.is_sterilized = True
        self.change_affection(-50)
        self.save_data()
        self.open_chat()
        self.chat_window.append_msg("猫猫鲨", "我...我感觉身体里少了点什么...妈妈大坏蛋！再也不理你了！", "#ff4d4d")
        if self.chat_window and len(self.chat_window.messages) > 0:
            self.chat_window.messages[0]["content"] = self.chat_window.get_system_prompt()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(4000, self.finish_utility)

    def go_gym(self):
        if getattr(self, 'is_egg', False) or self.hp <= 0: return
        
        import time
        now = time.time()
        if now - getattr(self, 'last_gym_time', 0.0) < 3600:
            self.open_chat()
            self.chat_window.append_msg("系统", "刚去过健身房，肌肉还在酸痛呢，休息1小时再去吧！", "#ff4d4d")
            return
            
        if self.coins >= 30:
            self.coins -= 30
            self.change_hp(15)
            self.change_affection(10)
            self.last_gym_time = now
            self.save_data()
            if self.chat_window: self.chat_window.update_aff_ui()
            self.state = "exercise"
            self.update_image()
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "呼呼...在健身房挥洒汗水！健康+15，快乐+10！", "#0066cc")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(4000, self.finish_utility)
        else:
            self.open_chat()
            self.chat_window.append_msg("系统", "金币不足30，连健身房的门卡都办不起！", "#ff4d4d")

    def contextMenuEvent(self, event):
        if self.hp <= 0 and self.state in ["heaven", "Variant died", "die"]: return
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: white; border-radius: 5px; padding: 5px; } QMenu::item { padding: 5px 20px; } QMenu::item:selected { background-color: #f0f0f0; border-radius: 3px; }")
        
        shop_menu = menu.addMenu("商店 🛒")
        care_menu = menu.addMenu("照顾猫猫鲨 💗")
        money_menu = menu.addMenu("获取钱钱 💰")
        
        # 绑定商店功能
        shop_menu.addAction("买房子 🏠", self.buy_house)
        shop_menu.addAction("猫猫鲨蛋 (500金币)", self.buy_egg)
        if not self.has_fishing_rod:
            shop_menu.addAction("鱼竿 (200金币)", lambda i="fishing_rod", p=200: self.buy_item(i, p))
        else:
            shop_menu.addAction("鱼竿 (已拥有)", lambda: None).setEnabled(False)

        # 绑定照顾功能
        care_menu.addAction("喂食 🐟 (15金币)", self.feed_pet)
        care_menu.addAction("喂水 💧 (15金币)", self.give_water)
        care_menu.addAction("洗白白 🛁 (15金币)", self.bath_pet)
        care_menu.addAction("去医院 🏥 (100金币)", self.go_hospital)
        if not getattr(self, 'is_sterilized', False):
            care_menu.addAction("绝育手术 ✂️ (200金币)", self.sterilize_pet)
        care_menu.addAction("去健身房 🏋️ (30金币)", self.go_gym)

        # 绑定赚钱功能
        money_menu.addAction("打工赚钱 💻", self.work_pet)
        money_menu.addAction("对战五子棋 ♟️", self.open_gomoku)
        money_menu.addAction("迎战蛆蛆 🪱", self.fight_maggot)

        # 绑定日常功能
        if getattr(self, 'is_boxed', False):
            menu.addAction("出纸箱 🐈", self.toggle_box_status)
        else:
            menu.addAction("进纸箱 📦", self.toggle_box_status)
            
        if self.is_house_visible:
            menu.addAction("隐藏房子 🏠", self.toggle_house_visibility)
        else:
            menu.addAction("显示房子 🏠", self.toggle_house_visibility)
            
        if not self.has_named:
            menu.addAction("给宝宝起名 🏷️", self.rename_pet)
        if self.has_fishing_rod:
            menu.addAction("去钓鱼 🎣", self.fish_pet)
            
        menu.addAction("聊天 💬", self.open_chat)
        menu.addAction("打猫猫鲨 🥊", self.hit_pet)
        menu.addAction("退出 ❌", QApplication.quit)
        
        menu.exec(event.globalPos())

    def mousePressEvent(self, event):
        if self.hp <= 0 and self.state in ["die", "heaven", "Variant died"]: return
        if self.is_egg:
            if event.button() == Qt.MouseButton.LeftButton:
                self.egg_clicks = getattr(self, 'egg_clicks', 0) + 1
                if self.egg_clicks >= 10:
                    self.is_egg = False
                    self.state = "birth"
                    self.update_image()
                    QTimer.singleShot(3000, self.finish_utility)
                    self.save_data()
                    
                    # 刚出生时自动弹窗起名
                    QTimer.singleShot(3500, self.rename_pet)
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state == "fish soon":
                self.fish_clicks += 1
                if self.fish_clicks >= 10:
                    self.catch_fish()
                event.accept()
                return
                
            self.is_dragging = True
            self.state = "drag" 
            self.update_image()
            self.velocity_y = 0 
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            if self.chat_window and self.chat_window.isVisible():
                self.chat_window.update_position()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            # 高空坠落检测: 距离地面超过 100 像素
            if self.y() < self.ground_y - 100:
                self.change_hp(-5)
                if self.hp <= 0: return # 摔死了
                self.change_affection(-1)
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    save_file = os.path.join(base_dir, "save.json")
    
    pets_data = []
    if os.path.exists(save_file):
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'pets' in data:
                    SHARED_DATA.update(data.get('inventory', {}))
                    pets_data = data.get('pets', [])
                else:
                    SHARED_DATA['coins'] = data.get('coins', 0)
                    SHARED_DATA['fish_count'] = data.get('fish_count', 0)
                    SHARED_DATA['water_count'] = data.get('water_count', 0)
                    SHARED_DATA['shampoo_count'] = data.get('shampoo_count', 0)
                    SHARED_DATA['has_fishing_rod'] = data.get('has_fishing_rod', False)
                    SHARED_DATA['last_work_time'] = data.get('last_work_time', 0.0)
                    SHARED_DATA['maggot_battle_times'] = data.get('maggot_battle_times', [])
                    SHARED_DATA['house_type'] = data.get('house_type', 0)
                    SHARED_DATA['mortgage_total_periods'] = data.get('mortgage_total_periods', 0)
                    SHARED_DATA['mortgage_paid_periods'] = data.get('mortgage_paid_periods', 0)
                    SHARED_DATA['mortgage_daily_amount'] = data.get('mortgage_daily_amount', 0)
                    SHARED_DATA['last_mortgage_date'] = data.get('last_mortgage_date', '')
                    pets_data = [data]
        except:
            pass
            
    alive_pets_data = []
    for pd in pets_data:
        if pd.get('hp', 60) > 0:
            alive_pets_data.append(pd)

    if alive_pets_data:
        pets_data = alive_pets_data
    else:
        pets_data = [{}]
        
    for pd in pets_data:
        pet = CatShark(pd)
        ALL_PETS.append(pet)
        pet.show()
        
    GLOBAL_HOUSE = HouseWidget(os.path.join(base_dir, "ui", "白色猫猫鲨"))
        
    sys.exit(app.exec())
