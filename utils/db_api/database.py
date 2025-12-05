from datetime import datetime

import aiomysql
import asyncio
from environs import Env

env = Env()
env.read_env('./envs/.env')


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        # Create the connection pool
        self.pool = await aiomysql.create_pool(
            host=env.str('MYSQL_HOST'),
            port=env.int('MYSQL_PORT'),
            user=env.str('MYSQL_USER'),
            password=env.str('MYSQL_PASSWORD'),
            db=env.str('MYSQL_DATABASE'),
            autocommit=True
        )

    async def execute(self, query, args: tuple = (), fetchone=False, fetchall=False):
        if self.pool is None:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                if fetchone:
                    return await cur.fetchone()
                elif fetchall:
                    return await cur.fetchall()
                else:
                    return None


