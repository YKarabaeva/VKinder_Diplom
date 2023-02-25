from random import randrange

import vk_api
import datetime
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
from DB_VKinder import add_find_person
from DB_VKinder import check_users

with open('group_token.txt', 'r') as file:
    group_token = file.readline()
with open('token_app.txt', 'r') as file:
    user_token = file.readline()

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), })


def get_user_info(user_id):
    url = 'https://api.vk.com/method/users.get'
    params = {'user_id': user_id,
              'access_token': user_token,
              'v': '5.131',
              'fields': 'name, surname, bdate, sex, relation, home_town'
              }
    res = requests.get(url, params=params)
    user_info = res.json()
    try:
        user_information = user_info['response']
    except KeyError:
        write_msg(user_id, "Ошибка получения данных (1), попробуйте еще раз!")
    try:
        user_information_lst = user_information[0]
    except IndexError:
        write_msg(user_id, "Ошибка при поиске данных (1), попробуйте еще раз!")
    user_name = user_information_lst['first_name']
    user_surname = user_information_lst['last_name']
    user_sex = user_information_lst['sex']
    user_bdate = user_information_lst['bdate']
    user_relation = user_information_lst['relation']
    user_town = user_information_lst['home_town']
    return user_name, user_surname, user_sex, user_bdate, user_relation, user_town


def get_user_sex(user_sex, user_id):
    sex_to_find = 0
    if user_sex == 1:
        sex_to_find = 2
    elif user_sex == 2:
        sex_to_find = 1
    elif user_sex == 0:
        write_msg(user_id, "У вас не указан пол на странице. Если Вы хотите найти девушку - введите 1, если парня - 2")
        for event_sex in longpoll.listen():
            if event_sex.type == VkEventType.MESSAGE_NEW and event_sex.to_me:
                person_answer = event_sex.text
                if person_answer == "1":
                    sex_to_find = 1
                if person_answer == "2":
                    sex_to_find = 2
    return sex_to_find


def get_user_age_min(user_bdate, user_id):
    date_split = user_bdate.split('.')
    if len(date_split) == 3:
        year = int(date_split[2])
        year_current = int(datetime.date.today().year)
        age_for_find = year_current - year
        write_msg(user_id, 'Мы определили Ваш возраст, желаете использовать его для нижней границы поиска'
                           ' (напишите "Использовать мой возраст") или зададим минимальный возраст для поиска '
                           ' (напишите "Задать минимальный возраст")?')
        for event_age_min in longpoll.listen():
            if event_age_min.type == VkEventType.MESSAGE_NEW and event_age_min.to_me:
                age_answer = event_age_min.text.lower()
                if age_answer == "использовать мой возраст":
                    age_for_find_min = age_for_find
                    return age_for_find_min
                if age_answer == "задать минимальный возраст":
                    write_msg(user_id, 'Введите минимальный возраст для поиска половинки: ')
                    for event_age_min_insert in longpoll.listen():
                        if event_age_min_insert.type == VkEventType.MESSAGE_NEW and event_age_min_insert.to_me:
                            age_for_find_min = int(event_age_min_insert.text)
                            return age_for_find_min
    elif len(date_split) == 2 or user_bdate == 'None':
        write_msg(user_id, 'Кажется, на Вашей странице не введен год рождения. Введите Ваш возраст:')
        for event_age_insert in longpoll.listen():
            if event_age_insert.type == VkEventType.MESSAGE_NEW and event_age_insert.to_me:
                age_for_find_min = event_age_insert.text
                return age_for_find_min


