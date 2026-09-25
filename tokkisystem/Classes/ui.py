from pathlib import Path
import warnings

from theme import ACCENT, BACKGROUND, MUTED, PANEL, TEXT, UNLOCK_CODE
from .page_manager import Page

class SquareButton:
    def __init__(self, canvas, page_tag, x, y, size, label, command,
                 color="#284957", font_size=18, icon_path=None,
                 show_background=True):
        self.canvas = canvas
        self.x, self.y, self.size = x, y, size
        self.color, self.font_size = color, font_size
        self.label_text, self.command = label, command
        self.show_background = show_background
        self.images = None
        self.pressed = False
        self.tag = f"button:{id(self)}"
        tags = (page_tag, self.tag)
        self.background = canvas.create_rectangle(
            0, 0, 0, 0, fill=color, outline="", tags=tags)
        self.label = canvas.create_text(
            x, y, text=label, fill=TEXT, justify="center",
            font=("DejaVu Sans", font_size, "bold"), tags=tags)
        self.icon = canvas.create_image(x, y, tags=tags)
        self.set_icon(icon_path)

    def set_icon(self, icon_path):
        self.images = None
        self.canvas.itemconfigure(self.icon, image="")
        if icon_path is not None and Path(icon_path).is_file():
            try:
                from PIL import Image, ImageEnhance, ImageTk
                with Image.open(icon_path) as source:
                    normal = source.convert("RGBA")
                resampling = getattr(Image, "Resampling", Image).LANCZOS
                edge = max(1, round(self.size * 0.68))
                normal.thumbnail((edge, edge), resampling)
                pressed = normal.resize(
                    (max(1, round(normal.width * .8)),
                     max(1, round(normal.height * .8))), resampling)
                pressed = ImageEnhance.Brightness(pressed).enhance(.65)
                self.images = (ImageTk.PhotoImage(normal, master=self.canvas),
                               ImageTk.PhotoImage(pressed, master=self.canvas))
            except (ImportError, OSError) as error:
                warnings.warn(f"Could not load {icon_path}: {error}")
        self.draw(False)

    def contains(self, x, y):
        half = self.size / 2
        return (self.x-half <= x <= self.x+half and
                self.y-half <= y <= self.y+half)

    def press(self, x, y):
        if self.contains(x, y):
            self.draw(True)

    def drag(self, x, y):
        self.draw(self.contains(x, y))

    def cancel(self):
        self.draw(False)

    def release(self, x, y):
        activated = self.contains(x, y)

        if activated:
            # Keep the pressed appearance visible briefly.
            self.draw(True)
            self.canvas.after(75, self.finish_press)
        else:
            self.draw(False)

    def finish_press(self):
        self.draw(False)
        self.command()

    def draw(self, pressed):
        self.pressed = pressed
        scale = .8 if pressed else 1
        half = self.size * scale / 2
        self.canvas.coords(self.background, self.x-half, self.y-half,
                           self.x+half, self.y+half)
        color = self.color
        if pressed:
            rgb = [int(color[i:i+2], 16) for i in (1, 3, 5)]
            color = "#" + "".join(f"{int(c*.65):02x}" for c in rgb)
        self.canvas.itemconfigure(
            self.background,
            fill=color if self.show_background or not self.images else "")
        self.canvas.itemconfigure(
            self.label, text="" if self.images else self.label_text,
            font=("DejaVu Sans", max(8, int(self.font_size*scale)), "bold"))
        if self.images:
            self.canvas.itemconfigure(self.icon, image=self.images[int(pressed)])


class UnlockSlider:
    def __init__(self, canvas, page_tag, unlock_command, lock_command,time):
        self.canvas = canvas
        self.time = time
        self.unlock_command, self.lock_command = unlock_command, lock_command
        self.left, self.right, self.y, self.size = 40, 440, 172, 64
        self.start, self.end = 72, 408
        self.value, self.unlocked, self.dragging, self.offset = 0, False, False, 0
        tags = (page_tag, f"slider:{id(self)}")
        self.track = canvas.create_rectangle(
            40, 140, 440, 204, fill=PANEL, outline="", tags=tags)
        self.hint = canvas.create_text(
            230, 172, text="SLIDE TO UNLOCK", fill=MUTED,
            font=("DejaVu Sans", 12, "bold"), tags=tags)
        self.thumb = canvas.create_rectangle(
            0, 0, 0, 0, fill=ACCENT, outline="", tags=tags)
        self.symbol = canvas.create_text(
            0, 0, text="→", fill=BACKGROUND,
            font=("DejaVu Sans", 25, "bold"), tags=tags)
        self.draw()

    def center(self): return self.start + (self.end-self.start)*self.value

    def contains(self, x, y):
        return abs(x-self.center()) <= 32 and abs(y-self.y) <= 32

    def draw(self):
        center = self.center()
        self.canvas.coords(self.thumb, center-32, 140, center+32, 204)
        self.canvas.coords(self.symbol, center, self.y)
        self.canvas.itemconfigure(
            self.thumb, fill="#65405a" if self.unlocked else
            ("#43b3a3" if self.dragging else ACCENT))
        self.canvas.itemconfigure(
            self.symbol, text="✕" if self.unlocked else "→",
            fill=TEXT if self.unlocked else BACKGROUND)
        self.canvas.itemconfigure(
            self.hint, text="UNLOCKED" if self.unlocked else "SLIDE TO UNLOCK")

    def press(self, x, y):
        if not self.unlocked:
            self.offset, self.dragging = x-self.center(), True
            self.draw()

    def drag(self, x, y):
        if self.dragging and not self.unlocked:
            self.value = max(0, min(1,
                (x-self.offset-self.start)/(self.end-self.start)))
            self.draw()

    def release(self, x, y):
        if self.unlocked:
            if self.contains(x, y): self.lock_command()
            return
        if not self.dragging: return
        self.drag(x, y)
        completed = self.value >= .9
        self.dragging = False
        if completed:
            self.set_unlocked(True)
            self.unlock_command()
        else:
            self.cancel()

    def cancel(self):
        self.dragging = False
        self.value = 1 if self.unlocked else 0
        self.draw()

    def set_unlocked(self, unlocked):
        self.unlocked = bool(unlocked)
        self.cancel()


