from datetime import datetime
import aiomysql
from environs import Env


env = Env()
env.read_env('./envs/.env')


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=env.str('MYSQL_HOST'),
            port=env.int('MYSQL_PORT'),
            user=env.str('MYSQL_USER'),
            password=env.str('MYSQL_PASSWORD'),
            db=env.str('MYSQL_DATABASE'),
            autocommit=True,
            minsize=1,
            maxsize=10,
            pool_recycle=1800,
            connect_timeout=10,
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
                return None

    # ==================== PRODUCT FUNCTIONS ====================

    async def add_product(self, title, description, price_1080p, group_url_1080p,
                          price_4k, group_url_4k, is_active, video_url):
        query = """
            INSERT INTO products(title, description, video_url, price_1080p, group_url_1080p,
                                 price_4k, group_url_4k, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        await self.execute(query, (
            title, description, video_url, price_1080p, group_url_1080p,
            price_4k, group_url_4k, is_active, datetime.now().date(), datetime.now()
        ))

    async def update_product(self, product_id, title, description, price_1080p, group_url_1080p,
                             price_4k, group_url_4k, is_active, video_url):
        query = """
            UPDATE products
            SET title=%s, description=%s, video_url=%s, price_1080p=%s, group_url_1080p=%s,
                price_4k=%s, group_url_4k=%s, is_active=%s, updated_at=%s
            WHERE id=%s
        """
        await self.execute(query, (
            title, description, video_url, price_1080p, group_url_1080p,
            price_4k, group_url_4k, is_active, datetime.now(), product_id
        ))

    async def get_products(self):
        query = "SELECT id, title FROM products"
        return await self.execute(query, fetchall=True)

    async def get_product(self, product_id):
        query = "SELECT * FROM products WHERE id=%s"
        return await self.execute(query, (product_id,), fetchone=True)

    async def get_product_by_name(self, pr_name):
        query = "SELECT * FROM products WHERE title=%s"
        return await self.execute(query, (pr_name,), fetchone=True)

    async def get_active_products(self):
        query = "SELECT * FROM products WHERE is_active='active' AND (price_1080p > 0 OR price_4k > 0)"
        return await self.execute(query, fetchall=True)

    async def get_free_products(self):
        query = "SELECT id, title FROM products WHERE price_1080p=0 AND price_4k=0 AND is_active='active'"
        return await self.execute(query, fetchall=True)

    async def delete_product(self, product_id):
        await self.execute("DELETE FROM products WHERE id=%s", (product_id,))

    # ==================== USER FUNCTIONS ====================

    async def add_user(self, fullname, phone_number, tg_id):
        query = """
            INSERT INTO users(fullname, phone_number, tg_id, created_at)
            VALUES (%s, %s, %s, %s)
        """
        await self.execute(query, (fullname, phone_number, tg_id, datetime.now().date()))

    async def update_user(self, fullname, phone_number, tg_id):
        query = "UPDATE users SET fullname=%s, tg_id=%s WHERE phone_number=%s"
        await self.execute(query, (fullname, tg_id, phone_number))

    async def get_user_by_tg_id(self, tg_id):
        query = "SELECT id, fullname FROM users WHERE tg_id=%s"
        return await self.execute(query, (tg_id,), fetchone=True)

    async def get_user_by_phone(self, phone):
        query = "SELECT id, fullname, tg_id FROM users WHERE phone_number=%s"
        return await self.execute(query, (phone,), fetchone=True)

    async def add_user_by_admin(self, phone_number, cost: float, groups: list, resolution: str):
        user_add_query = "INSERT INTO users(phone_number, created_at) VALUES (%s, %s)"
        await self.execute(user_add_query, (phone_number, datetime.now().date()))

        user_id = (await self.get_user_by_phone(phone_number))[0]
        count = len(groups)

        order_add_query = """
            INSERT INTO orders(user_id, cost, count, resolution, payment_method, is_paid, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        await self.execute(order_add_query, (user_id, cost, count, resolution, "cash", 1, datetime.now().date()))

        order_id = (await self.execute("SELECT LAST_INSERT_ID()", fetchone=True))[0]

        for product_id in groups:
            await self.execute(
                "INSERT INTO orders_product(order_id, product_id) VALUES (%s, %s)",
                (order_id, product_id)
            )

    # ==================== ORDER FUNCTIONS ====================

    async def add_order(self, user_id, product_id, cost, resolution):
        query = """
            INSERT INTO orders(user_id, cost, count, resolution, payment_method, is_paid, created_at)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
        """
        await self.execute(query, (user_id, cost, 1, resolution, 'cash', 1, datetime.now().date()))

        order_id = (await self.execute("SELECT LAST_INSERT_ID()", fetchone=True))[0]
        await self.execute(
            "INSERT INTO orders_product(order_id, product_id) VALUES (%s, %s)",
            (order_id, product_id)
        )

    async def get_user_paid_orders(self, user_id, resolution=None):
        """Foydalanuvchining to'langan buyurtmalarini olish"""
        if resolution:
            query = """
                SELECT p.id, p.title, o.resolution
                FROM products p
                JOIN orders_product op ON p.id = op.product_id
                JOIN orders o ON op.order_id = o.id
                WHERE o.user_id = %s AND o.is_paid = True AND o.resolution = %s
            """
            return await self.execute(query, (user_id, resolution), fetchall=True)
        else:
            query = """
                SELECT p.id, p.title, o.resolution
                FROM products p
                JOIN orders_product op ON p.id = op.product_id
                JOIN orders o ON op.order_id = o.id
                WHERE o.user_id = %s AND o.is_paid = True
            """
            return await self.execute(query, (user_id,), fetchall=True)

    async def get_user_order(self, user_id, product_id, resolution):
        """Foydalanuvchi ma'lum filmni ma'lum resolutsionda sotib olganmi?"""
        query = """
            SELECT o.* FROM orders o
            JOIN orders_product op ON o.id = op.order_id
            WHERE o.user_id = %s AND op.product_id = %s AND o.resolution = %s AND o.is_paid = True
            LIMIT 1
        """
        return await self.execute(query, (user_id, product_id, resolution), fetchone=True)

    async def get_unpurchased_products(self, user_id, resolution):
        """Foydalanuvchi sotib olmagan filmlar (ma'lum resolution uchun)"""
        query = """
            SELECT p.* FROM products p
            WHERE p.is_active = 'active'
              AND (p.price_1080p > 0 OR p.price_4k > 0)
              AND p.id NOT IN (
                  SELECT op.product_id FROM orders_product op
                  JOIN orders o ON op.order_id = o.id
                  WHERE o.user_id = %s AND o.resolution = %s AND o.is_paid = True
              )
        """
        return await self.execute(query, (user_id, resolution), fetchall=True)


    async def get_user_unique_films(self, user_id):
        """Foydalanuvchi sotib olgan unikal filmlar (resolution'siz)"""
        query = """
                SELECT DISTINCT p.id, p.title
                FROM products p
                         JOIN orders_product op ON p.id = op.product_id
                         JOIN orders o ON op.order_id = o.id
                WHERE o.user_id = %s \
                  AND o.is_paid = True
                ORDER BY p.title \
                """
        return await self.execute(query, (user_id,), fetchall=True)


    async def get_user_purchased_resolutions(self, user_id, product_id):
        """Foydalanuvchi ma'lum filmni qaysi resolution'larda sotib olgan"""
        query = """
                SELECT DISTINCT o.resolution
                FROM orders o
                         JOIN orders_product op ON o.id = op.order_id
                WHERE o.user_id = %s \
                  AND op.product_id = %s \
                  AND o.is_paid = True \
                """
        result = await self.execute(query, (user_id, product_id), fetchall=True)
        return [r[0] for r in result] if result else []


    # ==================== ADMIN FUNCTIONS ====================

    async def get_admins(self):
        query = "SELECT * FROM admin_users"
        return await self.execute(query, fetchall=True)

    async def add_admin(self, username):
        query = "INSERT INTO admin_users(username) VALUES(%s)"
        await self.execute(query, (username,))

    async def get_admin_by_id(self, admin_id):
        query = "SELECT * FROM admin_users WHERE id=%s"
        return await self.execute(query, (admin_id,), fetchone=True)

    async def update_admin_info(self, admin_id, username):
        query = "UPDATE admin_users SET username=%s WHERE id=%s"
        await self.execute(query, (username, admin_id))

    async def delete_admin(self, admin_id):
        query = "DELETE FROM admin_users WHERE id=%s"
        await self.execute(query, (admin_id,))



    # ========================== VIDEO FUNCTIONS =======================================

    async def add_video(self, video_url, desc):
        query = "INSERT INTO videos(video_url, video_description) VALUES(%s, %s)"
        await self.execute(query, (video_url, desc))


    async def update_video_info(self, pk, video_url, desc):
        query = "UPDATE videos SET video_url=%s, video_description=%s WHERE id=%s"
        await self.execute(query, (video_url, desc, pk))


    async def delete_video(self, pk):
        query = "DELETE FROM videos WHERE id=%s"
        await self.execute(query, (pk,))


    async def get_videos(self):
        query = "SELECT * FROM videos"
        return await self.execute(query, fetchall=True)


    # ============================ BOT FUNCTIONS ========================================

    async def add_bot_start(self, tg_id, fullname, username):
        sql = """
              INSERT INTO bot_starts (tg_id, fullname, username, started_at)
            VALUES (%s, %s, %s, %s)
              """
        await self.execute(sql, (tg_id, fullname, username, datetime.now().date()))

    async def is_started(self, tg_id):
        sql = "SELECT 1 FROM bot_starts WHERE tg_id = %s"
        result = await self.execute(sql, (str(tg_id),), fetchone=True)
        return result is not None

    async def get_all_starts(self):
        sql = "SELECT tg_id, fullname, username, started_at FROM bot_starts ORDER BY started_at DESC"
        return await self.execute(sql, fetchall=True)


