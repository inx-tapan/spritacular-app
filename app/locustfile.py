import io
import json
import os
import django
from PIL import Image

from locust import HttpUser, task
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spritacular.settings")
django.setup()


class UploadObservation(HttpUser):

    def generate_photo_file(self):
        """
        Generate temporary image object for image and file fields.
        """
        file = io.BytesIO()
        image = Image.new('RGBA', size=(4000, 4000), color=(155, 0, 0))
        image.save(file, format='png')
        file.name = 'test.png'
        file.seek(0)

        return file

    def on_start(self):
        response = self.client.post(reverse('login'), json={"email": "tapan.inx@gmail.com", "password": "tapan@1234"})
        self.client.headers.update({'Authorization': f"Bearer {json.loads(response.text).get('access')}"})

    # @task
    # def gallery(self):
    #     self.client.get(reverse('gallery'))

    @task
    def upload_observation(self):
        self.multiple_image_observation_data = {"image_0": self.generate_photo_file(),
                                                "image_1": self.generate_photo_file(),
                                                "image_2": self.generate_photo_file(), "data": """{
                                "image_type": 2,
                                "map_data": [
                                    {
                                        "image_id": 0,
                                        "image": "",
                                        "category_map": {"category": [1]},
                                        "location": "l1",
                                        "place_uid": "askhdjashkjdashkjas",
                                        "country_code": "US",
                                        "longitude": "40.123",
                                        "latitude": "44.123",
                                        "obs_date": "2022-02-25",
                                        "obs_time": "13:00:00",
                                        "timezone": "Africa/Lagos",
                                        "azimuth": "120",
                                        "is_precise_azimuth": 0
                                    },
                                    {
                                        "image_id": 1,
                                        "image": "",
                                        "category_map": {"category": [2]},
                                        "location": "l1",
                                        "place_uid": "askhdjashkjdashkjas",
                                        "country_code": "US",
                                        "longitude": "40.123",
                                        "latitude": "44.123",
                                        "obs_date": "2022-02-25",
                                        "obs_time": "13:00:00",
                                        "timezone": "Africa/Lagos",
                                        "azimuth": "120",
                                        "is_precise_azimuth": 0
                                    },
                                    {
                                        "image_id": 2,
                                        "image": "",
                                        "category_map": {"category": [3]},
                                        "location": "l1",
                                        "place_uid": "askhdjashkjdashkjas",
                                        "country_code": "US",
                                        "longitude": "40.123",
                                        "latitude": "44.123",
                                        "obs_date": "2022-02-25",
                                        "obs_time": "13:00:00",
                                        "timezone": "Africa/Lagos",
                                        "azimuth": "120",
                                        "is_precise_azimuth": 0
                                    }
                                ],
                                "camera": {
                                    "observation_settings": "True",
                                    "camera_type": "Sony",
                                    "iso": "",
                                    "shutter_speed": "",
                                    "fps": "",
                                    "lens_type": "prime",
                                    "focal_length": "35",
                                    "aperture": 1.4,
                                    "question_field_one": "",
                                    "question_field_two": ""
                                },
                                "elevation_angle": 20,
                                "video_url": "https://youtube-observationurl.com",
                                "story": "user experience..."
                    }"""}

        response = self.client.post(reverse('upload_observation'), data=self.multiple_image_observation_data,
                                    files={"image_0": self.generate_photo_file(),
                                           "image_1": self.generate_photo_file(),
                                           "image_2": self.generate_photo_file()})
        print(f"<=={response.text}||{response.status_code}==>")


