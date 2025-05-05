from tkinter import *
import threading
import pyperclip
from pynput import keyboard
from openai import OpenAI
import pyautogui
import pytesseract
from PIL import Image
import time
from pynput import mouse

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

previous_copied_word = pyperclip.paste()
copied_word = None

client = OpenAI(api_key='')

# Used to decide where to spawn the window and take the screenshot

start_x = None
start_y = None

width = None
height = None

double_click_detected = False
marked_word_detected = False
DOUBLE_CLICK_MAX_DELAY = 0.5
last_time_clicked = None
gui_spawn_x = 100
gui_spawn_y = 100

# Styling
bg_color = "#2C2C2C"

def CheckClipboardContinuosly():
    global previous_copied_word, copied_word
    while True:
        copied_word = pyperclip.paste()
        if (previous_copied_word != copied_word):

            # Take screenshot of screen
            screenshot = pyautogui.screenshot(region=(0, start_y-100, 1920, 150))
            screenshot.save("screenshot.png")

            text = pytesseract.image_to_string(screenshot)
            print("Converted screenshot to string")
            
            # Send request to OpenAI's API
            response = client.responses.create(
                model="gpt-4.1-nano-2025-04-14",
                input=f"The word: {copied_word}. Context: {text}",
                instructions="Explain the word accurately, briefly, and concisely."
            ) 

            # Show word on the screen
            word_meaning = response.output[0].content[0].text
            root.after(1, UpdateGUI(word_meaning))
            
            # Update previous word copied
            previous_copied_word = copied_word
            
def UpdateGUI(word_meaning):
    global bg_color
    for widget in frame.winfo_children():
        widget.destroy()
    label = Label(frame, text=word_meaning, bg=bg_color, fg="white")
    label.grid(column=0, row=0, sticky="nsew")
    root.after(1, update_window_position())

def update_window_position():
    global gui_spawn_x, gui_spawn_y

    # Update window position here
    root.geometry(f"+{gui_spawn_x}+{gui_spawn_y}")
    root.deiconify() # because of quirks in how overrideredirect, geometry, and visibility interact, it forces the window manager to reprocess positioning and appearance.
    root.attributes("-topmost", True)

def change_topmost(bool):
    root.attributes("-topmost", bool)

def OnClick(mouse_x, mouse_y, mouse_button, pressed):
    global start_x, start_y, width, height, last_time_clicked, gui_spawn_x, gui_spawn_y, double_click_detected, marked_word_detected
    if pressed:
        change_topmost(False)
        now = time.time()
        # Is it a double click?
        if last_time_clicked is not None:
            if (now - last_time_clicked < DOUBLE_CLICK_MAX_DELAY and start_x == mouse_x and start_y == mouse_y):
                print("Double click detected")
                double_click_detected = True
            else:
                print("Single click detected")
                double_click_detected = False

        last_time_clicked = now
        # Start positions
        start_x = mouse_x
        start_y = mouse_y
        
    else:
        if start_x is None or start_y is None:
            return
        width = abs(mouse_x - start_x)
        height = abs(mouse_y - start_y)

        if (width > 0 or height > 0):
            print("User has marked word")
            marked_word_detected = True
        else:
            print("User has not marked word")
            marked_word_detected = False

        if (marked_word_detected):

            min_x = min(start_x, mouse_x)
            min_y = min(start_y, mouse_y)
            app_height = root.winfo_height()
            gui_spawn_y = abs(min_y-app_height) - 20
            gui_spawn_x = abs(min_x - 50) 


# === Main Frontend ===
root = Tk()
root.withdraw()
# root.geometry(f"500x70+{gui_spawn_x}+{gui_spawn_y}")
root.overrideredirect(True)
root.configure(bg=bg_color)

# Grid configuration
root.grid_rowconfigure(1, weight=1)  # Give row 1 (content) room to grow
root.grid_columnconfigure(0, weight=1)

# === Custom title bar ===
title_bar = Frame(root, bg="#1F1F1F", relief="raised", bd=0, height=30)
title_bar.grid(row=0, column=0, sticky="new")

title_label = Label(title_bar, text="AI Dictionary", bg="#1F1F1F", fg="white", font=("Arial", 10))
title_label.pack(side=LEFT, padx=10)

close_button = Button(title_bar, text="✕", bg="#1F1F1F", fg="white", font=("Arial", 10, "bold"),
                      bd=0, highlightthickness=0, command=root.destroy, activebackground="#3A3A3A")
close_button.pack(side=RIGHT, padx=5)

# Possible to drag application 
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)

# === Content Frame ===
frame = Frame(root, padx=10, pady=10, bg=bg_color)
frame.grid(row=1, column=0, sticky="nsew")

label = Label(frame, text="", bg=bg_color, fg="white")
label.grid(column=0, row=0, sticky="nsew")

frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

root.bind("<Button-1>", start_move)
root.bind("<B1-Motion>", do_move)


threading.Thread(target=CheckClipboardContinuosly,daemon=True).start()

mouse_listener = mouse.Listener(on_click=OnClick)
mouse_listener.start()

root.mainloop()


# === Things that can be improved or are missing ===

# Limit, so users can't send too many tokens at once - right now they could potentially send 1 million tokens at once or more
# If the explanation is x long make it span one more line
# Choose between output languages
# Choose between short and long answers
# Make it possible for users to write their own instructions
# Possible to write with the bot
# Choose another hotkey than CTRL + C
# Update the position of where the window should spawn if the click was a double click