import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Token import community_token, user_token

vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)

vk_user_token = vk_api.VkApi(token=user_token)

answer_list = ['Привет!', 'Приветствую!', 'Здравствуйте!']
hello_list = ['Привет', 'привет', 'Хай', 'хай',
              'Начать', 'Start', 'Начать поиск']

favorite_users = []


def write_msg(user_id, message, photos=None, photo_links=None, keyboard=None):
    parametrs = {'user_id': user_id,
                 'random_id': random.randrange(10 ** 7)}

    if message:
        parametrs['message'] = message

    if keyboard is not None:
        parametrs['keyboard'] = keyboard.get_keyboard()

    attachments = []
    if photos:
        attachments.extend(photos)
    if photo_links:
        attachments.extend(photo_links)

    if attachments:
        parametrs['attachment'] = ','.join(attachments)

    vk.method('messages.send', parametrs)


def get_user_profile(user_id):
    user_info = vk.method('users.get', {'user_ids': user_id, 'fields': 'sex,bdate,city'})
    return user_info[0]


def get_top_photos(user_id):
    photos = vk_user_token.method('photos.getAll', {'owner_id': user_id, 'extended': 1})
    sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
    top_photos = sorted_photos[:3]
    photo_links = [photo['sizes'][-1]['url'] for photo in top_photos]
    return photo_links


user_offsets = {}


def search_users(user_id, criteria, user_token, offset=0):
    user_profile = get_user_profile(user_id)
    user_city = user_profile.get('city', {}).get('title', '')
    user_age = 2024 - int(user_profile['bdate'].split('.')[-1])

    criteria_str = ', '.join(criteria)

    if 'мужской' in criteria_str.lower():
        user_sex = 2
    elif 'женский' in criteria_str.lower():
        user_sex = 1
    else:
        user_sex = user_profile['sex']

    search_query = f'sex={user_sex}&city={user_city}'

    users = vk_api.VkApi(token=user_token).method('users.search',
                                                  {'count': 3, 'fields': 'photo_200', 'q': '', 'sort': 0, 'online': 0,
                                                   'has_photo': 1, 'status': 6, 'access_token': user_token,
                                                   'v': '5.131', 'is_closed': False, 'can_access_closed': True,
                                                   'hometown': user_city, 'sex': user_sex, 'age_from': user_age - 2,
                                                   'age_to': user_age + 2, 'city': user_city, 'offset': offset})

    if users['items']:
        random_user = random.choice(users['items'])
        user_info = f"{random_user['first_name']} {random_user['last_name']}\nhttps://vk.com/id{random_user['id']}"
        user_profile_link = f"https://vk.com/id{random_user['id']}"
        write_msg(user_id, f"{user_info}\n")

        photo_links = get_top_photos(random_user['id'])
        for link in photo_links:
            write_msg(user_id, 'Фотография:', photo_links=[link])

        next_button = VkKeyboard(one_time=False, inline=True)
        next_button.add_button('Далее', color=VkKeyboardColor.PRIMARY)
        write_msg(user_id, "Хотите еще вариантов?", keyboard=next_button)

    else:
        write_msg(user_id, 'Не удалось найти подходящих пользователей.')

    user_offsets[user_id] = 0


def search_next_user(user_id, criteria, user_token):
    offset = user_offsets.get(user_id, 0)
    offset += 3
    user_offsets[user_id] = offset
    search_users(user_id, criteria, user_token, offset)



criteria = None

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            filter_list = event.text.split(', ')
            chat_button = VkKeyboard(inline=True)
            if request == 'Начать' or request in hello_list:
                write_msg(event.user_id, f'{random.choice(answer_list)}')
                write_msg(event.user_id,
                          f'Подскажи, кого мы ищем?\nУкажи через запятую пол, возраст и город.\nПример: Мужской, 26, Москва')
            elif ',' in request:
                criteria = request.split(', ')
                search_users(event.user_id, criteria, user_token)
            elif request == 'Далее':
                search_next_user(event.user_id, criteria, user_token)
