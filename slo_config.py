from typing import NamedTuple

import numpy as np

PW_MAX_CORES = 10
MB = {'variables': ['pixel', 'fps', 'cores'],
      'parameter': ['pixel', 'cores'],
      'slos': [(1.0, False, 0.85),
               (1.0, False, 1.0),
               (10, True, 0.4),
               (1, False, 0.0),
               (1, False, 0.0),
               (1, False, 0.0)]}


class Full_State(NamedTuple):
    pixel: int
    pixel_thresh: int
    fps: float
    fps_thresh: int
    energy: int
    cores: int
    free_cores: int

    def for_tensor(self):
        return [self.pixel / self.pixel_thresh, self.fps / self.fps_thresh, self.cores,
                self.pixel > 100, self.pixel < 2000, self.free_cores > 0]


def calculate_slo_reward(state, slos=MB['slos']):
    fuzzy_slof = []

    for index, value in enumerate(state):
        t, neg, boost = slos[index]

        if neg:
            slo_f = 1 - (value / t)
        else:
            slo_f = (value / t)

        slo_f = np.clip(slo_f, 0.0, 1.10) * boost
        fuzzy_slof.append(slo_f)

    return fuzzy_slof
