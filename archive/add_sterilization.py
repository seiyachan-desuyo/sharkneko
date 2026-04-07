import os

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. __init__ property
init_old = "        self.is_boxed = pet_data.get('is_boxed', False)"
init_new = "        self.is_boxed = pet_data.get('is_boxed', False)\n        self.is_sterilized = pet_data.get('is_sterilized', False)"
content = content.replace(init_old, init_new)

# 2. save_data
save_old = "                    'is_boxed': getattr(p, 'is_boxed', False),"
save_new = "                    'is_boxed': getattr(p, 'is_boxed', False),\n                    'is_sterilized': getattr(p, 'is_sterilized', False),"
content = content.replace(save_old, save_new)

# 3. System Prompt
sys_old = "妈妈目前没有房贷压力。'}"
sys_new = "妈妈目前没有房贷压力。'}\n\" + (\"\\n【特别注意】：你已经被妈妈无情地带去医院做了绝育手术！你失去了繁衍后代的能力。你对此感到非常难过、幽怨和记仇，时不时要阴阳怪气妈妈剥夺了你的权利。\" if getattr(self.pet, \"is_sterilized\", False) else \"\")"
content = content.replace(sys_old, sys_new)

# 4. random_action (puberty_bed & walk_to_love)
ra_love_old = "if self.affection >= 80 and not getattr(self, 'has_reproduced', False):"
ra_love_new = "if self.affection >= 80 and not getattr(self, 'has_reproduced', False) and not getattr(self, 'is_sterilized', False):"
content = content.replace(ra_love_old, ra_love_new)

ra_puberty_old = "if 20 <= self.age <= 40:"
ra_puberty_new = "if 20 <= self.age <= 40 and not getattr(self, 'is_sterilized', False):"
content = content.replace(ra_puberty_old, ra_puberty_new)

ra_other_old = "if other != self and not getattr(other, 'is_egg', False) and other.affection >= 80 and not getattr(other, 'has_reproduced', False):"
ra_other_new = "if other != self and not getattr(other, 'is_egg', False) and other.affection >= 80 and not getattr(other, 'has_reproduced', False) and not getattr(other, 'is_sterilized', False):"
content = content.replace(ra_other_old, ra_other_new)

# 5. Methods
gym_func = "    def go_gym(self):"
sterilize_func = """    def sterilize_pet(self):
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

    def go_gym(self):"""
content = content.replace(gym_func, sterilize_func)

# 6. Menus
menu_old = 'care_menu.addAction("去医院 🏥 (100金币)", self.go_hospital)'
menu_new = 'care_menu.addAction("去医院 🏥 (100金币)", self.go_hospital)\n        if not getattr(self, \'is_sterilized\', False):\n            care_menu.addAction("绝育手术 ✂️ (200金币)", self.sterilize_pet)'
content = content.replace(menu_old, menu_new)

# 7. Lists (finish_utility, image, drag)
fu_old = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed", "exercise"]:'
fu_new = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed", "exercise", "sterilization"]:'
content = content.replace(fu_old, fu_new)

drag_old = '        if self.is_dragging or (self.y() < self.ground_y and self.state != "fly") or self.state in ["eat", "hit", "angry", "run_out", "run_in", "flower", "bath", "cry", "working", "money", "fishing", "fish soon", "Caught a shark", "dragon", "whale", "hospital", "exercise"]:'
drag_new = '        if self.is_dragging or (self.y() < self.ground_y and self.state != "fly") or self.state in ["eat", "hit", "angry", "run_out", "run_in", "flower", "bath", "cry", "working", "money", "fishing", "fish soon", "Caught a shark", "dragon", "whale", "hospital", "exercise", "sterilization"]:'
content = content.replace(drag_old, drag_new)

img_old = '        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died", "box", "exercise"]:'
img_new = '        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died", "box", "exercise", "sterilization"]:'
content = content.replace(img_old, img_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Sterilization added!")
