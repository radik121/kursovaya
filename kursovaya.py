import json, requests
from pprint import pprint

with open('vk_photos.json') as f:
    data = json.load(f)

with open('ya.token.txt') as f:
    ya_token = f.read().strip()


class PhotoVk_to_YaDisk:
    def __init__(self, user_id, disk_token, token=data['token'], version=data['v']):
        self.token = token
        self.version = version
        self.user_id = user_id
        self.disk_token = disk_token

    def get_vk_photos(self):
        api = requests.get('https://api.vk.com/method/photos.get', params={
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            # 'no_service_albums': 1,
            'count': 5,
            'access_token': self.token,
            'v': self.version
        })
        res = json.loads(api.text)
        photo_dict = {}
        info_list = []
        for photo in res['response']['items']:
            if str(photo['likes']['count']) in photo_dict:
                photo_dict[str(photo['likes']['count']) + '_' + str(photo['date'])] = photo['sizes'][-1]['url']
                info_list.append({'file_name': str(photo['likes']['count']) + '_' + str(photo['date']) + '.jpg',
                                  'size': photo['sizes'][-1]['type']})
            else:
                photo_dict[str(photo['likes']['count'])] = photo['sizes'][-1]['url']
                info_list.append({'file_name': str(photo['likes']['count']) + '.jpg',
                                  'size': photo['sizes'][-1]['type']})

        with open('info_files.json', 'w') as info:
            json.dump(info_list, info, indent=2)
            print('json-файл с информацией создан')

        return photo_dict

    def folder_to_disk(self):
        url_folder = 'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.disk_token)
        }
        params_folder = {
            'path': 'vk_photos'
        }
        folder = requests.put(url_folder, params=params_folder, headers=headers)
        if folder.status_code == 201:
            print('Папка на диске создана')

        for filename, url in self.get_vk_photos().items():
            url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            params_disk = {
                'path': 'vk_photos/' + filename + '.jpg',
                'url': url
            }
            upload = requests.post(url_upload, headers=headers, params=params_disk)
            # res = upload.json()
            # print(res)
            print(f'Фото {filename} успешно загружено!')


i = PhotoVk_to_YaDisk(9401276, ya_token)
# pprint(i.get_vk_photos())
i.folder_to_disk()
