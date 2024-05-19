from django.urls import path
from .consumers import WebScrapingConsumer

websocket_urlpatterns = [
    path('web_scraping/', WebScrapingConsumer.as_asgi()),
]
