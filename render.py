from numba import njit
from colors import *

Z_NEAR = 1e-6

@njit(cache=True)
def calc_bcords(x, y, x0, y0, x1, y1, x2, y2):
    d = ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    if d == 0:
        return -1.0, -1.0, -1.0
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / d
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / d
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2

@njit(cache=True)
def render_polygon(w, h, x0, y0, Z0, x1, y1, Z1, x2, y2, Z2, buffer, zbuffer, color):
    xmin = min(min(w-1, x0), min(x1, x2))
    ymin = min(min(h-1, y0), min(y1, y2))
    xmax = max(max(0, x0), max(x1, x2))
    ymax = max(max(0, y0), max(y1, y2))

    if ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)) == 0:
        return

    for w in range(xmin, xmax + 1):
        for h in range(ymin, ymax):
            l0, l1, l2 = calc_bcords(w, h, x0, y0, x1, y1, x2, y2)
            if l0 >= 0 and l1 >= 0 and l2 >= 0:
                z = l0 * Z0 + l1 * Z1 + l2 * Z2
                if z < zbuffer[h, w]:
                    buffer[h, w] = color
                    zbuffer[h, w] = z

@njit(cache=True)
def project(x, y, z, w, h, a, perspective):
    if perspective:
        px = a * x / z + w / 2.0
        py = -a * y / z + h / 2.0   # минус для переворота по Y
    else:
        px = a * x + w / 2.0
        py = -a * y + h / 2.0
    return int(round(px)), int(round(py))

@njit(cache=True)
def render(v, f, w, h, a, perspective, buffer, zbuffer, clr):

    for face in f:
        n = len(face)
        v0 = v[face[0]]
        v1 = v[face[1]]
        v2 = v[face[2]]
        x0 = v0[0]; y0 = v0[1]; z0 = v0[2]
        x1 = v1[0]; y1 = v1[1]; z1 = v1[2]
        x2 = v2[0]; y2 = v2[1]; z2 = v2[2]

        px0, py0 = project(x0, y0, z0, w, h, a, perspective)
        px1, py1 = project(x1, y1, z1, w, h, a, perspective)
        px2, py2 = project(x2, y2, z2, w, h, a, perspective)

        aс = np.array([x1 - x2, y1 - y2, z1 - z2])
        b = np.array([x1 - x0, y1 - y0, z1 - z0])

        nx = aс[1] * b[2] - aс[2] * b[1]
        ny = aс[2] * b[0] - aс[0] * b[2]
        nz = aс[0] * b[1] - aс[1] * b[0]

        lx = 0.0
        ly = 0.0
        lz = 1.0
        cos = ( nx*lx + ny*ly + nz*lz ) / (np.sqrt(nx*nx + ny*ny + nz*nz) * np.sqrt(lx*lx + ly*ly + lz*lz))

        if perspective and (z0 <= Z_NEAR or z1 <= Z_NEAR or z2 <= Z_NEAR):
            continue

        if cos < 0:
            color = -cos * clr
            render_polygon(w, h, px0, py0, z0, px1, py1, z1, px2, py2, z2, buffer, zbuffer, color)