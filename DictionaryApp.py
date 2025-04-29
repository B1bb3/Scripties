import pyperclip
import requests
from tkinter import *
from tkinter import ttk
import threading
import time
import pyautogui
# import json     og derefter json.loads(tekst som man gerne vil have til json)


last_text_selected = ""
selected_text = "" 
initial_word = pyperclip.paste()
meaning_index = 0
meanings_in_total = 0
keys = []
current_word_class = ""

our_meanings = {
    "noun": [],
    "verb": [],
    "adjective": [],
    "adverb": [],
    "pronoun": [],
    "preposition": [],
    "conjunction": [],
    "interjection": [],
} # Hey

def check_clipboard_continuosly():
    global last_text_selected, selected_text, our_meanings, meanings_in_total, keys, meaning_index, current_word_class

    while True:
        time.sleep(1)

        selected_text = pyperclip.paste()

        if (initial_word == selected_text):
            continue
        
        if (last_text_selected != selected_text):
            root.after(0, show_window)
            
            meaning_index = 0
            meanings_in_total = 0
            keys = []
            our_meanings = {
            "noun": [],
            "verb": [],
            "adjective": [],
            "adverb": [],
            "pronoun": [],
            "preposition": [],
            "conjunction": [],
            "interjection": [],
            }

            r = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{selected_text}')

            json_meanings = r.json()[0]["meanings"]

            if (r.status_code == 200):
                print("Request received with code 200")
            else:
                print("Request failed")


            # r.json()[0]["meanings"]    = all objects whether they are nouns, verbs or adjectives
            for meaning in json_meanings:
                part_of_speech = meaning.get("partOfSpeech", '')

                print(f"Checking part_of_speech: {part_of_speech}")
                print("      ")
                print(f"Checking definitions: {meaning['definitions']}")

                # Sort them into the eight different word classes
                if part_of_speech == "noun":
                    our_meanings["noun"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("noun")
                elif part_of_speech == "verb":
                    our_meanings["verb"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("verb")
                elif part_of_speech == "adjective":
                    our_meanings["adjective"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("adjective")
                elif part_of_speech == "adverb":
                    our_meanings["adverb"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("adverb")
                elif part_of_speech == "pronoun":
                    our_meanings["pronoun"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("pronoun")
                elif part_of_speech == "preposition":
                    our_meanings["preposition"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("preposition")
                elif part_of_speech == "conjunction":
                    our_meanings["conjunction"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("conjunction")
                elif part_of_speech == "interjection":
                    our_meanings["interjection"].extend(meaning["definitions"])
                    meanings_in_total += 1
                    keys.append("interjection")

            print(f"Checking our meanings: {our_meanings}")
            last_text_selected = selected_text

            current_word_class = keys[0]

            root.after(25, update_gui)


def update_gui():
    global meaning_index, meanings_in_total, keys, our_meanings, current_word_class
    for widget in frame.winfo_children():
        widget.destroy()
    ttk.Label(frame, text = f"{current_word_class}: {our_meanings[current_word_class][0]['definition']}").grid(column = 0, row = 0)
    if meanings_in_total - 1 != meaning_index: # Spawn the Next button if there are more meanings to show
        ttk.Button(frame, text="Next", command=nextMeaning).grid(column=1, row=0)
    if (meaning_index != 0):
        ttk.Button(frame, text="Back", command=previousMeaning).grid(column=1, row=1)
    

def show_window():
    x, y = pyautogui.position()
    root.geometry(f"+{x}+{y}")
    root.update_idletasks()
    root.deiconify()
    root.attributes('-topmost', True)  # Make it topmost for a brief moment
    root.lift()  # Bring it to the front
    root.attributes('-topmost', False)  # Return it to normal

def nextMeaning():
    global meaning_index, meanings_in_total, keys, our_meanings, current_word_class
    if (meaning_index < meanings_in_total):
        current_word_class = keys[meaning_index + 1]
        meaning_index += 1
        update_gui()

def previousMeaning():
    global meaning_index, meanings_in_total, keys, our_meanings, current_word_class
    if (meaning_index > 0):
        current_word_class = keys[meaning_index - 1]
        meaning_index -= 1
        update_gui()

# Frontend
root = Tk()
frame = ttk.Frame(root, padding=10)
frame.grid()

thread1 = threading.Thread(target=check_clipboard_continuosly, daemon=True)
thread1.start()


root.mainloop()








