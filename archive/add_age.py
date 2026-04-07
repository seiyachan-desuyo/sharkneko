import os

with open('/Users/seiya/Desktop/猫猫鲨/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add age property and birth_timestamp to __init__
props = """
    @property
    def age(self):
        import time
        return int((time.time() - getattr(self, 'birth_timestamp', time.time())) / 1800)

    def __init__(self, pet_data=None):
"""
content = content.replace("    def __init__(self, pet_data=None):", props)

init_old = """        self.fishing_times = pet_data.get('fishing_times', [])
        self.is_egg = pet_data.get('is_egg', False)"""

init_new = """        import time
        self.fishing_times = pet_data.get('fishing_times', [])
        self.birth_timestamp = pet_data.get('birth_timestamp', time.time())
        self.is_egg = pet_data.get('is_egg', False)"""
content = content.replace(init_old, init_new)

# 2. save_data birth_timestamp
save_old = """                    'pet_name': getattr(p, 'pet_name', "猫猫鲨"),
                    'has_named': getattr(p, 'has_named', False)
                })"""
save_new = """                    'pet_name': getattr(p, 'pet_name', "猫猫鲨"),
                    'has_named': getattr(p, 'has_named', False),
                    'birth_timestamp': getattr(p, 'birth_timestamp', __import__('time').time())
                })"""
content = content.replace(save_old, save_new)

# 3. get_aff_text age display
ui_old = """        hp_emoji = "🩸" if hp <= 30 else "❤️"
        return f"💰 {coins}  |  {hp_emoji} 生命: {hp}/100  |  {emoji} 好感度: {aff}/100" """
ui_new = """        hp_emoji = "🩸" if hp <= 30 else "❤️"
        return f"💰 {coins}  |  🎂 {self.pet.age}岁  |  {hp_emoji} 生命: {hp}/100  |  {emoji} 好感度: {aff}/100" """
content = content.replace(ui_old, ui_new)

# 4. get_system_prompt
sys_old = """        return f\"\"\"你是一只超级可爱的猫猫鲨（一半是猫，一半鲨鱼），你的名字叫【{self.pet.pet_name}】。当妈妈叫你这个名字时，你要有反应。你的妈妈是一条笨蛋大鲨鱼（也就是正在和你聊天的用户）。
你目前对妈妈的好感度是 {self.pet.affection}/100，生命值是 {hp}/100。"""
sys_new = """        return f\"\"\"你是一只超级可爱的猫猫鲨（一半是猫，一半鲨鱼），你的名字叫【{self.pet.pet_name}】。当妈妈叫你这个名字时，你要有反应。你的妈妈是一条笨蛋大鲨鱼（也就是正在和你聊天的用户）。
你目前对妈妈的好感度是 {self.pet.affection}/100，生命值是 {hp}/100，年龄是 {self.pet.age} 岁。"""
content = content.replace(sys_old, sys_new)


# 5. random_action logic
ra_old = """    def random_action(self):
        if getattr(self, 'is_egg', False): return
        if self.hp <= 0: return
        if self.hp <= 30:
            if self.state != "cry":
                self.state = "cry"
                self.update_image()
            return
            
        if self.affection >= 80 and not getattr(self, 'has_reproduced', False):"""

ra_new = """    def random_action(self):
        if getattr(self, 'is_egg', False): return
        
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
        if 20 <= self.age <= 40:
            import random
            if random.random() < 0.10:
                self.state = "puberty_bed"
                self.update_image()
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(3000, self.finish_utility)
                return

        if self.affection >= 80 and not getattr(self, 'has_reproduced', False):"""
content = content.replace(ra_old, ra_new)

# 6. game_loop jitter for puberty_bed
gl_old = """        if self.state == "fish soon":
            import random
            ox = random.randint(-5, 5)
            oy = random.randint(-5, 5)
            self.move(current_x + ox, current_y + oy)
            return"""
            
gl_new = """        if self.state in ["fish soon", "puberty_bed"]:
            import random
            ox = random.randint(-5, 5) if self.state == "fish soon" else random.randint(-2, 2)
            oy = random.randint(-5, 5) if self.state == "fish soon" else random.randint(-2, 2)
            self.move(current_x + ox, current_y + oy)
            return"""
content = content.replace(gl_old, gl_new)

# 7. update_image for new states
up_old = """        elif self.state in ["dragon", "whale", "love in bed", "birth", "love"]:
            img_name = self.state"""
up_new = """        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died"]:
            img_name = self.state
        elif self.state == "puberty_bed":
            img_name = "love in bed" """
content = content.replace(up_old, up_new)

# 8. Disable menus / interaction if dead
cm_old = """    def contextMenuEvent(self, event):
        menu = QMenu(self)"""
cm_new = """    def contextMenuEvent(self, event):
        if self.hp <= 0 and self.state in ["heaven", "Variant died", "die"]: return
        menu = QMenu(self)"""
content = content.replace(cm_old, cm_new)

# finish_utility support puberty_bed
fu_old = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital"]:'
fu_new = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed"]:'
content = content.replace(fu_old, fu_new)

# 9. prevent dragging if naturally dead
md_old = """        if self.is_egg:
            if event.button() == Qt.MouseButton.LeftButton:"""
md_new = """        if self.hp <= 0 and self.state in ["die", "heaven", "Variant died"]: return
        if self.is_egg:
            if event.button() == Qt.MouseButton.LeftButton:"""
content = content.replace(md_old, md_new)

with open('/Users/seiya/Desktop/猫猫鲨/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
