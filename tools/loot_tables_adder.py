import os
import json
import sys

root: str = './resources/chests'
root_villages: str = './resources/chests/village'

def get_file_list(dir: str):
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

def add_loot_table(path: str, loot_table: dict):

    with open(path, 'r', encoding='utf-8') as f:
        content: dict = json.load(f)

    content['pools'].append(loot_table)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)
    
    print(f'Added loot table to {path}')

def add_all(dir: str, loot_table: dict):
    if not os.path.exists(dir):
        print(f'{dir} does not exist')
        return
    file_list = get_file_list(dir)
    for file_name in file_list:
        add_loot_table(os.path.join(dir, file_name), loot_table)

if __name__ == '__main__':
    books_table: dict = {
        "bonus_rolls": 0.0,
        "entries": [
            {
                "type": "minecraft:loot_table",
                "name": "falsw:books",
                "weight": 10
            },
            {
                "type": "minecraft:empty",
                "weight": 90
            }
        ],
        "rolls": 1.0
    }
    add_all(root, books_table)
    lostpages_table: dict = {
        "bonus_rolls": 0.0,
        "entries": [
            {
                "type": "minecraft:loot_table",
                "name": "falsw:lostpages",
                "weight": 10
            },
            {
                "type": "minecraft:empty",
                "weight": 90
            }
        ],
        "rolls": 2.0
    }
    add_all(root, lostpages_table)