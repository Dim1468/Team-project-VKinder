import psycopg2


def id_by_link(cur, account_link) -> int:
    cur.execute('''
        SELECT id 
        FROM user_account
        WHERE account_link = %s
    ''', (account_link,))
    user_id = cur.fetchone()[0]
    return user_id


def get_a_person(cur, gender=None, age=None, city=None) -> tuple:
    cur.execute('''
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
    ''', (gender, age, city, gender, age, city))
    print(cur.fetchone())
    return cur.fetchone()


def check_double(cur, account_link) -> bool:
    cur.execute(f'''
        SELECT count(1) > 0
        FROM user_account
        WHERE account_link = '{account_link}'
        ''')
    result = cur.fetchone()
    return result[0]


def put_a_person(cur, first_name, last_name, account_link, gender=None, age=None, city=None, photo_links=None):
    if check_double(cur, account_link) is not True:
        cur.execute('''
            INSERT INTO user_account (first_name, last_name, gender, age, city, account_link, photo_links)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (first_name, last_name, gender, age, city, account_link, photo_links))


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
