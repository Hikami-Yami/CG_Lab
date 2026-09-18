from math import floor
import numpy as np
from PIL import Image

BACKGROUND_COLOR = (0,0,0)
LINES_COLOR = (200,100,50)
SCALE = 9000

def canvas(x,y,color=BACKGROUND_COLOR):
    """Создает холст размером x на y и заполнение цветом color"""
    img_mat = np.zeros((1000, 1000, 3), dtype=np.uint8)
    for i in range(1000):
        for j in range(1000):
            img_mat[i, j] = 0
    return img_mat

def line(img_mat, x0, y0, x1, y1):
    """Рисует линию от начальной точки до конечной"""
    dm = max(abs(floor(x0) - floor(x1)), abs(floor(y0) - floor(y1)))
    l = dm + 1
    if l == 1:
        pass
    else:
        dx = (x1 - x0) / (l - 1)
        dy = (y1 - y0) / (l - 1)
        x, y = x0, y0
        for i in range(l):
            img_mat[floor(x), floor(y)] = LINES_COLOR
            x += dx
            y += dy

def polygon(dots):
    """Принимает список точек и соединяет их между собой"""
    n = len(dots)
    for i in range(n):
        d1 = dots[i]
        d2 = dots[(i+1)%n]
        line(d1[1], d1[0], d2[1], d2[0])


img_mat = canvas(1000,1000)

v = []
f = []
with open('model.obj') as file:
    for s in file:
        sp = s.split()
        if sp[0] == 'v':
            v.append( [float(x) for x in sp[1:]] )
        if sp[0] == 'f':
            n1 = sp[1].split('/')[0]
            n2 = sp[2].split('/')[0]
            n3 = sp[3].split('/')[0]
            f.append( [int(n1), int(n2), int(n3),] )
            #f.append( [ x.split('/')[0] for x in sp[1:]] )


v2 = []
for i in v:
    v2.append([i[0]*SCALE+500, -i[1]*SCALE+920, i[2]*SCALE+500])

for i in v2:
    x,y,z = i
    img_mat[ floor(y), floor(x) ] = [200,100,50]

for i in f:
    dots = [v2[x-1] for x in i]
    polygon(dots)






img = Image.fromarray(img_mat)
img.save('image.png')