class LockPage(Page):
    def __init__(self, app):
        super().__init__(app.canvas, "lock")
        self.app, self.entered = app, []
        directions = [
            ("up", "↑", 96), ("left", "←", 192),
            ("right", "→", 288), ("down", "↓", 384),
        ]
        for direction, symbol, x in directions:
            self.widgets.append(SquareButton(
                self.canvas, self.tag, x, 180, 80, symbol,
                lambda d=direction: self.input_direction(d), font_size=28))
        self.progress = self.canvas.create_text(
            33, 66, text=f"0 / {len(UNLOCK_CODE)}", fill=ACCENT,
            font=("DejaVu Sans", 15, "bold"), tags=(self.tag,))

    def on_enter(self):
        self.entered.clear()
        self.update_progress()

    def update_progress(self, color=ACCENT):
        self.canvas.itemconfigure(
            self.progress, text=f"{len(self.entered)} / {len(UNLOCK_CODE)}",
            fill=color)

    def input_direction(self, direction):
        self.entered.append(direction)
        self.update_progress()
        if len(self.entered) == len(UNLOCK_CODE):
            if tuple(self.entered) == UNLOCK_CODE:
                self.app.go("home", reset=True)
            else:
                self.entered.clear()
                self.update_progress("#ff9a9a")


class NavPage(Page):
    def __init__(self, app, name, title, buttons):
        super().__init__(app.canvas, name)
        self.canvas.create_text(
            27, 81, anchor="w", text=title, fill=TEXT,
            font=("DejaVu Sans", 14, "bold"), tags=(self.tag,))
        for spec in buttons:
            x, label, color, command = spec[:4]
            icon_path = spec[4] if len(spec) > 4 else None
            self.widgets.append(SquareButton(
                self.canvas, self.tag, x, 185, 120, label, command,
                color=color, font_size=12 if len(label) > 7 else 16,
                icon_path=icon_path))


class TogglePage(Page):
    def __init__(self, app, name, title, device):
        super().__init__(app.canvas, name)
        self.app, self.device = app, device
        self.canvas.create_text(
            27, 81, anchor="w", text=title, fill=TEXT,
            font=("DejaVu Sans", 14, "bold"), tags=(self.tag,))
        self.button = SquareButton(
            self.canvas, self.tag, 240, 185, 120, "OFF", self.toggle,
            color="#65405a", font_size=24)
        self.widgets.append(self.button)

    def on_enter(self):
        enabled = self.app.devices.get_state(self.device)
        self.button.label_text = "ON" if enabled else "OFF"
        self.button.color = "#24574f" if enabled else "#65405a"
        self.button.draw(False)

    def toggle(self):
        enabled = self.app.devices.get_state(self.device)
        self.app.devices.set_state(self.device, not enabled)
        self.on_enter()


class SliderPage(Page):
    def __init__(self, app, name, title, device, time=5000):
        super().__init__(app.canvas, name)
        self.time = time
        self.app, self.device = app, device
        self.canvas.create_text(
            27, 81, anchor="w", text=title, fill=TEXT,
            font=("DejaVu Sans", 14, "bold"), tags=(self.tag,))
        self.slider = UnlockSlider(
            self.canvas, self.tag, self.unlock, self.relock,self.time)
        self.widgets.append(self.slider)

    def on_enter(self): self.update_slider()
    def on_leave(self): self.slider.cancel()

    def unlock(self):
        self.app.devices.unlock_for(
            self.device, milliseconds=self.time, on_lock=self.update_slider)
        self.update_slider()

    def relock(self):
        self.app.devices.set_state(self.device, False)
        self.update_slider()

    def update_slider(self):
        self.slider.set_unlocked(self.app.devices.get_state(self.device))