def get_user_age_max(user_bdate, user_id):
    date_split = user_bdate.split('.')
    if len(date_split) == 3:
        year = int(date_split[2])
        year_current = int(datetime.date.today().year)
        age_for_find = year_current - year
        write_msg(user_id, 'Мы определили Ваш возраст, желаете использовать его для верхней границы поиска'
                           ' (напишите "Использовать мой возраст") или зададим максимальный возраст для поиска '
                           ' (напишите "Задать максимальный возраст")?')
        for event_age_max in longpoll.listen():
            if event_age_max.type == VkEventType.MESSAGE_NEW and event_age_max.to_me:
                age_answer = event_age_max.text.lower()
                if age_answer == "использовать мой возраст":
                    age_for_find_max = age_for_find
                    return age_for_find_max
                if age_answer == "задать максимальный возраст":
                    write_msg(user_id, 'Введите максимальный возраст для поиска половинки: ')
                    for event_age_max_insert in longpoll.listen():
                        if event_age_max_insert.type == VkEventType.MESSAGE_NEW and event_age_max_insert.to_me:
                            age_for_find_max = event_age_max_insert.text
                            return age_for_find_max
    elif len(date_split) == 2 or user_bdate == 'None':
        write_msg(user_id, 'Давайте зададим максимальный возраст для поиска.')
        write_msg(user_id, 'Введите максимальный возраст для поиска половинки: ')
        for event_age_insert_second in longpoll.listen():
            if event_age_insert_second.type == VkEventType.MESSAGE_NEW and event_age_insert_second.to_me:
                age_for_find_max = event_age_insert_second.text
                return age_for_find_max


def get_user_relation(user_relation, user_id):
    relation_list = (2, 3, 4, 5, 6, 7, 8)
    if user_relation in relation_list:
        write_msg(user_id, "Скорее всего, у Вас есть отношения, Вы точно хотите воспользоваться ботом? Да/Нет?")
        for event_relation in longpoll.listen():
            if event_relation.type == VkEventType.MESSAGE_NEW and event_relation.to_me:
                relation_answer = event_relation.text.lower()
                if relation_answer == "да":
                    write_msg(user_id, "Хорошо, продолжаем работу!")
                if relation_answer == "нет":
                    write_msg(user_id, "Спасибо за уделенное время! До свидания!")
    return user_relation


def get_user_town(user_town, user_id):
    if user_town == 'NULL':
        write_msg(user_id, "На Вашей странице не указан город, введите, пожалуйста, город:")
        for event_town in longpoll.listen():
            if event_town.type == VkEventType.MESSAGE_NEW and event_town.to_me:
                user_town = event_town.text
                return user_town
    return user_town


def search_people(user_id, cand_sex, cand_age_min, cand_age_max, cand_town):
    url = 'https://api.vk.com/method/users.search'
    params = {'user_id': user_id,
              'access_token': user_token,
              'v': '5.131',
              'count': 100,
              'fields': 'first_name, last_name, id, is_closed',
              'sex': cand_sex,
              'age_from': cand_age_min,
              'age_to': cand_age_max,
              'home_town': cand_town,
              'relation': '1' or '6',
              'offset': 1
              }
    res = requests.get(url, params=params)
    req = res.json()
    try:
        people_vk = req['response']
    except KeyError:
        write_msg(user_id, "Ошибка получения данных (2), попробуйте еще раз!")
    try:
        people_list = people_vk['items']
    except KeyError:
        write_msg(user_id, "Ошибка при поиске данных (2), попробуйте еще раз!")
    people_open = []
    for person in people_list:
        if person['is_closed'] == False:
            people_open.append(person)
    return people_open


def count_photo(photo_ids_max_likes, candidate_id):
    photo_to_send = ""
    if len(photo_ids_max_likes) == 3:
        photo_to_send_first = 'photo' + candidate_id + '_' + photo_ids_max_likes[0]
        photo_to_send_second = 'photo' + candidate_id + '_' + photo_ids_max_likes[1]
        photo_to_send_third = 'photo' + candidate_id + '_' + photo_ids_max_likes[2]
        photo_to_send = photo_to_send_first + ',' + photo_to_send_second + ',' + photo_to_send_third
    if len(photo_ids_max_likes) == 2:
        photo_to_send_first = 'photo' + candidate_id + '_' + photo_ids_max_likes[0]
        photo_to_send_second = 'photo' + candidate_id + '_' + photo_ids_max_likes[1]
        photo_to_send = photo_to_send_first + ',' + photo_to_send_second
    if len(photo_ids_max_likes) == 1:
        photo_to_send_first = 'photo' + candidate_id + '_' + photo_ids_max_likes[0]
        photo_to_send = photo_to_send_first
    if len(photo_ids_max_likes) == 0:
        write_msg(event.user_id, "У пользователя нет фотографий")
        photo_to_send = 0
    return photo_to_send


