import os

with open('/Users/seiya/Desktop/猫猫鲨/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add SHARED_DATA and ALL_PETS
shared_decl = """
SHARED_DATA = {
    'coins': 0, 'fish_count': 0, 'water_count': 0, 'shampoo_count': 0,
    'has_fishing_rod': False, 'last_work_time': 0.0
}
ALL_PETS = []

# ================= 桌宠本体 =================
"""
content = content.replace("# ================= 桌宠本体 =================", shared_decl)

# 2. Add properties to CatShark
props = """
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

    def __init__(self, pet_data=None):
"""
content = content.replace("class CatShark(QWidget):\n    def __init__(self):", props)

# 3. Replace __init__ variable declarations
init_old = """        # 好感度与生命值系统
        self.affection = 50
        self.hp = 60
        self.last_hp_gain_time = 0.0
        
        # 金钱与商店系统
        self.coins = 0
        self.fish_count = 0
        self.water_count = 0
        self.shampoo_count = 0
        self.has_fishing_rod = False
        self.last_work_time = 0.0
        
        self.fishing_times = []
        self.fish_clicks = 0
        self.fish_timer = QTimer(self)
        self.fish_timer.timeout.connect(self.fish_timeout)
        self.fish_timer.setSingleShot(True)
        
        self.save_file = os.path.join(base_dir, "save.json")
        self.load_data()"""

init_new = """        # 好感度与生命值系统
        pet_data = pet_data or {}
        self.affection = pet_data.get('affection', 50)
        self.hp = pet_data.get('hp', 60)
        self.last_hp_gain_time = pet_data.get('last_hp_gain_time', 0.0)
        
        self.fishing_times = pet_data.get('fishing_times', [])
        self.is_egg = pet_data.get('is_egg', False)
        self.has_reproduced = pet_data.get('has_reproduced', False)
        self.egg_clicks = 0
        self.love_target = None
        
        if self.is_egg:
            self.state = "egg"
            
        self.fish_clicks = 0
        self.fish_timer = QTimer(self)
        self.fish_timer.timeout.connect(self.fish_timeout)
        self.fish_timer.setSingleShot(True)"""

content = content.replace(init_old, init_new)

# 4. Replace load_data and save_data
load_save_old_start = "    def load_data(self):"
load_save_old_end = "    def change_hp(self, delta):"

idx_start = content.find(load_save_old_start)
idx_end = content.find(load_save_old_end)

save_new = """    def save_data(self):
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
                    'has_reproduced': getattr(p, 'has_reproduced', False)
                })
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'inventory': SHARED_DATA,
                    'pets': pets_data
                }, f)
        except:
            pass

"""
content = content[:idx_start] + save_new + content[idx_end:]

# 5. random_action
ra_old = """    def random_action(self):
        if self.hp <= 0: return
        if self.hp <= 30:
            if self.state != "cry":
                self.state = "cry"
                self.update_image()
            return"""

ra_new = """    def random_action(self):
        if getattr(self, 'is_egg', False): return
        if self.hp <= 0: return
        if self.hp <= 30:
            if self.state != "cry":
                self.state = "cry"
                self.update_image()
            return
            
        if self.affection >= 80 and not getattr(self, 'has_reproduced', False):
            for other in ALL_PETS:
                if other != self and not getattr(other, 'is_egg', False) and other.affection >= 80 and not getattr(other, 'has_reproduced', False):
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
            return"""
content = content.replace(ra_old, ra_new)

# 6. game_loop for walk_to_love
gl_old = """        if self.state == "fish soon":
            import random
            ox = random.randint(-5, 5)
            oy = random.randint(-5, 5)
            self.move(current_x + ox, current_y + oy)
            return

        # 如果在爬墙，就不受重力影响！"""

gl_new = """        if self.state == "fish soon":
            import random
            ox = random.randint(-5, 5)
            oy = random.randint(-5, 5)
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

        # 如果在爬墙，就不受重力影响！"""
content = content.replace(gl_old, gl_new)

# 7. update_image changes
ui_old = """        if self.state in ["walk_left", "walk_right"]:
            img_name = "walk"
        elif self.state in ["run_out", "run_in"]:"""

ui_new = """        if getattr(self, 'is_egg', False):
            img_name = "egg"
        elif self.state in ["walk_left", "walk_right", "walk_to_love"]:
            img_name = "walk"
        elif self.state in ["run_out", "run_in"]:"""
content = content.replace(ui_old, ui_new)

ui_flip_old = """            if self.direction == 1 and self.state in ["walk_left", "walk_right", "run_out", "run_in", "climb_left", "climb_right", "fly"]:
                transform = QTransform().scale(-1, 1) """
ui_flip_new = """            if self.direction == 1 and self.state in ["walk_left", "walk_right", "run_out", "run_in", "climb_left", "climb_right", "fly", "walk_to_love"]:
                transform = QTransform().scale(-1, 1) """
content = content.replace(ui_flip_old, ui_flip_new)

# 8. Add reproduction methods
repro_code = """
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
            self.love_target.state = "idle"
            self.love_target.show()
            self.love_target.move(self.x() + 50, self.y())
            self.love_target.update_image()
            
        self.state = "idle"
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
        self.chat_window.append_msg("猫猫鲨", "哇！下蛋啦！家里又添新丁了！", "#ff6699")
"""
content = content.replace("    def update_image(self):", repro_code + "\n    def update_image(self):")


# 9. mousePressEvent for egg
mp_old = """    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state == "fish soon":"""

mp_new = """    def mousePressEvent(self, event):
        if getattr(self, 'is_egg', False):
            if event.button() == Qt.MouseButton.LeftButton:
                self.egg_clicks = getattr(self, 'egg_clicks', 0) + 1
                if self.egg_clicks >= 10:
                    self.is_egg = False
                    self.state = "birth"
                    self.update_image()
                    QTimer.singleShot(3000, self.finish_utility)
                    self.save_data()
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.state == "fish soon":"""
content = content.replace(mp_old, mp_new)

# 10. Buy egg in context menu
buy_egg_code = """    def buy_egg(self):
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

    def contextMenuEvent(self, event):"""
content = content.replace("    def contextMenuEvent(self, event):", buy_egg_code)

cm_old = """        # 绑定商店功能
        shop_menu.addAction(f"小鱼干 (15金币) [拥有:{self.fish_count}]", lambda i="fish", p=15: self.buy_item(i, p))"""

cm_new = """        # 绑定商店功能
        shop_menu.addAction("猫猫鲨蛋 (500金币)", self.buy_egg)
        shop_menu.addAction(f"小鱼干 (15金币) [拥有:{self.fish_count}]", lambda i="fish", p=15: self.buy_item(i, p))"""
content = content.replace(cm_old, cm_new)

# 11. finish_utility support love, love in bed, birth
fu_old = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon"]:'
fu_new = '        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed"]:'
content = content.replace(fu_old, fu_new)

# 12. Main execution block
main_old = """if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = CatShark()
    pet.show()
    sys.exit(app.exec())"""

main_new = """if __name__ == '__main__':
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
                    pets_data = [data]
        except:
            pass
            
    if not pets_data:
        pets_data = [{}]
        
    for pd in pets_data:
        pet = CatShark(pd)
        ALL_PETS.append(pet)
        pet.show()
        
    sys.exit(app.exec())"""
content = content.replace(main_old, main_new)

with open('/Users/seiya/Desktop/猫猫鲨/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactor complete.")
