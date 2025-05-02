from django.urls import path
from .views import AsyncUnattendedMissedCallsView

urlpatterns = [
    path('missed-calls/', AsyncUnattendedMissedCallsView.as_view(), name='missed-calls'),
]
