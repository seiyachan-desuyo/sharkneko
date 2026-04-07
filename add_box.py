import os

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update load_data / save_data / __init__ for is_boxed
init_old = """        self.is_egg = pet_data.get('is_egg', False)
        self.has_reproduced = pet_data.get('has_reproduced', False)"""

init_new = """        self.is_egg = pet_data.get('is_egg', False)
        self.has_reproduced = pet_data.get('has_reproduced', False)
        self.is_boxed = pet_data.get('is_boxed', False)"""
content = content.replace(init_old, init_new)

init2_old = """        if self.is_egg:
            self.state = "egg" """
init2_new = """        if self.is_egg:
            self.state = "egg"
        elif self.is_boxed:
            self.state = "box" """
content = content.replace(init2_old, init2_new)


save_old = """                    'pet_name': getattr(p, 'pet_name', "猫猫鲨"),
                    'has_named': getattr(p, 'has_named', False),
                    'birth_timestamp': getattr(p, 'birth_timestamp', __import__('time').time())
                })"""

save_new = """                    'pet_name': getattr(p, 'pet_name', "猫猫鲨"),
                    'has_named': getattr(p, 'has_named', False),
                    'birth_timestamp': getattr(p, 'birth_timestamp', __import__('time').time()),
                    'is_boxed': getattr(p, 'is_boxed', False)
                })"""
content = content.replace(save_old, save_new)


# 2. Add box state logic to random_action
ra_old = """    def random_action(self):
        if getattr(self, 'is_egg', False): return
        
        # 寿命检查 (100岁死亡)"""

ra_new = """    def random_action(self):
        if getattr(self, 'is_egg', False): return
        
        if getattr(self, 'is_boxed', False):
            # 只能睡觉或待在纸箱里
            if self.hp <= 0: pass # 下面的死亡逻辑会接管
            elif self.hp <= 30:
                if self.state != "cry":
                    self.state = "cry"
                    self.update_image()
                return
            else:
                import random
                self.state = random.choices(["box", "sleep"], weights=[70, 30])[0]
                self.update_image()
                return
                
        # 寿命检查 (100岁死亡)"""
content = content.replace(ra_old, ra_new)


# 3. Add base_state property to replace finish_utility 'idle'
prop_old = """    @property
    def age(self):"""
prop_new = """    @property
    def base_state(self):
        return "box" if getattr(self, 'is_boxed', False) else "idle"

    @property
    def age(self):"""
content = content.replace(prop_old, prop_new)

# Replace in finish_utility
fu_old = """        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed"]:
            self.state = "idle"
            self.update_image()"""

fu_new = """        if self.state in ["drink", "wanna", "bath", "money", "Caught a shark", "flower", "dragon", "whale", "fishing", "fish soon", "birth", "love", "love in bed", "hospital", "puberty_bed"]:
            self.state = self.base_state
            self.update_image()"""
content = content.replace(fu_old, fu_new)

# other idles in the code
content = content.replace('self.state = "idle"', 'self.state = self.base_state')
content = content.replace('self.love_target.state = "idle"', 'self.love_target.state = self.love_target.base_state')


# 4. Context Menu Toggle Function
toggle_code = """
    def toggle_box_status(self):
        self.is_boxed = not getattr(self, 'is_boxed', False)
        self.state = self.base_state
        self.update_image()
        self.save_data()

    def toggle_house_visibility(self):"""
content = content.replace("    def toggle_house_visibility(self):", toggle_code)

# 5. Add to Context Menu
menu_old = """        # 绑定日常功能
        if self.is_house_visible:"""
menu_new = """        # 绑定日常功能
        if getattr(self, 'is_boxed', False):
            menu.addAction("出纸箱 🐈", self.toggle_box_status)
        else:
            menu.addAction("进纸箱 📦", self.toggle_box_status)
            
        if self.is_house_visible:"""
content = content.replace(menu_old, menu_new)

# 6. Update Image matching
up_old = """        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died"]:
            img_name = self.state"""
up_new = """        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died", "box"]:
            img_name = self.state"""
content = content.replace(up_old, up_new)


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done Box")
