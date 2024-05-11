import logging
import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Token import community_token, user_token

# Логирование
logging.basicConfig(filename='app.log', level=logging.INFO)

try:
    vk = vk_api.VkApi(token=community_token)
    longpoll = VkLongPoll(vk)
    vk_user_token = vk_api.VkApi(token=user_token)
except Exception as e:
    logging.error(f"Error initializing VK API: {e}")
    raise

answer_list = ['Привет!', 'Приветствую!', 'Здравствуйте!']
hello_list = ['Привет', 'привет', 'Хай', 'хай', 'Начать', 'Start', 'Начать поиск']
favorite_users = []
shown_users = []


def write_msg(user_id, message, photos=None, photo_links=None, keyboard=None):
    """
    Отправляет сообщение пользователю с опциональными вложениями (фотографиями),
    ссылками на фотографии и пользовательской клавиатурой.

    Args: user_id (int): ID пользователя, которому отправляется сообщение.
          message (str): Текст сообщения.
          photos (list, optional): Список вложенных фотографий.
          photo_links (list, optional): Список ссылок на фотографии.
          keyboard (VkKeyboard, optional): Пользовательская клавиатура.
    """
    try:
        params = {'user_id': user_id, 'random_id': random.randrange(10 ** 7)}
        if message:
            params['message'] = message
        if keyboard is not None:
            params['keyboard'] = keyboard
        attachments = []
        if photos:
            attachments.extend(photos)
        if photo_links:
            attachments.extend(photo_links)
        if attachments:
            params['attachment'] = ','.join(attachments)
        vk.method('messages.send', params)
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        raise


def get_user_profile(user_id):
    """
    Получает информацию о профиле пользователя по его ID.
    Args: user_id (int): ID пользователя.
    Returns:
        dict: Информация о профиле пользователя.
    """
    try:
        user_info = vk.method('users.get', {'user_ids': user_id, 'fields': 'sex,bdate,city'})
        return user_info[0]
    except Exception as e:
        logging.error(f"Error getting user profile: {e}")
        raise


def get_top_photos(user_id):
    """
    Получает фотографии вариантов.
    Args: user_id (int): ID пользователя.
    Returns:
        list: Список ссылок на топ-3 фотографии.
    """
    try:
        photos = vk_user_token.method('photos.getAll', {'owner_id': user_id, 'extended': 1})
        sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
        top_photos = sorted_photos[:3]
        photo_links = [photo['sizes'][-1]['url'] for photo in top_photos]
        return photo_links
    except vk_api.exceptions.ApiError as e:
        if e.code == 30:
            return []
        else:
            logging.error(f"Error getting top photos: {e}")
            raise


def get_city_id(city_name):
    """
    Получает ID города по его названию.
    Args: city_name (str): Название города.
    Returns:
        int: ID города.
    """
    try:
        city = vk_user_token.method('database.getCities', {'q': city_name})
        return city['items'][0]['id'] if city['count'] > 0 else None
    except KeyError as e:
        logging.error(f"KeyError in get_city_id: {e}")
        return None
    except Exception as e:
        logging.error(f"Error in get_city_id: {e}")
        return None


def create_next_button():
    """
    Создает клавиатуру с кнопкой "Далее".
    Returns:
        VkKeyboard: Объект клавиатуры с кнопкой "Далее".
    """
    try:
        next_button = VkKeyboard(one_time=False, inline=True)
        next_button.add_button('Далее', color=VkKeyboardColor.PRIMARY)
        return next_button
    except Exception as e:
        logging.error(f"Error in create_next_button: {e}")
        return None


def create_gender_keyboard():
    """
    Создает клавиатуру с кнопками "Мужчина" и "Женщина".
    Returns:
        VkKeyboard: Объект клавиатуры с кнопками "Мужчина" и "Женщина".
    """
    try:
        gender_keyboard = VkKeyboard(one_time=False, inline=True)
        gender_keyboard.add_button('Мужчина', color=VkKeyboardColor.PRIMARY)
        gender_keyboard.add_button('Женщина', color=VkKeyboardColor.PRIMARY)
        return gender_keyboard
    except Exception as e:
        logging.error(f"Error in create_gender_keyboard: {e}")
        return None


def search_users(user_id, criteria, user_token):
    """
    Выполняет поиск пользователей по заданным критериям.
    Args: user_id (int): ID пользователя, выполняющего поиск.
          criteria (int): Критерий поиска (пол).
          user_token (str): Токен пользователя для доступа к API VK.
    """
    try:
        user_profile = get_user_profile(user_id)
        user_city_name = user_profile.get('city', {}).get('title', '')
        user_city_id = get_city_id(user_city_name)

        if user_city_id is None:
            write_msg(user_id, 'Не удалось определить ваш город.')
            return

        user_age = 2024 - int(user_profile['bdate'].split('.')[-1])

        users = vk_api.VkApi(token=user_token).method('users.search',
                                                       {'count': 10, 'fields': 'photo_200', 'sex': criteria,
                                                        'city': user_city_id, 'age_from': user_age - 2,
                                                        'age_to': user_age + 2})
        if users['items']:
            available_users = [user for user in users['items'] if user['id'] not in shown_users]
            if available_users:
                random_user = random.choice(available_users)
                user_info = f"{random_user['first_name']} {random_user['last_name']}\nhttps://vk.com/id{random_user['id']}"
                user_profile_link = f"https://vk.com/id{random_user['id']}"
                write_msg(user_id, f"{user_info}\n")

                photo_links = get_top_photos(random_user['id'])
                for link in photo_links:
                    write_msg(user_id, 'Фотография:', photo_links=[link])

                shown_users.append(random_user['id'])

                next_button = create_next_button()
                write_msg(user_id, "Хотите еще вариантов?", keyboard=next_button.get_keyboard())

            else:
                write_msg(user_id, 'Не удалось найти подходящих пользователей.')

        else:
            write_msg(user_id, 'Не удалось найти подходящих пользователей.')

    except Exception as e:
        logging.error(f"Error in search_users: {e}")

try:
    criteria = None
    
except Exception as e:
    logging.error(f"Error in other functions: {e}")
    

# Основной цикл
def main_loop():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                if request == 'Начать' or request in hello_list:
                    write_msg(event.user_id, f'{random.choice(answer_list)}')
                    write_msg(event.user_id,
                              f'Подскажи, кого мы ищем?\nУкажи пол:',
                              keyboard=create_gender_keyboard().get_keyboard())
                elif request.lower() == 'мужчина' or request.lower() == 'женщина':
                    criteria = 2 if request.lower() == 'мужчина' else 1
                    search_users(event.user_id, criteria, user_token)
                elif request == 'Далее':
                    if criteria:
                        search_users(event.user_id, criteria, user_token)
                    else:
                        write_msg(event.user_id, 'Сначала укажите пол.')

try:
    main_loop()
except Exception as e:
    logging.error(f"Error in main loop: {e}")
    raise
