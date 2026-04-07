import os

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update SHARED_DATA
shared_old = """SHARED_DATA = {
    'coins': 0, 'fish_count': 0, 'water_count': 0, 'shampoo_count': 0,
    'has_fishing_rod': False, 'last_work_time': 0.0, 'maggot_battle_times': [],
    'house_type': 0, 'mortgage_total_periods': 0, 'mortgage_paid_periods': 0,
    'mortgage_daily_amount': 0, 'last_mortgage_date': ''
}
ALL_PETS = []"""

shared_new = """SHARED_DATA = {
    'coins': 0, 'fish_count': 0, 'water_count': 0, 'shampoo_count': 0,
    'has_fishing_rod': False, 'last_work_time': 0.0, 'maggot_battle_times': [],
    'house_type': 0, 'mortgage_total_periods': 0, 'mortgage_paid_periods': 0,
    'mortgage_daily_amount': 0, 'last_mortgage_date': '', 'is_house_visible': True
}
ALL_PETS = []
GLOBAL_HOUSE = None"""
content = content.replace(shared_old, shared_new)

# 2. Add is_house_visible property
prop_old = """    @property
    def house_type(self): return SHARED_DATA['house_type']"""
prop_new = """    @property
    def is_house_visible(self): return SHARED_DATA.get('is_house_visible', True)
    @is_house_visible.setter
    def is_house_visible(self, val): SHARED_DATA['is_house_visible'] = val

    @property
    def house_type(self): return SHARED_DATA['house_type']"""
content = content.replace(prop_old, prop_new)

# 3. Insert HouseWidget class
house_class = """
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
"""
content = content.replace("# ================= 桌宠本体 =================", house_class)

# 4. update buy_house to refresh GLOBAL_HOUSE
buy_h_old = """            self.save_data()
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "我们搬到简陋的房子里啦，要努力赚钱哦！", "#0066cc")
            return"""
buy_h_new = """            self.save_data()
            if GLOBAL_HOUSE: GLOBAL_HOUSE.update_house()
            self.open_chat()
            self.chat_window.append_msg("猫猫鲨", "我们搬到简陋的房子里啦，要努力赚钱哦！", "#0066cc")
            return"""
content = content.replace(buy_h_old, buy_h_new)

buy_h2_old = """        self.save_data()
        
        if self.chat_window: self.chat_window.update_aff_ui()"""
buy_h2_new = """        self.save_data()
        if GLOBAL_HOUSE: GLOBAL_HOUSE.update_house()
        
        if self.chat_window: self.chat_window.update_aff_ui()"""
content = content.replace(buy_h2_old, buy_h2_new)

# 5. Add toggle_house_visibility
toggle_code = """
    def toggle_house_visibility(self):
        self.is_house_visible = not self.is_house_visible
        self.save_data()
        if GLOBAL_HOUSE:
            GLOBAL_HOUSE.update_house()

    def rename_pet(self):"""
content = content.replace("    def rename_pet(self):", toggle_code)

# 6. Add to contextMenuEvent
menu_old = """        # 绑定日常功能
        if not self.has_named:"""
menu_new = """        # 绑定日常功能
        if self.is_house_visible:
            menu.addAction("隐藏房子 🏠", self.toggle_house_visibility)
        else:
            menu.addAction("显示房子 🏠", self.toggle_house_visibility)
            
        if not self.has_named:"""
content = content.replace(menu_old, menu_new)

# 7. main instantiate GLOBAL_HOUSE
main_old = """    for pd in pets_data:
        pet = CatShark(pd)
        ALL_PETS.append(pet)
        pet.show()
        
    sys.exit(app.exec())"""
main_new = """    global GLOBAL_HOUSE
    GLOBAL_HOUSE = HouseWidget(os.path.join(base_dir, "ui", "白色猫猫鲨"))
    
    for pd in pets_data:
        pet = CatShark(pd)
        ALL_PETS.append(pet)
        pet.show()
        
    sys.exit(app.exec())"""
content = content.replace(main_old, main_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
