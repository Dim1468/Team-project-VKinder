import psycopg2

# класс для создания экземпляров пользователей ботом
class user_DB:
    # user_id - хранит уникальный идентефикатор странички вк пользователя бота
    # conn - connection для установки соединения с базой данных
    def __init__(self, conn, user_id):
        self.user_id = user_id
        self.conn = conn


class bot_user_DB(user_DB):
    # клаёт пользователя в бвзу данных
    def put_bot_user(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO bot_users
                    VALUES (%s)
                ''', (self.user_id, ))
            self.conn.commit()
        except psycopg2.errors.UniqueViolation:
            pass

    # при проведении поиска складывает информацию о нём в бд
    #    user_id - id пользователя бота
    #    criteria - информация об интересующем поле {1: 'Женщина', 2: 'Мужчина', 0: 'Пол не указан', 3: 'Пол не указан'}
    #    match_id - id пользователя вк, попавшемся при поиске
    #    status - информация, о том, прошёл ли поиск успешно
    #    flag - показывает, находится ли пользователь в ЧС (True - если находится)
    def put_search_data(self, criteria: int, match_id: int, status: str):
        try:
            flag = self.check_if_blocked(match_id)
            with self.conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO searches(starter_id, criteria, status)
                    VALUES (%s, %s, %s);
                    INSERT INTO search_users(match_id, search_id, flag)
                    VALUES (%s, lastval(), %s);
                ''', (self.user_id, criteria, status, match_id, flag))
            self.conn.commit()
        except psycopg2.errors.InFailedSqlTransaction as e:
            return e

    # используется методом put_search_data, проверяет, находится ли пользователь в чёрном списке
    #    match_id - id пользователя вк, попавшемся при поиске
    #    user_id - id пользователя бота
    def check_if_blocked(self, match_id) -> bool:
        with self.conn.cursor() as cur:
            cur.execute('''
                SELECT *
                FROM to_block
                WHERE blocked_account_id = %s AND user_account_id = %s
            ''', (match_id, self.user_id))
            if cur.fetchone():
                return True
            return False

    # показывает последнего вк пользователя, попавшегося в поиске конкретному пользователю бота
    #    user_id - id пользователя бота
    def get_last_shown_user(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    SELECT criteria, status, first_name, last_name, gender, age, city, account_link, photo_links
                    FROM vk_users 
                    JOIN search_users ON vk_users.user_id = search_users.match_id
                    JOIN searches ON search_users.search_id = searches.id
                    WHERE starter_id = %s;
                ''', (self.user_id, ))
                return cur.fetchone()
        except psycopg2.errors.InFailedSqlTransaction as e:
            return e

    # добавляет пользователя в список избранных
    #    user_id - id пользователя бота
    #    like_id - id пользователя вк
    def to_like(self, like_id):
        try:
            if self.user_id != like_id:
                with self.conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO to_like(user_account_id, liked_account_id) VALUES(%s, %s)
                    ''', (self.user_id, like_id))
                self.conn.commit()
            else:
                print('Так нельзя!')
        except psycopg2.errors.ForeignKeyViolation:
            print('Такого пользователя не существует')

    # добавляет пользователя в чёрный список
    #    user_id - id пользователя бота
    #    block_id - id пользователя вк
    def to_block(self, block_id):
        try:
            if self.user_id != block_id:
                with self.conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO to_block(user_account_id, blocked_account_id) VALUES(%s, %s)
                    ''', (self.user_id, block_id))
                self.conn.commit()
            else:
                print('Нельзя заблокировать самого себя')
        except psycopg2.errors.ForeignKeyViolation:
            print('Такого пользователя не существует')


# дочерний класс от user_DB, позволяет описать пользователя вк, появившегося при поиске
class vk_user_DB(user_DB):
    # помещает пользователя вк в бд
    #   gender - пол пользователя
    #   age - возраст
    #   city - город
    #   first_name - имя
    #   last_name - фамилия
    #   account_link - ссылка на страничку вк
    #   photo_links - словарь с фотографиями
    def put_a_vk_user(self, gender: str, age: int, city: str, first_name: str, last_name: str,
                      account_link: str, photo_links: dict):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO vk_users(user_id, first_name, last_name, gender, age, city, account_link, photo_links)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (self.user_id, first_name, last_name, gender, age,
                      city, account_link, photo_links))
            self.conn.commit()
        except psycopg2.errors.UniqueViolation:
            pass