def get_photos(candidate_id, user_id):
    url = 'https://api.vk.com/method/photos.get'
    params = {'access_token': user_token,
              'owner_id': candidate_id,
              'album_id': 'profile',
              'extended': 1,
              'v': '5.131',
              'count': 15
              }
    res = requests.get(url, params=params)
    photos = res.json()
    needed_photos = dict()
    try:
        photo_info = photos['response']
    except KeyError:
        write_msg(user_id, "Ошибка получения данных (3), попробуйте еще раз!")
    try:
        photo_information = photo_info['items']
    except KeyError:
        write_msg(user_id, "Ошибка при поиске данных (3), попробуйте еще раз!")
    for inf in photo_information:
        id_photo = str(inf['id'])
        likes_photo = inf['likes']['count']
        needed_photos[id_photo] = likes_photo
    max_likes = sorted(needed_photos, key=needed_photos.get, reverse=True)[:3]
    return max_likes


def result(user_id, person):
    if check_users(person_from_hundred['id']) is True:
        if person_from_hundred['is_closed'] is False:
            candidate_name = person['first_name']
            candidate_last_name = person['last_name']
            candidate_id = str(person['id'])
            candidate_link = 'vk.com/id' + str(person['id'])
            candidate_info = candidate_name + " " + candidate_last_name + " " + candidate_link
            write_msg(user_id, candidate_info)
            photo_ids_max_likes = get_photos(candidate_id, user_id)
            count_photo_to_send = count_photo(photo_ids_max_likes, candidate_id)
            add_find_person(candidate_id, candidate_name, candidate_last_name, count_photo_to_send)
            vk.method('messages.send', {'user_id': user_id,
                                        'access_token': user_token,
                                        'message': "Фотографии:",
                                        'attachment': count_photo_to_send,
                                        'random_id': 0
                                        })
            return candidate_id


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()
            if request == "запустить бот":
                find_user_id = str(event.user_id)
                write_msg(event.user_id, f"Привет, {get_user_info(find_user_id)[0]}! "
                                         f"Сейчас мы найдем подходящих для Вас пользователей в "
                                         f"соответстсвии с данными Вашей страницы")
                candidate_sex = get_user_sex(get_user_info(find_user_id)[2], find_user_id)
                candidate_age_min = get_user_age_min(get_user_info(find_user_id)[3], find_user_id)
                candidate_age_max = get_user_age_max(get_user_info(find_user_id)[3], find_user_id)
                candidate_town = get_user_town(get_user_info(find_user_id)[5], find_user_id)
                people_list_hundred = search_people(find_user_id, candidate_sex, candidate_age_min,
                                                    candidate_age_max, candidate_town)
                person_from_hundred = people_list_hundred.pop()
                result(event.user_id, person_from_hundred)
                repeat = "Yes"
                while repeat == "Yes":
                    write_msg(event.user_id, "Желаете продолжить поиск?")
                    for event_repeat in longpoll.listen():
                        if event_repeat.type == VkEventType.MESSAGE_NEW and event_repeat.to_me:
                            continue_answer = event_repeat.text.lower()
                            if continue_answer == "да":
                                if len(people_list_hundred) == 0:
                                    people_list_hundred = search_people(find_user_id, candidate_sex, candidate_age_min,
                                                                        candidate_age_max, candidate_town)
                                    person_from_hundred = people_list_hundred.pop()
                                    result(event.user_id, person_from_hundred)
                                else:
                                    person_from_hundred = people_list_hundred.pop()
                                    result(event.user_id, person_from_hundred)
                            if continue_answer == "нет":
                                write_msg(event.user_id, "Спасибо за уделенное время! До свидания!")
                                repeat = "No"
                            break
            else:
                write_msg(event.user_id, "Если вы хотите начать работу с сервисом знакомств, "
                                         "напишите - 'Запустить бот'")
