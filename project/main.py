import tkinter as tk
from datetime import datetime
from itertools import cycle
import random
import os

from pathlib import Path
from Classes.device_controller import DeviceController
from Classes.page_manager import PageManager
from Classes.ui import LockPage, NavPage, SliderPage, SquareButton, TogglePage
from theme import BACKGROUND, ICON_DIR, PANEL, QUOTES, TEXT


class App:
    def __init__(self, root):
        self.root = root
        root.title("Project Display")
        root.geometry("480x320")
        root.resizable(False, False)
        root.attributes("-fullscreen", True)
        
        root.overrideredirect(True)
        root.config(cursor="none")

        root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.bind_all("<Control-Shift-Q>",)
           
        
        
        self.canvas = tk.Canvas(root, width=480, height=320,
            bg=BACKGROUND, highlightthickness=0, borderwidth=0)
        self.canvas.pack()
        self.manager = PageManager()
        self.devices = DeviceController(root)
        self.active_button = None
        self.build_top_bar()
        self.build_pages()
        self.canvas.bind("<ButtonPress-1>", self.press)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<B1-Motion>", self.drag)
        root.bind("<FocusOut>", self.cancel_press)
        self.go("lock", reset=True)
        
        self.quotes = QUOTES
        self.quotes.append(f"YOU HIT A 1/{len(self.quotes)-1}")
        self.tick_clock()
        self.rotate_quote(0)

    def build_pages(self):
        self.manager.add("lock", LockPage(self))
        self.manager.add("home", NavPage(self, "home", "Home >>", [
            (90, "LIGHTS", "#24574f", lambda: self.go("lights"),
             ICON_DIR / "lights.png"),
            (240, "TOOLS", "#354b78", lambda: self.go("tools"),
             ICON_DIR / "tools.png"),
            (390, "LOCK", "#65405a", lambda: self.go("lock", reset=True),
             ICON_DIR / "lock.png"),
        ]))
        self.manager.add("lights", NavPage(self, "lights", "Lights", [
            (90, "SHOULDER", "#24574f", lambda: self.go("shoulderlight"),
             ICON_DIR / "shoulder.png"),
            (240, "HANDS", "#354b78", lambda: self.go("handlight"),
             ICON_DIR / "hands.png"),
            (390, "MASK", "#65405a", lambda: self.go("masklight"),
             ICON_DIR / "mask.png"),
        ]))
        for name, title in [
            ("shoulderlight", "Shoulder light"),
            ("handlight", "Hand light"),
            ("masklight", "Mask light"),
        ]:
            self.manager.add(name, TogglePage(self, name, title, name))
        self.manager.add("tools", SliderPage(
            self, "tools", "Tools", "demo_latch"))

    def build_top_bar(self):
        self.canvas.create_rectangle(
            0, 0, 480, 48, fill=PANEL, outline="", tags=("topbar",))
        self.clock = self.canvas.create_text(
            12, 24, anchor="w", fill=TEXT,
            font=("DejaVu Sans", 16, "bold"), tags=("topbar",))
        self.back_button = SquareButton(
            self.canvas, "topbar", 118, 24, 44, "←", self.back,
            color=PANEL, font_size=22)
        self.quote = self.canvas.create_text(
            468, 24, anchor="e", width=315, justify="right",
            fill="#f0d77c", font=("DejaVu Sans", 10, "bold"),
            tags=("topbar",))

    def go(self, name, reset=False):
        self.cancel_press()
        self.manager.reset_to(name) if reset else self.manager.show(name)
        self.update_back_button()

    def back(self):
        self.cancel_press()
        self.manager.back()
        self.update_back_button()

    def update_back_button(self):
        self.canvas.itemconfigure(
            self.back_button.label,
            fill=TEXT if self.manager.history else "#465368")
        self.canvas.itemconfigure(
            self.back_button.tag,
            state="hidden" if self.manager.current == "lock" else "normal")

    def press(self, event):
        self.cancel_press()
        controls = list(self.manager.pages[self.manager.current].widgets)
        if self.manager.history:
            controls.append(self.back_button)
        for control in reversed(controls):
            if control.contains(event.x, event.y):
                self.active_button = control
                control.press(event.x, event.y)
                break

    def drag(self, event):
        if self.active_button is not None:
            self.active_button.drag(event.x, event.y)

    def release(self, event):
        control = self.active_button
        self.active_button = None
        if control is not None:
            control.release(event.x, event.y)

    def cancel_press(self, event=None):
        if self.active_button is not None:
            self.active_button.cancel()
            self.active_button = None

    def tick_clock(self):
        self.canvas.itemconfigure(
            self.clock, text=datetime.now().strftime("%I:%M"))
        self.root.after(1000, self.tick_clock)

    def rotate_quote(self,index):
        self.canvas.itemconfigure(self.quote, text=self.quotes[index])
        randi = random.randint(0,len(self.quotes)-2)
        self.root.after(12500, self.rotate_quote,randi if randi != index else len(self.quotes)-1)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()