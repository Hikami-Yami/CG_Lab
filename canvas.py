from model import Model
from colors import *
from render import render


def r_matrix(alpha, beta, gamma):
    ca, sa = np.cos(alpha), np.sin(alpha)
    cb, sb = np.cos(beta), np.sin(beta)
    cg, sg = np.cos(gamma), np.sin(gamma)
    Rx = np.array([[1, 0, 0], [0, ca, sa], [0, -sa, ca]])
    Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    Rz = np.array([[cg, sg, 0], [-sg, cg, 0], [0, 0, 1]])
    return Rx @ Ry @ Rz

class Canvas:
    def __init__(self, x: int, y: int, color=(0,0,0)):
        """Создает холст размером x на y и заполнение цветом color"""
        self.w = x
        self.h = y
        self.color = np.array(ORANGE)
        self.bg_color = np.array(color, dtype=np.uint8)
        self.buffer = np.full(shape=(y, x, 3), fill_value=self.bg_color, dtype=np.uint8)
        self.zbuffer = np.full((y, x), np.inf, dtype=np.float32)

    def clear(self):
        self.buffer[:] = self.bg_color
        self.zbuffer[:] = np.inf

    def render_model(self, model: Model, tx, ty, tz, alpha, beta, gamma, perspective, a):
        min_b, max_b = model.get_bounds()
        R = r_matrix(alpha, beta, gamma)
        center = (min_b + max_b) / 2.0

        v = (model.v - center) @ R.T + np.array([tx, ty, tz])

        self.clear()
        render(v, model.f, self.w, self.h, a, perspective, self.buffer, self.zbuffer, self.color)
