
import os
import cv2
from threading import Thread

import utils


class VideoReader:
    def __init__(self, stream_id=0):
        # self.stream_id = stream_id  # default is 0 for primary camera

        # opening video capture stream
        # self.vcap = cv2.VideoCapture(self.stream_id)

        ROOT = os.path.dirname(__file__)
        self.video_path = ROOT + "/data/QR_Video.mp4"
        self.frame_count = 1
        self.last_frame_read = False

        self.vcap = cv2.VideoCapture(self.video_path)
        if self.vcap.isOpened() is False:
            print("[Exiting]: Error accessing webcam stream.")
            exit(0)

        # reading a single frame from vcap stream for initializing
        self.grabbed, self.frame = self.vcap.read()
        if self.grabbed is False:
            print('[Exiting] No more frames to read')
            exit(0)  # self.stopped is set to False when frames are being read from self.vcap stream

        self.stopped = True  # reference to the thread for reading next available frame from input stream
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True  # daemon threads keep running in the background while the program is executing

    # method for starting the thread for grabbing next available frame in input stream
    def start(self):
        self.stopped = False
        self.t.start()  # method for reading next frame

    def update(self):
        while not self.stopped:
            if self.last_frame_read:

                if self.frame_count >= self.vcap.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.frame_count = 1
                    self.vcap.set(cv2.CAP_PROP_POS_FRAMES, 0)

                self.grabbed, self.frame = self.vcap.read()
                self.frame_count += 1

                self.last_frame_read = False

        self.vcap.release()  # method for returning latest read frame

    def read(self):
        self.last_frame_read = True
        return self.frame

    # @utils.print_execution_time # Takes < 1ms, which I can hardly imagine
    def get_buffer_size_n(self, size):
        buffer = []
        while len(buffer) < size:
            frame = self.read()
            buffer.append(frame)

        return buffer

    def stop(self):
        self.stopped = True



# class WebcamStream:
#     def __init__(self, stream_id=0):
#         self.stream_id = stream_id  # default is 0 for primary camera
#
#         # opening video capture stream
#         self.vcap = cv2.VideoCapture(self.stream_id)
#         if self.vcap.isOpened() is False:
#             print("[Exiting]: Error accessing webcam stream.")
#             exit(0)
#         fps_input_stream = int(self.vcap.get(5))
#         print("FPS of webcam hardware/input stream: {}".format(fps_input_stream))
#
#         # reading a single frame from vcap stream for initializing
#         self.grabbed, self.frame = self.vcap.read()
#         if self.grabbed is False:
#             print('[Exiting] No more frames to read')
#             exit(0)  # self.stopped is set to False when frames are being read from self.vcap stream
#         self.stopped = True  # reference to the thread for reading next available frame from input stream
#         self.t = Thread(target=self.update, args=())
#         self.t.daemon = True  # daemon threads keep running in the background while the program is executing
#
#     # method for starting the thread for grabbing next available frame in input stream
#     def start(self):
#         self.stopped = False
#         self.t.start()  # method for reading next frame
#
#     def update(self):
#         while True:
#             if self.stopped is True:
#                 break
#             self.grabbed, self.frame = self.vcap.read()
#             if self.grabbed is False:
#                 print('[Exiting] No more frames to read')
#                 self.stopped = True
#                 break
#         self.vcap.release()  # method for returning latest read frame
#
#     def read(self):
#         return self.frame  # method called to stop reading frames
#
#     def stop(self):
#         self.stopped = True  # initializing and starting multi-threaded webcam capture input stream
#
#
# webcam_stream = WebcamStream(stream_id=0)  # stream_id = 0 is for primary camera
# webcam_stream.start()  # processing frames in input stream
# num_frames_processed = 0
# start = time.time()
# while True:
#     if webcam_stream.stopped is True:
#         break
#     else:
#         frame = webcam_stream.read()  # adding a delay for simulating time taken for processing a frame
#     delay = 0.03  # delay value in seconds. so, delay=1 is equivalent to 1 second
#     time.sleep(delay)
#     num_frames_processed += 1
#     cv2.imshow('frame', frame)
#     key = cv2.waitKey(1)
#     if key == ord('q'):
#         break
# end = time.time()
# webcam_stream.stop()  # stop the webcam stream# printing time elapsed and fps
# elapsed = end - start
# fps = num_frames_processed / elapsed
# print("FPS: {} , Elapsed Time: {} , Frames Processed: {}".format(fps, elapsed,
#                                                                  num_frames_processed))  # closing all windows
# cv2.destroyAllWindows()
