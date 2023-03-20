from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import datetime
from datetime import date
from pprint import pprint
from d2 import vk_client
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import bd
from bd import create_tables, User, Person, session, Seen_persones


def get_token(file_name):
    """Получение токена из файла"""
    with open(file_name, "r") as file:
        return file.readline()



def scan_msg(words: tuple) -> tuple:
    """Обрабатывает сообщения в чате"""
    for event in longpoll.listen():
        try:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                user_id = event.user_id
                if request in words:
                    return user_id, request
                else:
                    write_msg(user_id, "Не поняла вашего ответа...")
        except:
            pass


def write_msg(user_id, message, photos=None, keyboard=None):
    '''Функция для отправки сообщений'''
    params = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
    if photos:
        params['attachment'] = ','.join(photos)
        attachment = photos
        print(attachment)
    if keyboard:
        params['keyboard'] = keyboard
    return vk1.method('messages.send', params)



def ask_missed_info(user_id, user_info):
    """Проверяет недостающую информацию, спрашивает, если необходимо, и добавляет в словарь"""
    filled_info = {}
    vals = {'bdate': 'Возраст', 'city': 'город'}
    for key, value in vals.items():
        try:
            if not key in user_info:
                write_msg(user_id, f"Введите недостающие данные {vals[key]}: ")
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text.lower()
                            if key == 'bdate':
                                filled_info['user_age'] = int(request)
                                break
                            elif key == 'city':
                                filled_info['city'] = vk_client.get_city_id(request)
                                break
        except:
            pass
    return filled_info


def calculate_age(born):
    """Высчитывает возраст на сегодняшний день по дате рождения"""
    born = [int(i) for i in born.split('.')]
    today = date.today()
    return today.year - born[2] - ((today.month, today.day) < (born[1], born[0]))


def show_all_users(user_id, persons):
    for person in persons:
        photos = vk_client.get_user_photos(person['user_id'])
        if photos:
            expected_words = ('в избранное', 'дальше', 'выход')
            keyboard1 = VkKeyboard(one_time=True)
            keyboard1.add_button("В избранное", color=VkKeyboardColor.PRIMARY)
            keyboard1.add_button("Дальше", color=VkKeyboardColor.PRIMARY)
            keyboard1.add_line()
            keyboard1.add_button("Выход", color=VkKeyboardColor.SECONDARY)
            keyboard1 = keyboard1.get_keyboard()
            write_msg(user_id, *show_person(person, photos), keyboard=keyboard1)

            add_person_to_bd(person)

            # добавляем пару в просмотренные
            add_user_to_seen(person['user_id'], user_id)
            answer = scan_msg(expected_words)[1]
            if answer == 'дальше':
                continue
            elif answer == 'в избранное':
                session.query(Seen_persones).filter(Seen_persones.seen_person_id == person['user_id']).update({"liked": True})
                session.commit()

                continue
            elif answer == 'выход':
                write_msg(user_id, "Пока((")
                return
        # except:
        #     pass

    write_msg(user_id, "Кондидаты закончились")
    return True


def show_person(person, photos):
    person_age = datetime.now().year - int(person['bdate'][-4:])
    age = f", {person_age} {('год', ('лет', 'года')[0 < person_age % 10 < 5])[person_age % 10 != 1]}"
    return f"{person['first_name']} {age}\nhttps://vk.com/id{person['user_id']}", photos

def add_user_to_bd(user_info, user_id):
    # try:
        user_bd = User(user_id=user_id, first_name=user_info['first_name'], bdate=user_info.get('bdate', 0),
                       sex=user_info['sex'],
                       city=user_info['city'], age=user_info['age'])
        session.add(user_bd)
        session.commit()
    # except:
    #     pass

def add_user_to_seen(person_id, user_id):
    # try:
        person = Seen_persones(seen_person_id = person_id, user_id_user = user_id, liked = False)
        session.add(person)
        session.commit()
    # except:
    #     pass


def get_user_info_from_bd(user_id):
    info = {}
    try:
        info['user_id'] = session.query(User.user_id).filter(User.user_id == user_id).all()[0][0]
        info['first_name'] = session.query(User.first_name).filter(User.user_id == user_id).all()[0][0]
        info['bdate'] = session.query(User.bdate).filter(User.user_id == user_id).all()[0][0]
        info['sex'] = session.query(User.sex).filter(User.user_id == user_id).all()[0][0]
        info['city'] = session.query(User.city).filter(User.user_id == user_id).all()[0][0]
        info['age'] = session.query(User.age).filter(User.user_id == user_id).all()[0][0]
    except:
        pass
    return info

def add_person_to_bd(person):
    # try:
        person_bd = Person(person_id=person['user_id'], name = person['first_name'], bdate = person['bdate'], sex = person['sex'], city = person['city'])
        session.add(person_bd)
        session.commit()
    # except:
    #     pass


token_group = get_token('token_g.txt')
vk1 = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk1)


def main():
    create_tables(bd.engine)
    user_id, request = scan_msg(('привет', 'хай', 'ку'))

    if request:
        answers = ('да', 'конечно', 'несомненно', 'начать поиск')
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Начать поиск", color=VkKeyboardColor.POSITIVE)
        keyboard = keyboard.get_keyboard()
        write_msg(user_id, f"Привет, {vk_client.get_user_info(user_id)['first_name']}!\nПодобрать пару?",
                  keyboard=keyboard)
        answer = scan_msg(answers)[1]
        if answer:
            bd_user_info = session.query(User).filter(User.user_id == user_id).all()
            if bool(bd_user_info):
                user_info = get_user_info_from_bd(user_id)
                pprint(user_info)
            else:
                user_info = vk_client.get_user_info(user_id)
                user_info.update(ask_missed_info(user_id, user_info))
                user_age = user_info.get('user_age', calculate_age(user_info.get('bdate', '0.0.0')))
                user_info['age'] = user_age
                add_user_to_bd(user_info, user_id)
                pprint(user_info)
            persons = vk_client.search_users(user_id, user_info['city'], 3 - user_info['sex'], user_info['age'] - 4, user_info['age']+4)
            pprint(persons)

            show_all_users(user_id, persons)

    elif request == "пока":
        write_msg(user_id, "Пока((")

while True:
    if __name__ == '__main__':
        main()
