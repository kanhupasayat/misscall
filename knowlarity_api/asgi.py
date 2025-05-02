# knowlarity_api/asgi.py

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import calllogs.routing  # Make sure this matches your app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowlarity_api.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            calllogs.routing.websocket_urlpatterns
        )
    ),
})
