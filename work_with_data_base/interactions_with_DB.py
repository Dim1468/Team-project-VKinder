import psycopg2


class User:
    def __init__(self, cur, gender=None, age=None, city=None, first_name=None, last_name=None,
                 account_link=None, photo_links=None):
        self.cur = cur
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.age = age
        self.city = city
        self.account_link = account_link
        self.photo_links = photo_links

    def get_a_person(self) -> tuple:
        self.cur.execute('''
            SELECT *
            FROM user_account
            WHERE
                gender iLIKE %s
                OR age = %s
                OR city iLIKE %s
            ORDER BY
                gender iLIKE %s DESC, gender,
                age = %s DESC, age,
                city iLIKE %s DESC, city;   
        ''', (self.gender, self.age, self.city, self.gender, self.age, self.city))
        return self.cur.fetchone()

    def check_double(self) -> bool:
        self.cur.execute(f'''
            SELECT count(1) > 0
            FROM user_account
            WHERE account_link = '{self.account_link}'
            ''')
        result = self.cur.fetchone()
        return result[0]

    def put_a_person(self):
        if self.check_double() is not True:
            self.cur.execute('''
                INSERT INTO user_account (first_name, last_name, gender, age, city, account_link, photo_links)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (self.first_name, self.last_name, self.gender, self.age,
                  self.city, self.account_link, self.photo_links))


def id_by_link(cur, account_link) -> int:
    cur.execute('''
        SELECT id 
        FROM user_account
        WHERE account_link = %s
    ''', (account_link,))
    user_id = cur.fetchone()[0]
    print(user_id)
    return user_id


def to_like(conn, user_id, like_id):
    try:
        if user_id != like_id:
            with conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO to_like(user_account_id, liked_account_id) VALUES(%s, %s)
                    ''', (user_id, like_id))
        else:
            print('Так нельзя!')
    except psycopg2.errors.ForeignKeyViolation:
        print('Такого пользователя не существует')


def to_block(conn, user_id, block_id):
    try:
        if user_id != block_id:
            with conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO to_block(user_account_id, blocked_account_id) VALUES(%s, %s)
                    ''', (user_id, block_id))
        else:
            print('Нельзя заблокировать самого себя')
    except psycopg2.errors.ForeignKeyViolation:
        print('Такого пользователя не существует')
