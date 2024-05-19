import json
from channels.generic.websocket import AsyncWebsocketConsumer
from products.utils import ProductScraping
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from products.api.serializers import ProductLinkSerializer, CartSerializer
from django.core.cache import cache
from asgiref.sync import sync_to_async

class WebScrapingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = None
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization')

        if auth_header:
            token = auth_header.decode('utf-8').split()[1]
            if token:
                self.user = await self.get_user_by_token(token)

        await self.accept()

    @database_sync_to_async
    def get_user_by_token(self, token):
        try:
            return Token.objects.get(key=token).user
        except ObjectDoesNotExist:
            return None    

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            return await self.send_error('Not json data')

        serializer = ProductLinkSerializer(data=data)
        if not serializer.is_valid():
            return await self.send_error(serializer.errors)

        product_link = serializer.validated_data['product_link']
        product_market = serializer.data.get('market')
        cache_key = f'product_cache_{product_link}'

        product_cached = await self.get_cached_product(cache_key)
        if product_cached:
            await self.send_product_data(product_cached)
            await self.save_product_data(product_cached)
        else:
            await self.scrape_and_send_product_data(product_link, product_market, cache_key)

    async def get_cached_product(self, cache_key):
        return await sync_to_async(cache.get)(cache_key)

    async def send_error(self, error):
        await self.send(text_data=json.dumps({'error': error}))

    async def send_product_data(self, product_data):
        await self.send(text_data=json.dumps(product_data))

    async def save_product_data(self, product_data):
        product_cached_serializer = CartSerializer(data=product_data)
        if await sync_to_async(product_cached_serializer.is_valid)():
            await sync_to_async(product_cached_serializer.save)()
        else:
            await self.send_error(product_cached_serializer.errors)

    async def scrape_and_send_product_data(self, product_link, product_market, cache_key):
        product = ProductScraping(product_link)
        if await sync_to_async(product.is_work)():
            product_data = product.data
            await self.send_product_data(product_data)
            if self.user:
                product_data.update({'user': self.user.id})
                product_data.update({'market': product_market})
                await sync_to_async(cache.set)(cache_key, product_data, timeout=30)  # Cache result for 30 sec
                await self.save_product_data(product_data)
        else:
            await self.send_error(product.errors)
