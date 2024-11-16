import json, time, os
import unicodedata
import shutil
import copy
import re

class Bookmaker:
    def __init__(self) -> None:
        self.raw: list
        self.book_name: str
        self.author: str
        self.pages: list[str]
        self.maked_book: dict
        self.description: list = []

    def input(self, text: str, name: str = 'Book_Name', author: str = 'Author', description: list[str] = []):
        self.raw = text.split('\n')
        self.book_name = name
        self.author = author
        self.pages = []
        self.maked_book = {}
        self.description = description
    
    def make(self) -> None:
        print(f'Total Lines: {len(self.raw)}. Start!')
        position: tuple[int,int] = (0,0)
        page: str = ''
        pages: list[str] = []
        char_width: int = 0
        for text_line in self.raw:
            for char in text_line:
                if 'CJK' in unicodedata.name(char) or char in ['，', '。', '？', '！', '；', '：', '、']:
                        char_width = 8
                else:
                    match ord(char):
                        case 32, 34, 40, 41, 42, 73, 91, 93, 116, 123, 125:
                            char_width = 3
                        case 33, 39, 44, 46, 58, 59, 105, 124:
                            char_width = 1
                        case 60, 62, 102, 107:
                            char_width = 4
                        case 64, 126:
                            char_width = 6
                        case _:
                            char_width = 5
                line, width = position
                if width + char_width + 1 > 114:
                    line += 1
                    width = 0
                    if line > 13:
                        line = 0
                        pages.append(f"'{page}'")
                        print(f'Page[{len(pages)}]:\n{page}')
                        page = ''
                page += char
                width += char_width + 1
                position = (line, width)
            line, width = position
            page += '\\n'
            line += 1
            width = 0
            if line > 13:
                line = 0
                pages.append(f"'{page}'")
                print(f'Page[{len(pages)}]:\n{page}')
                page = ''
            position = (line, width)
        if page:
            pages.append(f"'{page}'")
            print(f'Page[{len(pages)}]:\n{page}')
        self.pages = pages
        self.maked_book = {
            'title': self.book_name,
            'author': self.author,
            'pages': self.pages,
            'display': {'Lore':self.description}
        }
        print(f'Total Pages: {len(pages)}. Finish!')
    
    def save(self) -> None:
        with open(f'{self.book_name}.json', 'w', encoding='utf-8') as f:
            json.dump(self.maked_book, f, ensure_ascii=False)
    
    def get_json(self) -> dict:
        return self.maked_book

    def get_command(self) -> None:
        print(f'give @p minecraft:written_book{self.maked_book} 1')
        print('Please use a command block.')
    
    def get_nbt(self) -> str:
        nbt_pages: str = ""
        for text in self.maked_book['pages']:
            nbt_pages += "\"{\\\"text\\\":\\\"" + text.strip("'").replace("\\n", "\n") + "\\\"}\","
        return "{author:\"" + self.maked_book['author'] + "\",title:\"" + self.maked_book['title'] + "\",pages:[" + nbt_pages + "]}"
            

