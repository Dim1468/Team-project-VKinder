import psycopg2
from psycopg2.extras import Json
from work_with_data_base.interactions_with_DB import (User, Actions)
from work_with_data_base.creation_of_DB import renovate_tables
from work_with_data_base.user_data.DB_login_info import database, user, password

if __name__ == '__main__':
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:

            # Создаю пользователей
            put_user1 = User(cur, 'female', None, 'Stokholm', 'Maria',
                             'Reinolds', 'jbjkcmck',
                             photo_links=Json({
                                 1: 'https://i.yapx.cc/OMDU5.jpg',
                                 2: 'https://i.pinimg.com/736x/7c/24/cc/7c24ccdd8698cce9aa18b13ec6b59082.jpg',
                                 3: 'https://www.youtube.com/watch?v=1HVWTrbgmxw'
                             }))
            put_user2 = User(cur, 'male', '18', 'Stokholm', 'Leo', 'Peterson', 'sxjdvbkbc')
            put_user3 = User(cur, None, '13', 'Valle del sol', 'Xio', 'Mala-Suerte', 'israpsidian')

            get_user1 = User(cur, city='Stokholm')
            get_user2 = User(cur, gender='male', age='18', city='Stokholm')
            get_user3 = User(cur, age='13', city='valle del sol')

            like1 = Actions(conn, 1, like_id=3)
            like2 = Actions(conn, 7, like_id=3)
            like3 = Actions(conn, 3, like_id=3)
            block1 = Actions(conn, 2, block_id=1)
            block2 = Actions(conn, 3, block_id=3)
            block3 = Actions(conn, 15, block_id=1)

            # Очищаю данные таблицы
            renovate_tables(cur)

            # Заполняю таблицу пользователей
            put_user1.put_a_person()
            put_user2.put_a_person()
            put_user3.put_a_person()

            # Достаю пользователей по совпадениям
            get_user1.get_a_person()
            get_user2.get_a_person()
            get_user3.get_a_person()

    # тестирую функцию to_like
    like1.to_like()
    like2.to_like()
    like3.to_like()

    # тестирую функцию to_block
    block1.to_block()
    block2.to_block()
    block3.to_block()
