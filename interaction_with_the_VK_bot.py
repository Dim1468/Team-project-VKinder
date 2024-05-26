import json
import logging
import random
import psycopg2
import vk_api
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Token import community_token, user_token
from work_with_data_base.interactions_with_DB import user_DB, bot_user_DB, vk_user_DB
from work_with_data_base.user_data.DB_login_info import database, user, password

conn = psycopg2.connect(database=database, user=user, password=password)
cur = conn.cursor()

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

buttons_config = {
    "next": {"title": "Далее", "color": VkKeyboardColor.PRIMARY},
    "like": {"title": "Like", "color": VkKeyboardColor.POSITIVE},
    "block": {"title": "ЧС", "color": VkKeyboardColor.NEGATIVE},
    "male": {"title": "Мужчина", "color": VkKeyboardColor.PRIMARY},
    "female": {"title": "Женщина", "color": VkKeyboardColor.PRIMARY}
}

def create_button(button_config):
    button = VkKeyboard(one_time=False, inline=True)
    button.add_button(button_config['title'], color=button_config['color'])
    return button

def create_keyboard(buttons):
    keyboard = VkKeyboard(one_time=False, inline=True)
    for button_config in buttons:
        keyboard.add_button(button_config['title'], color=button_config['color'])
    return keyboard

def write_msg(user_id, message, photos=None, photo_links=None, keyboard=None):
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
    try:
        user_info = vk.method('users.get', {'user_ids': user_id, 'fields': 'sex,bdate,city,first_name,last_name'})
        return user_info[0]
    except Exception as e:
        logging.error(f"Error getting user profile: {e}")
        raise

PHOTOS_NOT_FOUND_CODE = 30

def get_top_photos(user_id, photos_count=3):
    try:
        photos = vk_user_token.method('photos.getAll', {'owner_id': user_id, 'extended': 1})
        sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
        top_photos = sorted_photos[:photos_count if len(sorted_photos) >= photos_count else len(sorted_photos)]
        photo_links = [photo['sizes'][-1]['url'] for photo in top_photos]
        return photo_links
    except vk_api.exceptions.ApiError as e:
        if e.code == PHOTOS_NOT_FOUND_CODE:
            return []
        else:
            logging.error(f"Error getting top photos: {e}")
            raise

def get_user_age(birthdate_str):
    if birthdate_str:
        try:
            birthdate = datetime.strptime(birthdate_str, '%d.%m.%Y')
        except ValueError:
            today = datetime.now()
            birthdate = datetime(today.year, int(birthdate_str.split('.')[1]), int(birthdate_str.split('.')[0]))
        current_date = datetime.now()
        age = current_date.year - birthdate.year - (
                    (current_date.month, current_date.day) < (birthdate.month, birthdate.day))
        return age
    else:
        return -1

def get_city_id(city_name):
    city = vk_user_token.method('database.getCities', {'q': city_name})
    return city['items'][0]['id'] if city['count'] > 0 else None

def search_users(user_id, criteria, user_db):
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

    if not users['items']:
        write_msg(user_id, 'Не удалось найти подходящих пользователей.')
        return

    available_users = [user for user in users['items'] if not user_db.check_if_blocked(user['id'])]
    if not available_users:
        write_msg(user_id, 'Не удалось найти подходящих пользователей.')
        return

    random_user = random.choice(available_users)
    show_user_info(user_id, random_user)
    user_db.put_search_data(criteria, random_user['id'], 'success')  # Помечаем пользователя как показанного
    show_interaction_buttons(user_id)

def show_user_info(user_id, user_data):
    user_info = f"{user_data['first_name']} {user_data['last_name']}\nhttps://vk.com/id{user_data['id']}"
    write_msg(user_id, user_info)
    photo_links = get_top_photos(user_data['id'])
    for link in photo_links:
        write_msg(user_id, 'Фотография:', photo_links=[link])

def show_interaction_buttons(user_id):
    keyboard = create_keyboard([buttons_config['next'], buttons_config['like'], buttons_config['block']])
    write_msg(user_id, "Выберите действие:", keyboard=keyboard.get_keyboard())

def handle_like_button_click(user_id, user_db):
    try:
        last_shown_user = user_db.get_last_shown_user()
        if not last_shown_user:
            write_msg(user_id, "Ошибка: не удалось получить данные последнего показанного пользователя.")
            return

        user_db.to_like(last_shown_user[0])

        write_msg(user_id, "!")
        search_users(user_id, last_shown_user[0], user_db)
    except Exception as e:
        logging.error(f"Error handling like button click: {e}")
        raise

def handle_block_button_click(user_id, user_db):
    try:
        last_shown_user = user_db.get_last_shown_user()
        if not last_shown_user:
            write_msg(user_id, "Ошибка: не удалось получить данные последнего показанного пользователя.")
            return

        user_db.to_block(last_shown_user[0])
        write_msg(user_id, 'Вы добавили вариант в черный список.')

        search_users(user_id, last_shown_user[0], user_db)
    except Exception as e:
        logging.error(f"Error handling block button click: {e}")
        raise


GENDER_FEMALE = 1
GENDER_MALE = 2
GENDER_UNKNOWN = 0
def main_loop():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text
            user_id = event.user_id

            user_db = bot_user_DB(conn, user_id)

            if request == 'Начать' or request in hello_list:
                # Получаем информацию о профиле пользователя

                bot_user_id = user_db.put_bot_user()

                write_msg(user_id, f'{random.choice(answer_list)}')
                write_msg(user_id, f'Подскажи, кого мы ищем?\nУкажи пол:',
                          keyboard=create_keyboard([buttons_config['male'], buttons_config['female']]).get_keyboard())



            elif request.lower() == 'мужчина' or request.lower() == 'женщина':
                criteria = GENDER_MALE if request.lower() == 'мужчина' else GENDER_FEMALE


                user_profile = get_user_profile(user_id)
                birthdate_str = user_profile.get('bdate', None)
                age = get_user_age(birthdate_str)
                city = user_profile['city']['title'] if 'city' in user_profile else None


                search_data = {
                    'starter_id': bot_user_id,
                    'criteria': criteria,
                    'status': 'active'
                }
                search_id = user_db.put_search_data(search_data)


                search_users(user_id, criteria, user_db)

            elif request == 'Далее':
                if criteria:
                    search_users(user_id, criteria, user_db)
                else:
                    write_msg(user_id, 'Сначала укажите пол.')

            elif request == 'Like' or request == 'ЧС':
                shown_users = user_db.get_shown_users()


                if not shown_users:
                    write_msg(user_id, 'Пользователи не найдены.')
                    continue

                if request == 'Like':
                    handle_like_button_click(user_id, user_db)
                elif request == 'ЧС':
                    handle_block_button_click(user_id, user_db)



try:
    main_loop()
except Exception as e:
    logging.error(f"Error in main loop: {e}")
    raise


