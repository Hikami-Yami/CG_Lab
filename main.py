from math import floor
import numpy as np
from PIL import Image
import time
BACKGROUND_COLOR = (0,0,0)
COLOR = (200,100,50)

class Model:
    def __init__(self, filename: str):
        self.v = []     # Координаты вершин: [[x, y, z], ...]
        self.f = []     # Индексы вершин для граней: [[v0, v1, v2], ...]
        self._load_obj(filename)

    def _load_obj(self, filename: str):
        with open(filename) as file:
            for s in file:
                sp = s.split()
                if sp[0] == 'v':
                    # v.append( [float(x) for x in sp[1:]] )
                    self.v.append([float(sp[1]), float(sp[2]), float(sp[3])])
                if sp[0] == 'f':
                    self.f.append([int(x.split('/')[0]) for x in sp[1:]])

    def get_bounds(self):
        """Возвращает (min_cords, max_cords) для всех вершин."""
        v_np = np.array(self.v)
        min_b = v_np.min(axis=0)
        max_b = v_np.max(axis=0)
        return min_b, max_b

class Canvas:
    def __init__(self, x: int, y: int, color=(0,0,0)):
        """Создает холст размером x на y и заполнение цветом color"""
        self.x = x
        self.y = y
        self.line_color = COLOR
        self.bg_color = np.array(color, dtype=np.uint8)
        self.buffer = np.full(shape=(y, x, 3), fill_value=self.bg_color, dtype=np.uint8)

    def clear(self):
        self.buffer[:] = self.bg_color

    def save(self, filename: str):
        img = Image.fromarray(self.buffer)
        img.save(filename)

    def set_pixel(self, x: int, y: int):
        """Рисует пиксель с защитой от выхода за границы холста."""
        if 0 <= x < self.x and 0 <= y < self.y:
            self.buffer[y, x] = self.line_color

    def line(self, x0, y0, x1, y1):
        """Рисует линию от начальной точки до конечной"""
        dm = max(abs(floor(x0) - floor(x1)), abs(floor(y0) - floor(y1)))
        l = dm + 1
        if l == 1:
            self.buffer[y0, x0] = self.line_color
            return
        else:
            dx = (x1 - x0) / dm
            dy = (y1 - y0) / dm
            x, y = x0, y0

            for i in range(l):
                self.buffer[floor(y), floor(x)] = self.line_color
                x += dx
                y += dy

    def polygon(self, dots):
        """Принимает список координат точек и соединяет их между собой
           dots = [ [x0,y0,z0], [x1,y1,z1], [x2,y2,z2] ]"""
        n = len(dots)
        for i in range(n):
            d0 = dots[i]
            d1 = dots[(i+1)%n]
            self.line( d0[1], d0[0], d1[1], d1[0] )

    def render_wireframe(self, model: Model, padding: int = 40):
        min_b, max_b = model.get_bounds()

        size_x = max_b[0] - min_b[0]
        size_y = max_b[1] - min_b[1]

        center_x = (min_b[0] + max_b[0]) / 2.0
        center_y = (min_b[1] + max_b[1]) / 2.0

        usable_w = self.x - 2 * padding
        usable_h = self.y - 2 * padding

        scale_x = usable_w / size_x if size_x != 0 else 1.0
        scale_y = usable_h / size_y if size_y != 0 else 1.0
        scale = min(scale_x, scale_y)

        def project(v):
            sx = int(round( (v[0] - center_x)*scale + self.x/2.0 ))
            sy = int(round( -(v[1] - center_y)*scale + self.y/2.0 ))
            return sx, sy

        for face in model.f:
            n = len(face)
            for i in range(n):
                v0 = model.v[face[i] - 1]
                v1 = model.v[face[(i + 1) % n] - 1]

                x0, y0 = project(v0)
                x1, y1 = project(v1)
                self.line(x0, y0, x1, y1)


if __name__ == '__main__':
    start = time.process_time()

    canvas = Canvas(5000,5000)
    m = Model('model.obj')
    canvas.render_wireframe(m)
    canvas.save('image.png')

    end = time.process_time()
    execution_time = end - start
    print(f"Время выполнения: {execution_time:.4f} сек")