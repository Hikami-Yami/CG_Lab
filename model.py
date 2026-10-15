import numpy as np


class Model:
    def __init__(self, filename: str):
        self.v = []     # Координаты вершин: [[x, y, z], ...]
        self.f = []     # Индексы вершин для граней: [[v0, v1, v2], ...]
        self._load_obj(filename)

    def _load_obj(self, filename: str):
        with open(filename) as file:
            for s in file:
                sp = s.split()
                if not sp:
                    continue
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