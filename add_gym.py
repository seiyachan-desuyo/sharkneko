import os

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update finish_utility
fu_old = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed"]:'
fu_new = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed", "exercise"]:'
content = content.replace(fu_old, fu_new)

# 2. Add go_gym
gym_code = """
    def go_gym(self):
        if getattr(self, 'is_egg', False) or self.hp <= 0: return
        if self.coins >= 20:
            self.coins -= 20
            self.change_hp(10)
            self.change_affection(10)
            self.save_data()
            if self.chat_window: self.chat_window.update_aff_ui()
            self.state = "exercise"
            self.update_image()
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "呼呼...在健身房挥洒汗水！健康+10，快乐+10！", "#0066cc")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(4000, self.finish_utility)
        else:
            self.open_chat()
            self.chat_window.append_msg("系统", "金币不足20，连健身房的门卡都办不起！", "#ff4d4d")

    def contextMenuEvent(self, event):"""
content = content.replace("    def contextMenuEvent(self, event):", gym_code)

# 3. Add to context menu
menu_old = """        care_menu.addAction("去医院 🏥 (100金币)", self.go_hospital)"""
menu_new = """        care_menu.addAction("去医院 🏥 (100金币)", self.go_hospital)
        care_menu.addAction("去健身房 🏋️ (20金币)", self.go_gym)"""
content = content.replace(menu_old, menu_new)

# 4. Prevent dragging/actions while exercising
drag_old = '        if self.is_dragging or (self.y() < self.ground_y and self.state != "fly") or self.state in ["eat", "hit", "angry", "run_out", "run_in", "flower", "bath", "cry", "working", "money", "fishing", "fish soon", "Caught a shark", "dragon", "whale", "hospital"]:'
drag_new = '        if self.is_dragging or (self.y() < self.ground_y and self.state != "fly") or self.state in ["eat", "hit", "angry", "run_out", "run_in", "flower", "bath", "cry", "working", "money", "fishing", "fish soon", "Caught a shark", "dragon", "whale", "hospital", "exercise"]:'
content = content.replace(drag_old, drag_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Gym feature added")
