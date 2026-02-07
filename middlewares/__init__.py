import asyncio

from aiogram import Router

from middlewares.throttling import ThrottlingMiddleware

from loader import dp
from .db_middleware import DbSessionMiddleware

# Barcha update turlariga middleware qo'shish
dp.update.middleware(DbSessionMiddleware())

loop = asyncio.get_event_loop()
redis_url = "redis://localhost"  # Redis URL
router = Router()
router.message.middleware(ThrottlingMiddleware(redis_url))
