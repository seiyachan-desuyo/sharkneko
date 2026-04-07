import sys
file_path = '/Users/seiya/Desktop/猫猫鲨/main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the broken patch if it exists
if "def global_exception_handler" in content:
    # Just remove my faulty imports so I don't break datetime
    content = content.replace("import sys\nimport traceback\nimport datetime\n\ndef global_exception_handler", "import sys\nimport traceback\nimport datetime as _my_dt\n\ndef global_exception_handler")
    content = content.replace("{datetime.datetime.now()}", "{_my_dt.datetime.now()}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed patch.")
