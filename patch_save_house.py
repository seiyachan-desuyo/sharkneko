import os
import json

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add to save_data
save_old = """                    'shampoo_count': self.shampoo_count,
                    'has_fishing_rod': self.has_fishing_rod,
                    'last_work_time': self.last_work_time,
                    'maggot_battle_times': getattr(self, 'maggot_battle_times', [])"""

save_new = """                    'shampoo_count': self.shampoo_count,
                    'has_fishing_rod': self.has_fishing_rod,
                    'last_work_time': self.last_work_time,
                    'maggot_battle_times': getattr(self, 'maggot_battle_times', []),
                    'house_type': self.house_type,
                    'mortgage_total_periods': self.mortgage_total_periods,
                    'mortgage_paid_periods': self.mortgage_paid_periods,
                    'mortgage_daily_amount': self.mortgage_daily_amount,
                    'last_mortgage_date': self.last_mortgage_date"""

content = content.replace(save_old, save_new)

# Add to load_data
load_old = """                    SHARED_DATA['maggot_battle_times'] = data.get('maggot_battle_times', [])"""
load_new = """                    SHARED_DATA['maggot_battle_times'] = data.get('maggot_battle_times', [])
                    SHARED_DATA['house_type'] = data.get('house_type', 0)
                    SHARED_DATA['mortgage_total_periods'] = data.get('mortgage_total_periods', 0)
                    SHARED_DATA['mortgage_paid_periods'] = data.get('mortgage_paid_periods', 0)
                    SHARED_DATA['mortgage_daily_amount'] = data.get('mortgage_daily_amount', 0)
                    SHARED_DATA['last_mortgage_date'] = data.get('last_mortgage_date', '')"""
content = content.replace(load_old, load_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Save patch Done")
