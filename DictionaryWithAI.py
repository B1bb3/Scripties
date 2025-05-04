""" import tesseract
import pyautogui
from pynput.mouse import Listener
from PIL import Image
import time 
import pyperclip 
from pynput import keyboard  """
# husk at lave limit så de ikke kan sende 1 mil tokens på en gang.
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
button_pressed = True
bg_color = "#2C2C2C"

client = OpenAI(api_key='')

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


def CheckClipboardContinuosly():
    global previous_copied_word, copied_word, button_pressed
    while True:
        time.sleep(0.2)

        copied_word = pyperclip.paste()
        if (previous_copied_word != copied_word and button_pressed):

            # Take screenshot of screen
            screenshot = pyautogui.screenshot(region=(start_x, start_y, 1720, 800))
            screenshot.save("screenshot.png")

            text = pytesseract.image_to_string(screenshot)


            print(text)
            
            # Send request to OpenAI's API
            response = client.responses.create(
                model="gpt-4.1-nano-2025-04-14",
                input=copied_word,
                instructions="Explain the word accurately, briefly, and concisely."
            ) 

            word_meaning = response.output[0].content[0].text
            UpdateGUI(word_meaning)
            
            previous_copied_word = copied_word
            
def UpdateGUI(word_meaning):
    global bg_color
    for widget in frame.winfo_children():
        widget.destroy()
    label = Label(frame, text=word_meaning, bg=bg_color, fg="white")
    label.grid(column=0, row=0, sticky="nsew")
    update_window_position()

def update_window_position():
    global gui_spawn_x, gui_spawn_y

    # Update window position here (you can adjust this to your logic)
    root.geometry(f"+{gui_spawn_x}+{gui_spawn_y}")
    root.attributes("-topmost", True)




def OnClick(mouse_x, mouse_y, mouse_button, pressed):
    global start_x, start_y, width, height, last_time_clicked, gui_spawn_x, gui_spawn_y, double_click_detected, marked_word_detected
    if pressed:
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
        width = abs(mouse_x-start_x)
        height = abs(mouse_y-start_y)

        if (width > 0 or height > 0):
            gui_spawn_x = start_x
            gui_spawn_y = start_y
            print("User has marked word")
            marked_word_detected = True
        else:
            print("User has not marked word")
            marked_word_detected = False

    if (marked_word_detected):
        min_x = min(start_x, mouse_x)
        min_y = min(start_y, mouse_y)
        app_width = root.winfo_width()
        app_height = root.winfo_height()

        gui_spawn_y = abs(min_y-app_height) - 50
        gui_spawn_x = min_x


# === Main Frontend ===
root = Tk()
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



"""def OnPress(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def OnRelease(key):
    print(f'Key released: {key}')
    if key == keyboard.Key.esc:
        # Stop listener
       return False
"""

"""
start_x = None
start_y = None
screenshot = None

def on_click(x, y, button, pressed):
    global start_x, start_y, screenshot

    if (pressed):
        start_x = x
        start_y = y
        print(f"Button pressed at: {start_x}, {start_y}")

    else: 
        end_x = x
        end_y = y

        left = min(start_x, end_x)
        top = min(start_y, end_y)
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)
        if width > 0 and height > 0:
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            print("Screenshot taken")    
            screenshot.save("SelectedArea.png")
            print("Screenshot saved")


listener = Listener(on_click=on_click)
listener.start()
listener.join()
"""

"""listener = keyboard.Listener(on_press=OnPress, on_release=OnRelease)
listener.start() """