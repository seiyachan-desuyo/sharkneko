import os

file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update image map for exercise
up_old = """        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died", "box"]:\n            img_name = self.state"""
up_new = """        elif self.state in ["dragon", "whale", "love in bed", "birth", "love", "heaven", "Variant died", "box", "exercise"]:\n            img_name = self.state"""
content = content.replace(up_old, up_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Image path patched")
