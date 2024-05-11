# Описание

Этот код представляет собой бота для социальной сети ВКонтакте. Он использует библиотеку `vk_api` для взаимодействия с API ВКонтакте. Бот может отправлять сообщения пользователям, а также принимать команды из личного сообщения.  Бот может отправлять сообщения, получать информацию о профиле пользователя, получать топ-3 фотографии пользователя а также выполнять поиск пользователей по заданным критериям.

# Логирование

Бот использует модуль `logging` для ведения журнала. Все ошибки и информационные сообщения записываются в файл `app.log`.

# Инициализация бота

Бот инициализируется с помощью токена сообщества и токена пользователя. Токен сообщества используется для отправки сообщений пользователям, токен пользователя используется для получения информации о пользователе.

# Список ответов

Бот имеет список ответов, которые он может отправлять пользователям. Этот список содержит приветственные сообщения.


# Функции

- `get_user_profile(user_id)`: Получает информацию о профиле пользователя по его ID.
- `get_top_photos(user_id)`: Получает топ-3 фотографии пользователя.
- `get_city_id(city_name)`: Получает ID города по его названию.
- `create_next_button()`: Создает клавиатуру с кнопкой "Далее".
- `create_gender_keyboard()`: Создает клавиатуру с кнопками "Мужчина" и "Женщина".
- `search_users(user_id, criteria, user_token)`: Выполняет поиск пользователей по заданным критериям.

# Основной цикл

Основной цикл `main_loop()` слушает события новых сообщений и выполняет соответствующие действия в зависимости от полученного текста сообщения. Бот реагирует на команды "Начать", указание пола, кнопку "Далее" и другие варианты.