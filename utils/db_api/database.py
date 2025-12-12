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
            db=env.str('MYSQL_NAME'),
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


    async def add_product(self, group_name, group_description, group_price,
                          group_url,group_status,group_video):
        query = """
            INSERT INTO products(title, description, video_url, group_url, price, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
        await self.execute(query,
                           (
                               group_name, group_description, group_video,
                               group_url, group_price, group_status,
                               datetime.now().date(), datetime.now()
                           )
                    )

    async def update_product(self, product_id, group_name, group_description, group_price,
                          group_url,group_status,group_video):
        query = """
            UPDATE products
            SET title=%s, description=%s, video_url=%s, group_url=%s, price=%s, is_active=%s, updated_at=%s
            WHERE id=%s
            """
        await self.execute(query,
                           (
                               group_name, group_description, group_video,
                               group_url, group_price, group_status,
                               datetime.now(), product_id
                           )
                    )

    async def get_products(self):
        query = """
            SELECT id, title FROM products
        """

        return await self.execute(query=query, fetchall=True)


    async def get_product(self, product_id):
        query = """
            SELECT * FROM products WHERE id=%s
        """
        return await self.execute(query, (product_id, ), fetchone=True)


    async def get_active_products(self):
        query = """
            SELECT id, title FROM products WHERE is_active='active'
        """

        return await self.execute(query, fetchall=True)


    async def delete_product(self, product_id):
        query = """
            DELETE FROM products WHERE id=%s
        """

        await self.execute(query, (product_id, ))


    # User functions ---------------------------------------------------------------------------


    async def add_user(self, fullname, phone_number, tg_id):
        query = """
            INSERT INTO users(fullname, phone_number, tg_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        await self.execute(query,
                           (
                            fullname, phone_number,
                            tg_id, datetime.now().date()
                            )
                        )


    async def get_user_by_tg_id(self, tg_id):
        query = """
            SELECT id, fullname FROM users WHERE tg_id=%s
        """

        return await self.execute(query, (tg_id, ), fetchone=True)



    async def add_order(self, user_id, product_id, paid_status):
        query = """
            INSERT INTO orders(user_id, product_id, is_paid, created_at)
            VALUES(%s, %s, %s, %s)
        """

        await self.execute(query, (user_id, product_id, paid_status, datetime.now().date()))


    async def get_user_paid_orders(self, user_id):
        query = """
            SELECT p.id, p.title
            FROM products p
            JOIN orders o ON p.id = o.product_id
            WHERE o.user_id = %s
              AND o.is_paid = 'is_paid';
        """
        return await self.execute(query, (user_id,), fetchall=True)


    async def get_user_order(self, user_id, order_id):
        query = """
            SELECT * FROM orders 
            WHERE user_id=%s
            AND product_id=%s
        """

        return await self.execute(query, (user_id, order_id), fetchone=True)

