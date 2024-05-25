import psycopg2
import unittest
from psycopg2.extras import Json
from work_with_data_base.interactions_with_DB import (bot_user_DB, vk_user_DB)
from work_with_data_base.user_data.DB_login_info import database, user, password

with psycopg2.connect(database=database, user=user, password=password) as conn:
    vk_user = vk_user_DB(conn, 3456789)
    vk_user.put_a_vk_user('None', 40, 'None', 'Jakie', 'None', 'dfghjvbnm', None)
    vk_user2 = vk_user_DB(conn, 98765)
    vk_user2.put_a_vk_user('female', 30, 'dunno',
                           'Ash', 'Pacific', 'mfoobofmb',
                           photo_links=Json(
                               {1: 'https://really', 2: 'https://better', 3: 'https://dont||'}))
    bot_user = bot_user_DB(conn, 123456)
    bot_user.put_bot_user()
    bot_user.put_search_data(1, vk_user.user_id, 'alles gut')
    bot_user.put_search_data(1, vk_user2.user_id, 'gut')


class TestDB(unittest.TestCase):

    def test_put_bot_user(self):
        with psycopg2.connect(database=database, user=user, password=password) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * 
                    FROM bot_users
                    WHERE user_id = 123456
                ''')
                self.assertIn(123456, cur.fetchone())

    def test_put_a_vk_user(self):
        with psycopg2.connect(database=database, user=user, password=password) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT *
                    FROM vk_users
                    WHERE user_id = %s
                ''', (vk_user.user_id, ))
                self.assertEqual((3456789, 'Jakie', 'None', 'None', 40, 'None', 'dfghjvbnm', None), cur.fetchone())

                cur.execute('''
                                    SELECT user_id, first_name, last_name, gender, age, city
                                    FROM vk_users
                                    WHERE user_id = %s
                                ''', (vk_user2.user_id,))
                self.assertEqual((98765, 'Ash', 'Pacific', 'female', 30, 'dunno'), cur.fetchone())

    def test_put_search_data(self):
        with psycopg2.connect(database=database, user=user, password=password) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT *
                    FROM searches s
                    JOIN search_users sa on s.id = sa.search_id
                    WHERE starter_id = 123456
                ''')
                actual = cur.fetchall()
                for expected in [(1, bot_user.user_id, 1, 'alles gut', vk_user.user_id, 1, False),
                                 (2, bot_user.user_id, 1, 'gut', vk_user2.user_id, 2, False)
                                 ]:
                    self.assertIn(expected, actual)

    def test_get_last_shown_user(self):
        self.assertEqual((1, 'gut', 'Ash', 'Pacific', 'female', 30, 'dunno', 'mfoobofmb',
                          {'1': 'https://really', '2': 'https://better', '3': 'https://dont||'}),
                         bot_user.get_last_shown_user())

    def test_to_block(self):
        with psycopg2.connect(database=database, user=user, password=password) as conn:
            with conn.cursor() as cur:
                self.assertEqual(False, bot_user.check_if_blocked(98765))

                bot_user.to_block(98765)
                bot_user.put_search_data(1, vk_user2.user_id, 'Blocked')
                self.assertEqual(True, bot_user.check_if_blocked(98765))

                cur.execute('''
                                SELECT blocked_account_id
                                FROM to_block
                                WHERE user_account_id = %s;
                            ''', (bot_user.user_id,))
                self.assertIn((98765,), cur.fetchall())

    def test_to_like(self):
        with psycopg2.connect(database=database, user=user, password=password) as conn:
            with conn.cursor() as cur:
                bot_user.to_like(like_id=3456789)
                cur.execute('''
                                SELECT liked_account_id
                                FROM to_like
                                WHERE user_account_id = %s;
                            ''', (bot_user.user_id,))
                self.assertIn((3456789,), cur.fetchall())


if __name__ == '__main__':
    unittest.main()
