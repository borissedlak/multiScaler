import concurrent.futures
import logging
import threading
import time
from random import randint

import cv2
from prometheus_client import start_http_server, Gauge
from pyzbar.pyzbar import decode

import utils
from VehicleService import VehicleService
from VideoReader import VideoReader

DEVICE_NAME = utils.get_ENV_PARAM("DEVICE_NAME", "Unknown")
logger = logging.getLogger("multiscale")

start_http_server(8000)
fps = Gauge('fps', 'Current processing FPS', ['service_id', 'metric_id'])
pixel = Gauge('pixel', 'Current processing FPS', ['service_id', 'metric_id'])
energy = Gauge('energy', 'Current processing FPS', ['service_id', 'metric_id'])
cores = Gauge('cores', 'Current processing FPS', ['service_id', 'metric_id'])
# in_time_fuzzy = Gauge('in_time_fuzzy', 'Fuzzy SLO fulfillment', ['service_id', 'metric_id'])


class QrDetector(VehicleService):
    def __init__(self, show_results=False):
        super().__init__()
        self._terminated = True
        self._running = False
        self.service_conf = {'pixel': 800, 'fps': 20}
        self.number_threads = 2
        self.fps = utils.FPS_()

        self.webcam_stream = VideoReader()
        self.webcam_stream.start()

        # self.device_metric_reporter = DeviceMetricReporter(leader_ip, gpu_available=False)
        # self.service_metric_reporter = ServiceMetricReporter("QR")

        self.show_result = show_results

    def process_one_iteration(self, params, frame) -> None:

        # global frame_count
        target_height, source_fps = int(params['pixel']), int(params['fps'])

        original_width, original_height = frame.shape[1], frame.shape[0]
        ratio = original_height / target_height

        frame = cv2.resize(frame, (int(original_width / ratio), int(original_height / ratio)))

        start_time = time.time()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray)
        combined_img = utils.highlight_qr_codes(frame, decoded_objects)

        if self.show_result:
            cv2.imshow("Detected Objects", combined_img)

        processing_time = (time.time() - start_time) * 1000.0
        # pixel = combined_img.shape[0]

        # TODO: These are the metrics that can be submitted to Prometheus

        # service_blanket = self.service_metric_reporter.create_metrics(processing_time, source_fps, pixel=pixel)
        # device_blanket = self.device_metric_reporter.create_metrics()
        # merged_metrics = utils.merge_single_dicts(service_blanket["metrics"], device_blanket["metrics"])

        # frame_count += 1
        # print(processing_time, params)

    def process_loop(self):

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.number_threads) as executor:
            while self._running:

                buffer = self.webcam_stream.get_buffer_size_n(self.number_threads)
                future_dict = {executor.submit(self.process_one_iteration, self.service_conf, frame): frame
                               for frame in buffer}

                for future in concurrent.futures.as_completed(future_dict):
                    number = future_dict[future]
                    try:
                        result = future.result()
                        # print("ready")
                        self.fps.tick()
                    except Exception as e:
                        print(f"Error occurred while fetching {number}: {e}")

                # This is only executed once, and not for every frame
                processing_fps = self.fps.get_fps()
                fps.labels(service_id="video", metric_id="fps").set(processing_fps)
                pixel.labels(service_id="video", metric_id="pixel").set(self.service_conf['pixel'])
                energy.labels(service_id="video", metric_id="energy").set(randint(1,20))
                cores.labels(service_id="video", metric_id="cores").set(self.number_threads)
                # in_time_fuzzy.labels(service_id="video", metric_id="in_time").set(
                #     max(1, current_fps) / self.service_conf['fps'])
                # time.sleep(1)

        self._terminated = True
        logger.info("QR Detector stopped")

    def start_process(self):
        self._terminated = False
        self._running = True

        processing_thread = threading.Thread(target=self.process_loop, daemon=True)
        processing_thread.start()
        logger.info("QR Detector started")

    def terminate(self):
        self._running = False

    def change_config(self, config):
        self.service_conf = config
        logger.info(f"QR Detector changed to {config}")

    # TODO: Takes too long with 106ms
    # @utils.print_execution_time
    def change_threads(self, c_threads):
        self.terminate()
        # Wait until it is really terminated and then start new
        while not self._terminated:
            time.sleep(0.01)

        self.number_threads = c_threads
        logger.info(f"QR Detector set to work with {c_threads} threads")

        self.start_process()


if __name__ == '__main__':
    qd = QrDetector(show_results=False)
    qd.start_process()

    while True:
        time.sleep(1000)
