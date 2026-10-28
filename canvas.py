from PIL import Image
import numpy as np
from math import floor
from model import Model
from colors import *


class Canvas:
    def __init__(self, x: int, y: int, color=(0,0,0)):
        """Создает холст размером x на y и заполнение цветом color"""
        self.x = x
        self.y = y
        self.clr = np.array(COLOR)
        self.color = np.array(COLOR)
        self.bg_color = np.array(color, dtype=np.uint8)
        self.buffer = np.full(shape=(y, x, 3), fill_value=self.bg_color, dtype=np.uint8)
        self.zbuffer = np.full((y, x), np.inf, dtype=np.float32)

    def clear(self):
        self.buffer[:] = self.bg_color
    def save(self, filename: str):
        img = Image.fromarray(self.buffer)
        img.save(filename)

#region Not used
    def set_pixel(self, x: int, y: int):
        """Рисует пиксель с защитой от выхода за границы холста."""
        if 0 <= x < self.x and 0 <= y < self.y:
            self.buffer[y, x] = self.color

    def line(self, x0, y0, x1, y1):
        """Рисует линию от начальной точки до конечной"""
        dm = max(abs(floor(x0) - floor(x1)), abs(floor(y0) - floor(y1)))
        l = dm + 1
        if l == 1:
            self.buffer[y0, x0] = self.color
            return
        else:
            dx = (x1 - x0) / dm
            dy = (y1 - y0) / dm
            x, y = x0, y0

            for i in range(l):
                self.buffer[floor(y), floor(x)] = self.color
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
        """Рисует каркас модели с отступом по краям,
                автоматически масштабируя и центрируя координаты вершин"""
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
#endregion

    def calc_bcords(self, x, y, x0, y0, x1, y1, x2, y2):
        lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
        lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
        lambda2 = 1.0 - lambda0 - lambda1
        return lambda0, lambda1, lambda2

    def render_polygon(self, x0, y0, Z0, x1, y1, Z1, x2, y2, Z2, cos=1):
        xmin = min(self.x, x0, x1, x2)
        ymin = min(self.y, y0, y1, y2)
        xmax = max(0, x0, x1, x2)
        ymax = max(0, y0, y1, y2)

        if ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)) == 0:
            return

        for x in range(xmin, xmax):
            for y in range(ymin, ymax):
                l0,l1,l2 = self.calc_bcords(x, y, x0, y0, x1, y1, x2, y2)
                if l0 >= 0 and l1 >= 0 and l2 >= 0:
                    z = l0*Z0 + l1*Z1 + l2*Z2
                    if z < self.zbuffer[y, x]:
                        self.buffer[y,x] = self.color
                        self.zbuffer[y, x] = z


    def render_model(self, model: Model, padding: int = 40):
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
            sx = int(round((v[0] - center_x) * scale + self.x / 2.0))
            sy = int(round(-(v[1] - center_y) * scale + self.y / 2.0))
            return sx, sy

        for face in model.f:
            n = len(face)
            v0 = model.v[face[0] - 1]
            v1 = model.v[face[1] - 1]
            v2 = model.v[face[2] - 1]

            x0, y0 = project(v0)
            x1, y1 = project(v1)
            x2, y2 = project(v2)

            X0 = -v0[0]
            Y0 = v0[1]
            Z0 = -v0[2]
            X1 = -v1[0]
            Y1 = v1[1]
            Z1 = -v1[2]
            X2 = -v2[0]
            Y2 = v2[1]
            Z2 = -v2[2]
            a = np.array([X1 - X2, Y1 - Y2, Z1 - Z2])
            b = np.array([X1 - X0, Y1 - Y0, Z1 - Z0])
            n = np.cross(a, b)
            l = np.array([0,0,1])
            cos = np.dot(n,l) / (np.linalg.norm(n) * np.linalg.norm(l))

            if cos < 0:
                self.color = -cos * self.clr
                self.render_polygon(x0, y0, Z0, x1, y1, Z1, x2, y2, Z2)