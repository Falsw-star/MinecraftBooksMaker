import os
import json

files = os.listdir("books")
for file in files:
    if file.endswith(".json"):
        with open(f"books/{file}", "r", encoding='utf-8') as f:
            data: dict = json.load(f)
            data["author"].replace("Anonymous", "Unknown")
            n = 0
            while os.path.exists(f"all_books/{data['title']}-{data['author']}-{str(n)}.txt"):
                n += 1
            with open(f"all_books/{data["title"]}-{data["author"]}-{str(n)}.txt", "w", encoding='utf-8') as f:
                f.write(data["text"])
                f.write("\n\n\n")
                f.write("LORE BEGIN")
                for line in data["lore"]:
                    f.write(line)
                f.write("LORE END")
            print(f"Wrote {data["title"]}-{data["author"]}-{str(n)}")