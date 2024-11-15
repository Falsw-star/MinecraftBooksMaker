import os

files = os.listdir("notes")
for file in files:
    with open(f"notes/{file}", "r", encoding='utf-8') as f:
        data: str = f.read()
    with open(f"all_lostpages/{file}.txt", "w", encoding='utf-8') as f:
        f.write(data)