import os

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update SHARED_DATA
shared_old = """SHARED_DATA = {
    'coins': 0, 'fish_count': 0, 'water_count': 0, 'shampoo_count': 0,
    'has_fishing_rod': False, 'last_work_time': 0.0, 'maggot_battle_times': []
}"""

shared_new = """SHARED_DATA = {
    'coins': 0, 'fish_count': 0, 'water_count': 0, 'shampoo_count': 0,
    'has_fishing_rod': False, 'last_work_time': 0.0, 'maggot_battle_times': [],
    'house_type': 0, 'mortgage_total_periods': 0, 'mortgage_paid_periods': 0,
    'mortgage_daily_amount': 0, 'last_mortgage_date': ''
}"""
content = content.replace(shared_old, shared_new)

# 2. Add Properties
prop_insert = """
    @property
    def maggot_battle_times(self): return SHARED_DATA['maggot_battle_times']
    @maggot_battle_times.setter
    def maggot_battle_times(self, val): SHARED_DATA['maggot_battle_times'] = val
"""

prop_new = prop_insert + """
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
"""
content = content.replace(prop_insert, prop_new)

# 3. Add to system prompt
sys_old = """如果你的生命值低于30，你正处于极度虚弱、想哭的状态。"""
sys_new = """如果你的生命值低于30，你正处于极度虚弱、想哭的状态。
【房屋与房贷信息】
你当前住在：""" + "{['简陋房子', '普通房子', '豪华房子'][self.pet.house_type]}" + """
""" + "{f'妈妈目前背负着房贷，每天需还款 {self.pet.mortgage_daily_amount} 金币，已还 {self.pet.mortgage_paid_periods}/{self.pet.mortgage_total_periods} 期。' if self.pet.mortgage_total_periods > 0 and self.pet.mortgage_paid_periods < self.pet.mortgage_total_periods else '妈妈目前没有房贷压力。'}"

content = content.replace(sys_old, sys_new)


# 4. Add mortgage check in random_action
ra_old = """    def random_action(self):
        if getattr(self, 'is_egg', False): return"""

ra_new = """    def random_action(self):
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
                """
content = content.replace(ra_old, ra_new)

# 5. Add House Menu and Logic
buy_egg_code = """    def buy_egg(self):"""
house_code = """    def buy_house(self):
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
        
        if self.chat_window: self.chat_window.update_aff_ui()
        self.open_chat()
        if periods > 1:
            self.chat_window.append_msg("系统", f"恭喜购买新房！已扣除首付 {down_payment} 金币。接下来还要还 {periods - 1} 天房贷，每天 {daily_amount} 金币哦！", "#ff6699")
        else:
            self.chat_window.append_msg("系统", f"全款拿下新房！花费 {price} 金币，大佬大气！", "#ff6699")

    def buy_egg(self):"""
content = content.replace(buy_egg_code, house_code)


menu_old = """        # 绑定商店功能
        shop_menu.addAction("猫猫鲨蛋 (500金币)", self.buy_egg)"""
menu_new = """        # 绑定商店功能
        shop_menu.addAction("买房子 🏠", self.buy_house)
        shop_menu.addAction("猫猫鲨蛋 (500金币)", self.buy_egg)"""
content = content.replace(menu_old, menu_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