class DatapackMaker:
    def __init__(self) -> None:
        
        self.log('Main', 'Initializing...')
        self.maker: Bookmaker = Bookmaker()
        if os.path.exists('latest.log'):
            os.remove('latest.log')
            self.log('Main', 'Cleared latest.log.')
        if not os.path.exists('all_books'): os.mkdir('all_books')
        if not os.path.exists('all_lostpages'): os.mkdir('all_lostpages')
        if not os.path.exists('build'): os.mkdir('build')
        self.log('Main', 'Checked dirs.')
    
    def log(self, tag: str, text: str):
        with open('latest.log', 'a', encoding='utf-8') as f:
            f.write(f'[{tag}] : {text}')
            f.write('\n')
            print(f'[{tag}] : {text}')
    
    def parse_book(self, file_path:str, file_name: str) -> tuple[str, str, str, list[str]]:
        book_info = file_name.split('-')
        title = book_info[0] if book_info[0] else 'Unknown'
        author = book_info[1] if book_info[1] else 'Unknown'

        pattern = r'LORE BEGIN(.*?)LORE END'
        with open(os.path.join(file_path, file_name), 'r', encoding='utf-8') as f:
            o_text = f.read()
            lores = re.findall(pattern, o_text, re.DOTALL)
            if lores:
                lore = [line for line in lores[0].splitlines() if line]
            else:
                lore = []
            text = re.sub(pattern, '', o_text)
        
        return text, title, author, lore
            
        

    def get_all_books(self) -> list[tuple[str, str, str, list[str]]]:
        self.log('BooksGetter', 'Getting all books...')
        all_books: list[tuple[str, str, str, list[str]]] = []
        for path, subdirs, files in os.walk("all_books"):
            for name in files:
                all_books.append(self.parse_book(path, name))
        return all_books
    
    def get_all_lostpages(self) -> list[list[str]]:
        self.log('LostPagesGetter', 'Getting all lost pages...')
        all_lostpages: list[list[str]] = []
        for path, subdirs, files in os.walk("all_lostpages"):
            for name in files:
                with open(os.path.join(path, name), 'r', encoding='utf-8') as f:
                    all_lostpages.append(f.read().splitlines())
        return all_lostpages
    
    def make(self):
        
        self.log('Main', 'Reading books...')
        all_books = self.get_all_books()
        self.log('Main', f'Finish! Total books: {len(all_books)}.')
        
        self.log('Main', 'Reading lost pages...')
        all_lostpages = self.get_all_lostpages()
        self.log('Main', f'Finish! Total lost pages: {len(all_lostpages)}.')
        
        self.log('Main', 'Creating datapack dir...')
        datapack_dir = f'build/Minecraft_BooksAndStories_b{len(all_books)}l{len(all_lostpages)}'
        
        if os.path.exists(datapack_dir):
            shutil.rmtree(datapack_dir)
        
        os.mkdir(datapack_dir)
        with open(datapack_dir + '/pack.mcmeta', 'w', encoding='utf-8') as f:
            json.dump({"pack": {"description": "I left so much to say...","pack_format": 15}}, f, indent=4)
        
        os.mkdir(datapack_dir + '/data')
        os.mkdir(datapack_dir + '/data/falsw')
        os.mkdir(datapack_dir + '/data/falsw/loot_tables')
        os.mkdir(datapack_dir + '/data/minecraft')
        os.mkdir(datapack_dir + '/data/minecraft/loot_tables')

        self.log('Main', 'Creating loot tables...')
        
        loot_table = {
            "type": "minecraft:chest",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [
                   ]
                }
            ]
        }
        
        item_the_book = {
            "type": "minecraft:item",
            "name": "minecraft:written_book",
            "functions": [
                {
                    "function": "minecraft:set_nbt",
                    "tag": ""
                },
                {
                    "function": "minecraft:set_lore",
                    "lore": []
                }
            ]
        }
        item_the_note = {
            "type": "minecraft:item",
            "name": "minecraft:paper",
            "functions": [
                {
                    "function": "minecraft:set_name",
                    "name": {"text": "残页", "italic": False, "color": "blue"}
                },
                {
                    "function": "minecraft:set_lore",
                    "lore": []
                }
            ]
        }
        

        self.log('Main', 'Adding books...')
        books_table = copy.deepcopy(loot_table)
        
        for book in all_books:
            text, title, author, lore = book
            self.maker.input(text, title, author)
            self.maker.make()
            n_book = self.maker.get_nbt()
            i_book = copy.deepcopy(item_the_book)
            i_book['functions'][0]['tag'] = n_book
            i_book['functions'][1]['lore'] = lore
            books_table['pools'][0]['entries'].append(i_book)
            
            self.log('Main', f'Added book: ({len(text)} chars)')
        
        with open(datapack_dir + '/data/falsw/loot_tables/books.json', 'w', encoding='utf-8') as f:
            json.dump(books_table, f, indent=4, ensure_ascii=False)
            self.log('Main', 'Added books table.')
        
        
        self.log('Main', 'Adding lost pages...')
        lostpages_table = copy.deepcopy(loot_table)
        
        for lostpage in all_lostpages:
            i_note = copy.deepcopy(item_the_note)
            i_note['functions'][1]['lore'] = lostpage
            lostpages_table['pools'][0]['entries'].append(i_note)

            self.log('Main', f'Added lost page: {len(lostpage)} lines')
            
        # pack info tag
        tag_lostpage = str(time.time())
        i_tag_lostpage = copy.deepcopy(item_the_note)
        i_tag_lostpage['functions'][0]['name']['text'] = tag_lostpage
        i_tag_lostpage['functions'][0]['name']['color'] = 'red'
        i_tag_lostpage['functions'][1]['lore'] = ['b' + str(len(all_books)), 'n' + str(len(all_lostpages))]
        lostpages_table['pools'][0]['entries'].append(i_tag_lostpage)
        self.log('Main', 'Added pack info tag lost page.')
        
        with open(datapack_dir + '/data/falsw/loot_tables/lostpages.json', 'w', encoding='utf-8') as f:
            json.dump(lostpages_table, f, indent=4, ensure_ascii=False)
            self.log('Main', 'Added lost pages table.')
        
        self.log('Main', 'Copying resources...')
        shutil.copytree('resources/chests', datapack_dir + '/data/minecraft/loot_tables/chests')
        
        self.log('Main', 'Finish!')
        self.log('Main', 'Saved datapack to: ' + datapack_dir)
        
if __name__ == '__main__':
    DatapackMaker().make()