# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Yeh ek temporary in-memory storage hai. Production ke liye Redis use karein.
marked_data = {}

class CallCopyConsumer(AsyncWebsocketConsumer):
    # Step 1: Naya user connect hota hai
    async def connect(self):
        self.room_group_name = "copy_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Naye client ko saari purani copied calls ki history bhej do
        for number, time in marked_data.items():
            await self.send(text_data=json.dumps({
                "number": number,
                "time": time
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Step 4: Frontend se copy ka signal receive karna
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            number = data["number"]
            time = data["time"]

            # In-memory storage update karna
            marked_data[number] = time

            # Group ke sabhi members ko yeh event broadcast karna
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_copy_event", # Yeh function neeche hai
                    "number": number,
                    "time": time
                }
            )
        except (json.JSONDecodeError, KeyError):
            await self.send(text_data=json.dumps({"error": "Invalid data format"}))

    # Step 5: Group ke sabhi members ko message bhejna
    async def send_copy_event(self, event):
        number = event["number"]
        time = event["time"]

        # Har client ke browser ko final data bhejna
        await self.send(text_data=json.dumps({
            "number": number,
            "time": time
        }))
