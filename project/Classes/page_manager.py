"""The same Page/PageManager interface as the original prototype."""


class Page:
    def __init__(self, canvas, name):
        self.canvas = canvas
        self.tag = f"page:{name}"
        self.widgets = []

    def show(self):
        self.canvas.itemconfigure(self.tag, state="normal")
        self.on_enter()

    def hide(self):
        self.on_leave()
        self.canvas.itemconfigure(self.tag, state="hidden")

    def on_enter(self):
        pass

    def on_leave(self):
        pass


class PageManager:
    def __init__(self):
        self.pages = {}
        self.current = None
        self.history = []

    def add(self, name, page):
        self.pages[name] = page
        page.hide()

    def show(self, name, remember=True):
        if name not in self.pages:
            raise KeyError(f"Unknown page: {name}")
        if name == self.current:
            return
        if self.current is not None:
            self.pages[self.current].hide()
            if remember:
                self.history.append(self.current)
        self.current = name
        self.pages[name].show()

    def back(self):
        if self.history:
            self.show(self.history.pop(), remember=False)

    def reset_to(self, name):
        self.history.clear()
        self.show(name, remember=False)
