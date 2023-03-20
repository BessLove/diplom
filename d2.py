import requests
from bd import Seen_persones, session

with open('token_app.txt', "r") as file:
    token = file.readline()


class VkApiClient:
    CNT = 0

    def __init__(self, base_url: str = "https://api.vk.com/"):
        self.token = token
        self.api_version = '5.131'
        self.base_url = base_url

    def general_params(self):
        return {
            "access_token": self.token,
            "v": self.api_version,
        }

    def get_user_info(self, user_ids):
        params = {
            "user_ids": user_ids,
            "fields": "bdate, city, sex"
        }
        user_info_dict = requests.get(f"{self.base_url}/method/users.get",
                                      params={**params, **self.general_params()}).json()['response'][0]
        if user_info_dict.get('city'):
            user_info_dict['city'] = user_info_dict.get('city', {}).get('id')
        return user_info_dict
        # return [user_info_dict.get('first_name'), user_info_dict.get('bdate'), user_info_dict.get('sex'), user_info_dict.get('city')['id']]

    def search_users(self, user_id, city_id=1, sex=(1, 2), age_from=18, age_to=99):
        params = {
            "sort": 0,
            "offset": 0,
            "count": 300,
            "city_id": city_id,
            "sex": sex,
            "status": (1, 6),
            "age_from": age_from,
            "age_to": age_to,
            "has_photo": 1,
            "fields": "bdate, city, sex, relation"
        }
        users = requests.get(f"{self.base_url}/method/users.search",
                             params={**params, **self.general_params()}).json()['response']['items']

        # return requests.get(f"{self.base_url}/method/users.search",
        #                     params={**params, **self.general_params()}).json()['response']['items']

        users_list = []
        for user in users:
            if not user['is_closed'] and user.get('city', {}).get('id') == 1:
                person_id = user.get('id')
                # проверяем есть ли пара в просмотренных
                q = session.query(Seen_persones).filter(Seen_persones.seen_person_id == person_id,
                                                        Seen_persones.user_id_user == user_id).all()
                if not bool(q):
                    users_list.append(
                        {'user_id': person_id, 'first_name': user.get('first_name'), 'bdate': user.get('bdate'),
                         'sex': user.get('sex'), 'city': user.get('city', {}).get('id')})
                else:
                    continue
        return users_list

    def get_user_photos(self, owner_id):
        params = {
            "owner_id": owner_id,
            "album_id": 'profile',
            "extended": '1'
        }
        try:
            photos = requests.get(f"{self.base_url}/method/photos.get",
                                  params={**params, **self.general_params()}).json()['response']
            # return requests.get(f"{self.base_url}/method/photos.get",
            #                     params={**params, **self.general_params()}).json()['response']

            if photos['count'] < 3:
                return False
            best_photos = sorted(photos.get('items'),
                                 key=lambda x: (x['likes']['count'], x['comments']['count']), reverse=True)[:3]
            # return best_photos
            list_photos = []
            for photo in best_photos:
                list_photos.append(f"photo{owner_id}_{photo['id']}")
            return list_photos
        except KeyError:
            pass

    def get_city_id(self, city):
        params = {
            # "country_id": 1,
            "q": city,
            "count": 1
        }
        city_id = requests.get(f"{self.base_url}/method/database.getCities",
                               params={**params, **self.general_params()}).json()['response']['items'][0]['id']

        return city_id


vk_client = VkApiClient()

# person = vk_client.search_users(7889219, 1, 1, 16, 24)
# person_photos = vk_client.get_user_photos('9254819') #555686640
# pprint(person_photos)
# user = vk_client.get_user_info('7889219') #44125188   7889219   59303115
# pprint(person)
# for pers in person:
#     print(pers)
# pprint(user)
# city = vk_client.get_city_id('москва')
# print(city)
# user_name, bdate, sex, city_id = vk_client.get_user_info('7889219')
# print(user_name)
