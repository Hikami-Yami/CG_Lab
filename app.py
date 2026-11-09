import tkinter as tk
from PIL import Image, ImageTk


class App:
    # инициализация параметров
    def __init__(self, model, canvas, win_w=1000, win_h=1000):
        self.model = model
        self.renderer = canvas
        self.root = tk.Tk()
        self.root.geometry(f"{win_w}x{win_h}")
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.focus_set()
        self.canvas.bind('<Configure>', lambda e: self._refit())
        self.root.bind('<Key>', self.on_key)
        self.photo = None
        self.last_full = None
        self.render()


    # реакция на нажатие клавиш
    def on_key(self, event):
        k = event.keysym

        if k == 'Up':
            pass
            # Обработка
        elif k == 'Down':
            pass
            # Обработка
        elif k == 'space':
            Image.fromarray(self.renderer.buffer).save("image.png")
            return 'break'
        else:
            return
        self.render()
        return 'break'

    # рендер
    def render(self):
        self.renderer.render_model(self.model)
        self.last_full = Image.fromarray(self.renderer.buffer)
        self._refit()

    # вспомогательная функция, чтобы поместить картинку в окно
    def _refit(self):
        if self.last_full is None:
            return
        ww = self.canvas.winfo_width()
        wh = self.canvas.winfo_height()
        if ww < 10 or wh < 10:
            return

        s = min(ww / self.renderer.x, wh / self.renderer.y)
        dw = max(1, int(self.renderer.x * s))
        dh = max(1, int(self.renderer.y * s))
        disp = self.last_full.resize((dw, dh), Image.BILINEAR)
        self.photo = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(ww // 2, wh // 2, image = self.photo)

        # запуск программы
    def run(self):
        self.root.mainloop()