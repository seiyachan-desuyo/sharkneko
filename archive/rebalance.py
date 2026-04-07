import os

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Age 1800 -> 3600
content = content.replace("time.time() - getattr(self, 'birth_timestamp', time.time())) / 1800", "time.time() - getattr(self, 'birth_timestamp', time.time())) / 3600")

# 2. __init__ add vars
content = content.replace("self.egg_clicks = 0", "self.egg_clicks = 0\n        self.last_gym_time = pet_data.get('last_gym_time', 0.0)\n        self.last_drain_time = pet_data.get('last_drain_time', time.time())")

# 3. load_data
content = content.replace("self.has_named = data.get('has_named', False)", "self.has_named = data.get('has_named', False)\n                    self.last_gym_time = data.get('last_gym_time', 0.0)\n                    self.last_drain_time = data.get('last_drain_time', time.time())")

# 4. save_data
content = content.replace("'is_boxed': getattr(p, 'is_boxed', False)", "'is_boxed': getattr(p, 'is_boxed', False),\n                    'last_gym_time': getattr(p, 'last_gym_time', 0.0),\n                    'last_drain_time': getattr(p, 'last_drain_time', __import__('time').time())")

# 5. work penalty fix
old_work = '''    def finish_working(self):
        import time
        now = time.time()
        self.state = "money"
        self.update_image()
        self.coins += 35
        
        # 1小时内重复打工会有惩罚
        if now - self.last_work_time < 3600:
            self.change_hp(-10)
            self.change_affection(-10)
            if self.hp > 0:
                self.open_chat()
                self.chat_window.append_msg("猫猫鲨", "连续打工太累了宝宝要碎了！赚了35金币，但扣除10点生命和好感！", "#ff4d4d")
        else:
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "打工完成！努力赚钱养家！赚到了35个金币！", "#0066cc")'''

new_work = '''    def finish_working(self):
        import time
        now = time.time()
        self.state = "money"
        self.update_image()
        
        # 1小时内重复打工会有惩罚
        if now - self.last_work_time < 3600:
            self.change_hp(-15)
            self.change_affection(-15)
            if self.hp > 0:
                self.open_chat()
                self.chat_window.append_msg("猫猫鲨", "连续打工效率极差！一分钱没赚到，还扣了15点生命和好感！", "#ff4d4d")
        else:
            self.coins += 35
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "打工完成！努力赚钱养家！赚到了35个金币！", "#0066cc")'''
content = content.replace(old_work, new_work)

# 6. gym cooldown & balance
old_gym = '''    def go_gym(self):
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
            self.chat_window.append_msg("系统", "金币不足20，连健身房的门卡都办不起！", "#ff4d4d")'''

new_gym = '''    def go_gym(self):
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
            self.chat_window.append_msg("系统", "金币不足30，连健身房的门卡都办不起！", "#ff4d4d")'''
content = content.replace(old_gym, new_gym)

# Replace gym menu text
content = content.replace("去健身房 🏋️ (20金币)", "去健身房 🏋️ (30金币)")

# 7. fishing exploit fix
content = content.replace("self.change_affection(10)\n        self.state = \"fishing\"", "self.state = \"fishing\"")

# 8. passive drain
ra_old = '''    def random_action(self):
        if getattr(self, 'is_egg', False): return'''
ra_new = '''    def random_action(self):
        if getattr(self, 'is_egg', False): return
        
        # 被动流逝：每小时 -2 HP, -2 好感度
        import time
        now = time.time()
        drain_interval = 3600
        last_drain = getattr(self, 'last_drain_time', now)
        if now - last_drain >= drain_interval:
            hours_passed = int((now - last_drain) / drain_interval)
            self.change_hp(-2 * hours_passed)
            self.change_affection(-2 * hours_passed)
            self.last_drain_time = last_drain + hours_passed * drain_interval
            self.save_data()'''
content = content.replace(ra_old, ra_new)

# 9. Optional: fix trigger_death so it doesn't kill the whole app if there are multiple pets
td_old = '''    def trigger_death(self):
        self.state = "die"
        self.update_image()
        self.open_chat()
        self.chat_window.append_msg("猫猫鲨", "我再也不喜欢妈妈了！", "#ff4d4d")
        # 3秒后退出程序
        QTimer.singleShot(3000, QApplication.quit)'''
td_new = '''    def trigger_death(self):
        self.state = "die"
        self.update_image()
        self.open_chat()
        self.chat_window.append_msg("猫猫鲨", "我再也不喜欢妈妈了！", "#ff4d4d")
        
        def remove_pet():
            self.hide()
            if self.chat_window: self.chat_window.hide()
            if self in ALL_PETS: ALL_PETS.remove(self)
            if not ALL_PETS: QApplication.quit()
            
        QTimer.singleShot(3000, remove_pet)'''
content = content.replace(td_old, td_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Rebalance applied")
