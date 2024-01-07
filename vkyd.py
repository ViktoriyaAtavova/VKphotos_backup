import requests
import json
from datetime import datetime
from time import gmtime, strftime
from config import token_VK, token_YD, id_VK

class VKAPIPhotos:

    api_base_url = 'https://api.vk.com/method'

    def __init__(self, user_id):
        self.user_id = user_id

    def get_commom_params(self):
        return {
            'access_token': token_VK,
            'v': '5.154',
            'extended': 1
        }

    def get_likes_frequency(self, photos_list:list):
        likes_frequency_dict = {}
        for photo in photos_list:
            likes = photo['likes']['count']
            if likes in likes_frequency_dict:
                likes_frequency_dict[likes] += 1
            else:
                likes_frequency_dict.setdefault(likes, 1)
        return likes_frequency_dict

    def get_photos(self, photos_count=5):
        base_params = self.get_commom_params()
        base_params.update({'owner_id': self.user_id, 'album_id': 'profile'})
        response = requests.get(f'{self.api_base_url}/photos.get', params=base_params)
        photos_list = response.json()['response']['items'][-photos_count:]
        likes_frequency = self.get_likes_frequency(photos_list)
        biggest_photos_list = []
        for photo in photos_list:
            likes = photo['likes']['count']
            sizes = photo['sizes']
            biggest_photo = None
            for size in sizes:
                if biggest_photo is None or size['height'] > biggest_photo['height']:
                    biggest_photo = size
            if likes_frequency[likes] == 1:
                biggest_photos_list.append({'file_name': str(likes),
                                            'size': biggest_photo['type'],
                                            'url': biggest_photo['url']})
            else:
                timestamp = photo['date']
                formatted_date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
                biggest_photos_list.append({'file_name': f'{str(likes)}_{formatted_date}',
                                            'size': biggest_photo['type'],
                                            'url': biggest_photo['url']})
        return biggest_photos_list

    def save_json(self, photos:list):
        formatted_date_time = strftime("%Y-%m-%d_%H_%M_%S", gmtime())
        with open(f'photos_{formatted_date_time}.json', 'w') as file:
            file.write(json.dumps(photos))

class YDiskAPI:

    api_base_url_YD = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.token = token

    def get_commom_headers(self):
        return {
            'Authorization': self.token,
        }


    def create_folder(self, folder_name):
        base_params = {'path': f'{folder_name}'}
        base_headers = self.get_commom_headers()
        response = requests.put(self.api_base_url_YD, params=base_params, headers=base_headers)

    def load_files(self, photos, folder_name='Profile Photos'):
        base_headers = self.get_commom_headers()
        for index, photo in enumerate(photos):
            log_start_loading(len(photos), index, photo['file_name'])
            response = requests.post(self.api_base_url_YD + '/upload', params={
                'url': photo['url'],
                'path': f'{folder_name}/{photo["file_name"]}'
            }, headers=base_headers)
            print (log_end_loading(response.status_code))


def log_start_loading(files_count, file_index, name):
    print(f'Загрузка фото: ({name}) {file_index +1}/{files_count}')


def log_end_loading(status_code):
    if 200 <= status_code < 300:
        return f'Загрузка прошла успешна'
    else:
        return f'Ошибка загрузки'


if __name__ == '__main__':
     vk_client = VKAPIPhotos(id_VK)
     photos_inf = vk_client.get_photos()
     vk_client.save_json(photos_inf)
     yd_api = YDiskAPI(token_YD)
     yd_api.create_folder('Profile Photos')
     yd_api.load_files(photos_inf)



