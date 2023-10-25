from channels.generic.websocket import AsyncWebsocketConsumer
from dehaze import LWAED
from PIL import Image
import io

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        self.dehaze = LWAED()
        await self.accept()
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data=None, bytes_data=None):
        processed_frame = self.dehaze.realtime_process(bytes_data)
        bytes_io = io.BytesIO()
        processed_frame.save(bytes_io, format='JPEG')
        bytes_data = bytes_io.getvalue()

        await self.send(bytes_data=bytes_data)



