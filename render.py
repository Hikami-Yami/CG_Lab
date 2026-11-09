from numba import njit
from colors import *

@njit(cache=True)
def calc_bcords(x, y, x0, y0, x1, y1, x2, y2):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2

@njit(cache=True)
def render_polygon(x, y, x0, y0, Z0, x1, y1, Z1, x2, y2, Z2, buffer, zbuffer, color):
    xmin = min(min(x, x0), min(x1, x2))
    ymin = min(min(y, y0), min(y1, y2))
    xmax = max(max(0, x0), max(x1, x2))
    ymax = max(max(0, y0), max(y1, y2))

    if ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)) == 0:
        return

    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            l0, l1, l2 = calc_bcords(x, y, x0, y0, x1, y1, x2, y2)
            if l0 >= 0 and l1 >= 0 and l2 >= 0:
                z = l0 * Z0 + l1 * Z1 + l2 * Z2
                if z < zbuffer[y, x]:
                    buffer[y, x] = color
                    zbuffer[y, x] = z

@njit(cache=True)
def render(v, f, x, y, scale, center_x, center_y, buffer, zbuffer, clr):
    def project(v):
        sx = int(round((v[0] - center_x) * scale + x / 2.0))
        sy = int(round(-(v[1] - center_y) * scale + y / 2.0))
        return sx, sy

    for face in f:
        n = len(face)
        v0 = v[face[0]]
        v1 = v[face[1]]
        v2 = v[face[2]]

        px0, py0 = project(v0)
        px1, py1 = project(v1)
        px2, py2 = project(v2)

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

        nx = a[1] * b[2] - a[2] * b[1]
        ny = a[2] * b[0] - a[0] * b[2]
        nz = a[0] * b[1] - a[1] * b[0]

        lx = 0.0
        ly = 0.0
        lz = 1.0
        cos = ( nx*lx + ny*ly + nz*lz ) / (np.sqrt(nx*nx + ny*ny + nz*nz) * np.sqrt(lx*lx + ly*ly + lz*lz))


        if cos < 0:
            color = -cos * clr
            render_polygon(x, y, px0, py0, Z0, px1, py1, Z1, px2, py2, Z2, buffer, zbuffer, color)