import tkinter as tk
from PIL import Image, ImageTk

FILL = 0.6          # какую долю окна занимает модель на старте
DIST_K = 3.0        # стартовое расстояние
STEP_K = 0.3        # шаг сдвига
ANGLE_STEP = 0.4    # шаг поворота

class App:
    # инициализация параметров
    def __init__(self, model, canvas, win_w=1000, win_h=1000):
        self.model = model
        self.renderer = canvas

        min_b, max_b = model.get_bounds()
        self.size = float((max_b - min_b).max())
        self.tz0 = DIST_K * self.size
        self.step = STEP_K * self.size
        self.reset_state()

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

    def reset_state(self):
        self.tx, self.ty, self.tz = 0.0, 0.0, self.tz0
        self.beta = 0.0
        self.perspective = True

    def _scale(self):
        a = FILL * min(self.renderer.w, self.renderer.h) / self.size
        if self.perspective:
            a *= self.tz0
        return a

    # реакция на нажатие клавиш
    def on_key(self, event):
        k = event.keysym.lower()

        if   k == 'left':  self.beta -= ANGLE_STEP
        elif k == 'right': self.beta += ANGLE_STEP
        elif k == 'a':     self.tx -= self.step
        elif k == 'd':     self.tx += self.step
        elif k == 'w':     self.ty += self.step
        elif k == 's':     self.ty -= self.step
        elif k == 'up':    self.tz -= self.step     # ближе
        elif k == 'down':  self.tz += self.step     # дальше
        elif k == 'p':     self.perspective = not self.perspective
        elif k == 'r':     self.reset_state()
        elif k == 'space':
            Image.fromarray(self.renderer.buffer).save("image.png")
            return 'break'
        else:
            return
        self.render()
        return 'break'


    def render(self):
        self.renderer.render_model(
            self.model, self.tx, self.ty, self.tz,
            0.0, self.beta, 0.0,
            self.perspective, self._scale())
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

        s = min(ww / self.renderer.w, wh / self.renderer.h)
        dw = max(1, int(self.renderer.w * s))
        dh = max(1, int(self.renderer.h * s))
        disp = self.last_full.resize((dw, dh), Image.BILINEAR)
        self.photo = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(ww // 2, wh // 2, image = self.photo)

        # запуск программы
    def run(self):
        self.root.mainloop()