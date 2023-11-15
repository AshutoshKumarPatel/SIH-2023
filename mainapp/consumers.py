from channels.generic.websocket import AsyncWebsocketConsumer
from dehaze import RealtimeWorker
from PIL import Image
import io
import asyncio
import multiprocessing

TASK_QUEUE = multiprocessing.JoinableQueue()
PROCESS = None

class VideoConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.return_dict = {}

    async def connect(self):
        global PROCESS
        self.manager = multiprocessing.Manager()
        self.return_dict = self.manager.dict()
        
        if PROCESS is None or not PROCESS.is_alive():
            PROCESS = multiprocessing.Process(target=RealtimeWorker, args=(TASK_QUEUE, self.return_dict))
            PROCESS.start()
        await self.accept()
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data=None, bytes_data=None):
        TASK_QUEUE.put(bytes_data)

        while 'result' not in self.return_dict:
            await asyncio.sleep(0.1)
        processed_frame = self.return_dict['result']
        bytes_io = io.BytesIO()
        processed_frame.save(bytes_io, format='JPEG')
        bytes_data = bytes_io.getvalue()

        await self.send(bytes_data=bytes_data)



