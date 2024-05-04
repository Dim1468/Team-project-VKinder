import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from Token import community_token, user_token
#БД#
#ВК#

vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)

answer_list = ['Привет!', 'Приветствую!', 'Здравствуйте!']
hello_list = ['Привет', 'привет', 'Хай', 'хай', 
              'Начать', 'Start', 'Начать поиск']

def write_msg(user_id, message, keyboard=None, attachment=None):
    parametrs = {'user_id': user_id,
                 'message': message,
                 'random_id': random.randrange(10 ** 7),
                 'attachment': attachment
                 }

    if keyboard is not None:
        parametrs['keyboard'] = keyboard.get_keyboard()

    vk.method('messages.send', parametrs)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            filter_list = event.text.split(', ')
            chat_button = VkKeyboard(inline=True)
            if request == 'Начать' or request in answer_list:
                write_msg(
                    event.user_id, f'{random.choice(answer_list)}')  # выводим приветствие рандомным образом
                write_msg(
                    event.user_id, f'Подскажи, кого мы ищем?\nУкажи через запятую пол, возраст и город.\nПример: Мужской, 26, Москва')