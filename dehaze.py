#Imports
import io
import cv2
import sys
import time
import ffmpeg
import numpy as np
import multiprocessing

from PIL import Image
from keras.models import load_model
from keras.optimizers import Adam
from tqdm import tqdm
from pathlib import Path

class LWAED:
    def __init__(self) -> None:
        self.light_model_path = 'models/LCA_640.360_76k_white_dataset.h5'
        self.dark_model_path = 'models/LWAED_640.360_78k_v0_black_dataset_finetuned.h5'

        self.light_model = None
        self.dark_model = None

        self.last_used = time.time()

        self.frame_skip = 1
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

    def analyze_image(self, image):
        white_threshold = np.array([101, 101, 101])
        black_threshold = np.array([100, 100, 100])
        
        white_pixels = np.sum(np.all(image > white_threshold, axis=-1))
        black_pixels = np.sum(np.all(image < black_threshold, axis=-1))
        
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

        stream = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(*self.image_size))
        stream = ffmpeg.output(stream, output_file, pix_fmt='yuv420p', vcodec='libx264', r=fps)
        try:
            stream = ffmpeg.run(stream, input=np.array(frames).tobytes(), capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print(e.stderr.decode(), file=sys.stderr)


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
    

def VideoWorker(task_queue):
    L = LWAED()
    while True:
        try:
            input_file, output_file = task_queue.get(timeout=60)
            print(f"Received task: {input_file}, {output_file}")
            print(f"Processing task: {input_file}, {output_file}")
            L.process_video(input_file, output_file)
            print(f"Finished task: {input_file}, {output_file}")
            task_queue.task_done()

        except multiprocessing.queues.Empty:
            print("No tasks received for 1 minute(s), terminating...")
            break

def RealtimeWorker(task_queue, return_dict):
    L = LWAED()
    while True:
        try:
            bytes_data = task_queue.get(timeout=60)
            processed_frame = L.realtime_process(bytes_data)
            try:
                return_dict['result'] = processed_frame
            except BrokenPipeError:
                print("Manager has been closed, terminating...")
                break

        except multiprocessing.queues.Empty:
            print("No tasks received for 1 minute(s), terminating...")
            break

Path('uploads').mkdir(parents=True, exist_ok=True)