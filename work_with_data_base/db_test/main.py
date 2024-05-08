import psycopg2
from psycopg2.extras import Json
from work_with_data_base.interactions_with_DB import (get_a_person, put_a_person, to_like, to_block)
from work_with_data_base.creation_of_DB import renovate_tables
from work_with_data_base.user_data.DB_login_info import database, user, password


if __name__ == '__main__':
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            # Очищаю данные таблицы
            renovate_tables(cur)
            # Заполняю таблицу пользователей
            put_a_person(cur, 'Maria', 'Reinolds', 'jbjkcmck', 'female', city='Stokholm',
                         photo_links=Json({1: 'https://i.yapx.cc/OMDU5.jpg',
                                           2: 'https://i.pinimg.com/736x/7c/24/cc/7c24ccdd8698cce9aa18b13ec6b59082.jpg',
                                           3: 'https://www.youtube.com/watch?v=1HVWTrbgmxw'}))
            put_a_person(cur, 'Leo', 'Peterson', 'sxjdvbkbc', 'male', '18', city='Stokholm')
            put_a_person(cur, 'Xio', 'Mala-Suerte', age='13', account_link='israpsidian', city='Valle del sol')
            put_a_person(cur, 'Maria', 'Reis', 'kdkljcnk', 'female', city='Stokholm')
            put_a_person(cur, 'Maria', 'Reinolds', 'jbjkcmck', 'female', city='Stokholm')
            # Достаю пользователей по совпадениям
            get_a_person(cur, city='Stokholm')
            get_a_person(cur, gender='male', age='18', city='Stokholm')
            get_a_person(cur, age='13', city='valle del sol')
    # тестирую функцию to_like
    to_like(conn, 1, 3)
    to_like(conn, 7, 3)
    to_like(conn, 3, 3)
    # тестирую функцию to_block
    to_block(conn, 2, 1)
    to_block(conn, 3, 3)
    to_block(conn, 15, 1)
