#Imports
import io
import cv2
import os
import sys
from queue import Queue
import gc
from keras import backend as K
import threading
import time
import ffmpeg
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from PIL import Image
from keras.utils import load_img, img_to_array
from keras.models import load_model
from keras.optimizers import Adam
from tqdm import tqdm

class LWAED:
    def __init__(self, idle_time=300) -> None:
        self.light_model_path = 'models/LCA_640.360_76k_white_dataset.h5'
        self.dark_model_path = 'models/LWAED_640.360_78k_v0_black_dataset_finetuned.h5'

        self.light_model = None
        self.dark_model = None

        self.frame_skip = 20
        self.idle_time = idle_time
        self.queue = Queue()
        threading.Thread(target=self._manage_model).start()
        self.image_size = (640, 360)
        self._load_model()

    def _load_model(self):
        self.light_model = load_model(self.light_model_path, compile = False)
        self.dark_model = load_model(self.dark_model_path, compile = False)

        opt = Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999)

        self.light_model.compile(optimizer=opt, loss='mse')
        print('loaded light model')
        
        self.dark_model.compile(optimizer=opt, loss='mse')
        print('loaded dark model')

        return self.light_model, self.dark_model
    
    def _manage_model(self):
        while True:
            if not self.queue.empty():
                task = self.queue.get()
                if self.light_model is None or self.dark_model is None:
                    self._load_model()
                input_file, output_file = task['data']
                result = self.process_video(input_file, output_file)
                task['callback']
                self.last_used = time.time()
            elif self.light_model is not None and time.time() - self.last_used > self.idle_time:
                K.clear_session()
                del self.light_model
                del self.dark_model
                gc.collect()
                self.light_model = None
                self.dark_model = None
            time.sleep(1)

    def add_task(self, data, callback):
        self.queue.put({'data': data, 'callback': callback})


    def analyze_image(self, image):
        white_threshold = np.array([101, 101, 101])
        black_threshold = np.array([100, 100, 100])
        
        white_pixels = np.sum(np.all(image > white_threshold, axis=-1))
        black_pixels = np.sum(np.all(image < black_threshold, axis=-1))
        # print(white_pixels, black_pixels)
        
        if white_pixels > black_pixels:
            return 1
        else:
            return 0
    
    def rescale_video(self, input_file, output_file):
        cap = cv2.VideoCapture(input_file)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_file, fourcc, fps, self.image_size)

        for _ in tqdm(range(frame_count)):
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, self.image_size)
            out.write(frame)

        cap.release()
        out.release()

    def process_video(self, input_file, output_file):
        cap = cv2.VideoCapture(input_file)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        frame_counter = 0
        frames = []

        for _ in tqdm(range(frame_count)):
            ret, frame = cap.read()
            if not ret:
                break

            if frame_counter % self.frame_skip == 0:
                frame = cv2.resize(frame, self.image_size)
                model_no = self.analyze_image(frame)
                frame = frame / 255.0

                selected_model = self.light_model if model_no else self.dark_model
                predicted_frame = selected_model.predict(np.expand_dims(frame, axis=0), verbose=0)
                predicted_frame = np.clip(predicted_frame, 0.0, 1.0)
                predicted_frame = (predicted_frame[0] * 255).astype(np.uint8)

                for i in range(self.frame_skip):
                    frames.append(predicted_frame)

            frame_counter += 1

        cap.release()

        stream = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(*self.image_size))
        stream = ffmpeg.output(stream, output_file, pix_fmt='yuv420p', vcodec='libx264', r=fps)
        try:
            stream = ffmpeg.run(stream, input=np.array(frames).tobytes(), capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print(e.stderr.decode(), file=sys.stderr)
            # raise e


    def realtime_process(self, bytes_data):
        frame = Image.open(io.BytesIO(bytes_data))

        frame = np.array(frame)
        frame = cv2.resize(frame, self.image_size)
        frame = frame / 255.0

        predicted_frame = self.light_model.predict(np.expand_dims(frame, axis=0), verbose=False)
        predicted_frame = np.clip(predicted_frame, 0.0, 1.0)
        predicted_frame = (predicted_frame[0] * 255).astype(np.uint8)
        predicted_frame = Image.fromarray(predicted_frame)

        return predicted_frame


if __name__=='__main__':
    input_file = 'uploads/sample1.mp4'
    output_file = 'uploads/sample5.mp4'

    L = LWAED()
    L.add_task((input_file, output_file), 'success')

    # L.process_video('uploads/sample1.mp4', 'uploads/sample6.mp4')
    # L.realtime_process(byte_data)
    # result.show()