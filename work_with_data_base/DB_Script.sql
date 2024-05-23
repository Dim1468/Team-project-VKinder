-- таблица пользователей вк, поподающихся при поиске
--	user_id - уникальный идентификатор странички пользователя вк
--	first_name, last_name, gender, age, city - личная информация пользователя
--	account_link - ссылка на акаунт пользователя вк
--	photo_links - словарик с фотографиями пользователя
CREATE TABLE IF NOT EXISTS vk_users(
    user_id BIGINT UNIQUE NOT NULL,
    first_name VARCHAR(15) NOT NULL,
    last_name VARCHAR(25),
    gender VARCHAR(7),
    age INTEGER,
    city VARCHAR(20),
    account_link TEXT NOT NULL,
    photo_links JSONB
);

-- таблица пользователей бота
--	user_id - уникальный идентификатор странички пользователя ботом
CREATE TABLE IF NOT EXISTS bot_users(
	user_id BIGINT UNIQUE 
);

-- таблица(история) запросов пользователей
--	starter_id отражает пользователя, зделавшего запрос
--	в criteria находится информация о запросе пользователя(gender_mapping)
-- status - состояние запроса(прошел ли успешно, или возникли проблемы)
CREATE TABLE IF NOT EXISTS searches(
	id SERIAL PRIMARY KEY,
	starter_id BIGINT REFERENCES bot_users(user_id),
	criteria INTEGER,
	status VARCHAR(42)
);

-- результаты запросов пользователей
--	match_id отражает профиль найденного пользователя
-- 	search_id - это порядковый номер запрса
--	flag - показывает, попадался ли данный пользователь в поиске раньше
CREATE TABLE IF NOT EXISTS search_users(
	match_id BIGINT REFERENCES vk_users(user_id),
	search_id BIGINT REFERENCES searches(id),
	flag BOOLEAN
);

-- таблица понравившихся пользователей
--	id - уникальный идентификатор пары
--	user_account_id - пользователь, сделавший запрос
--	liked_account_id - понравившийся пользователь
CREATE TABLE IF NOT EXISTS to_like(
    id SERIAL PRIMARY KEY,
    user_account_id BIGINT REFERENCES bot_users(user_id),
    liked_account_id BIGINT REFERENCES vk_users(user_id)
);

-- таблица непонравившихся пользователей
--	id - уникальный идентификатор пары
--	user_account_id - пользователь, сделавший запрос
--	blocked_account_id - непонравившийся пользователь
CREATE TABLE IF NOT EXISTS to_block(
    id SERIAL PRIMARY KEY,
    user_account_id BIGINT REFERENCES bot_users(user_id),
    blocked_account_id BIGINT REFERENCES vk_users(user_id)
);
