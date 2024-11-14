import logging
import os
import time

import cv2
import numpy as np

logger = logging.getLogger('multiscale')


def get_ENV_PARAM(var, DEFAULT) -> str:
    ENV = os.environ.get(var)
    if ENV:
        logger.info(f'Found ENV value for {var}: {ENV}')
    else:
        ENV = DEFAULT
        logger.warning(f"Didn't find ENV value for {var}, default to: {DEFAULT}")
    return ENV


# def get_local_ip():
#     interfaces = netifaces.interfaces()
#     for interface in interfaces:
#         ifaddresses = netifaces.ifaddresses(interface)
#         if netifaces.AF_INET in ifaddresses:
#             for addr in ifaddresses[netifaces.AF_INET]:
#                 ip = addr.get('addr')
#                 if ip and ip.startswith('192.168'):
#                     return ip
#     return None

def highlight_qr_codes(frame, decoded_objects):
    for obj in decoded_objects:
        points = obj.polygon
        if len(points) == 4:
            pts = np.array(points, dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (0, 255, 0), 4)

        qr_data = obj.data.decode('utf-8')
        qr_type = obj.type
        text = f"{qr_type}: {qr_data}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return frame


def print_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000.0
        logger.info(f"{func.__name__} took {execution_time_ms:.0f} ms to execute")
        print(f"{func.__name__} took {execution_time_ms:.0f} ms to execute")
        return result

    return wrapper


class FPS_:
    def __init__(self, max_fps=300, sliding_window=5):
        self.prev_time = 0
        self.new_time = 0

        self.time_store = Cyclical_Array(max_fps)
        self.fps_store = Cyclical_Array(sliding_window)

    def tick(self) -> None:
        self.time_store.put(time.time())

    # @print_execution_time
    def get_fps(self) -> int:
        current_time = time.time()
        recent_timestamps = [t for t in self.time_store.data if current_time - t <= 1]
        return len(recent_timestamps)

    def get_balanced_fps(self) -> int:
        self.fps_store.put(self.get_fps())
        return int(self.fps_store.get_average())


class Cyclical_Array:
    def __init__(self, size):
        self.data = np.zeros(size, dtype=object)
        self.index = 0
        self.size = size

    def put(self, item):
        self.data[self.index % self.size] = item
        self.index = self.index + 1

    def get_average(self):
        # print(self.data, np.mean(self.data, dtype=np.float64))
        return np.mean(self.data, dtype=np.float64)

def convert_prom_multi(raw_result, item_name="__name__", decimal=False):
    return [(item['metric'][item_name], (float if decimal else int) (item['value'][1])) for item in raw_result]

def filter_tuple(tuple, name, index):
    return next((item for item in tuple if item[index] == name), None)