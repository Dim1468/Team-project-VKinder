def renovate_tables(cur):
    delete_tables(cur)
    create_tables(cur)


def delete_tables(cur):
    cur.execute('''
            DROP TABLE user_photo;
            DROP TABLE to_like;
            DROP TABLE to_block;
            DROP TABLE user_account;
        ''')


def create_tables(cur):
    cur.execute('''
            CREATE TABLE IF NOT EXISTS user_account(
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(15) NOT NULL,
                last_name VARCHAR(25) NOT NULL,
                gender VARCHAR(7),
                age INTEGER,
                city VARCHAR(20),
                account_link TEXT NOT NULL,
                photo_links JSONB
            );
            
            CREATE TABLE IF NOT EXISTS to_like(
                id SERIAL PRIMARY KEY,
                user_account_id INTEGER REFERENCES user_account(id),
                liked_account_id INTEGER REFERENCES user_account(id)
            );
    
            CREATE TABLE IF NOT EXISTS to_block(
                id SERIAL PRIMARY KEY,
                user_account_id INTEGER REFERENCES user_account(id),
                blocked_account_id INTEGER REFERENCES user_account(id)
            );
        ''')
