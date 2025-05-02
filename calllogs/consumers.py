import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Global list to store all marked numbers
marked_numbers = []

class CallCopyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("copy_group", self.channel_name)
        await self.accept()

        # Send all previously marked numbers to the new client
        for number in marked_numbers:
            await self.send(text_data=json.dumps({
                "number": number
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("copy_group", self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            number = data["number"]

            # Add to global list (avoid duplicates if needed)
            marked_numbers.append(number)

            # Broadcast this number to all connected clients
            await self.channel_layer.group_send(
                "copy_group",
                {
                    "type": "send_copy",
                    "number": number
                }
            )
        except (json.JSONDecodeError, KeyError):
            await self.send(text_data=json.dumps({"error": "Invalid data format"}))

    async def send_copy(self, event):
        await self.send(text_data=json.dumps({
            "number": event["number"]
        }))

