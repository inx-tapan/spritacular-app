import io

from PIL import Image
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.test import override_settings


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestSetUp(APITestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.register_url = reverse('register')

        self.user_data = {
            'first_name': "first",
            'last_name': 'last',
            'email': 'testemail@gmail.com',
            'password': 'pass@1234',
            'location': 'Seville, Andalusia, Spain',
            'place_id': 'ChIJkWK-Eg0RSFb-HGIY8DQ',
            "location_metadata": None
        }

        self.invalid_change_password_data_one = {'old_password': 'test',
                                                 'new_password': 'test@1234',
                                                 'confirm_password': 'test@1234'}

        self.invalid_change_password_data_two = {'old_password': 'pass@1234',
                                                 'new_password': 'test@1234',
                                                 'confirm_password': 'test@123'}

        self.valid_change_password_data = {'old_password': 'pass@1234',
                                           'new_password': 'test@1234',
                                           'confirm_password': 'test@1234'}

        self.camera_data = {
            "camera_type": "canon",
            "iso": 100,
            "shutter_speed": 2,
            "fps": 60,
            "lens_type": "prime",
            "focal_length": 35,
            "aperture": 1.4,
            "question_field_one": "Camera Time",
            "question_field_two": "Polarizing Filter"
        }

        self.invalid_camera_data = {
            "camera_type": "",
            "iso": 100,
            "shutter_speed": 2,
            "fps": 60,
            "lens_type": "prime",
            "focal_length": "",
            "aperture": 1.4,
            "question_field_one": "Camera Time",
            "question_field_two": "Polarizing Filter"
        }

        self.observation_data = {"image_0": self.generate_photo_file(), "data": """{
                "image_type": 1,
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
        self.draft_observation_data = {"image_0": self.generate_photo_file(), "data": """{
                "is_draft": "True",
                "image_type": 1,
                "map_data": [
                    {
                        "image_id": 0,
                        "image": "",
                        "category_map": {"category": [1]},
                        "location": "",
                        "place_uid": "",
                        "country_code": "",
                        "longitude": "",
                        "latitude": "",
                        "obs_date": null,
                        "obs_time": null,
                        "timezone": "",
                        "azimuth": "",
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
        self.multiple_image_observation_data = {"image_0": self.generate_photo_file(), "image_1": self.generate_photo_file(), "image_2": self.generate_photo_file(), "data": """{
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
        self.invalid_single_image_observation_data = {"image_0": self.generate_photo_file(), "image_1": self.generate_photo_file(), "image_2": self.generate_photo_file(), "data": """{
                    "image_type": 1,
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
        self.invalid_multiple_image_observation_data = {"image_0": self.generate_photo_file(), "image_1": self.generate_photo_file(), "image_2": self.generate_photo_file(), "image_3": self.generate_photo_file(), "data": """{
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
                                    },
                                    {
                                        "image_id": 3,
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

    def generate_photo_file(self):
        """
        Generate temporary image object for image and file fields.
        """
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, format='png')
        file.name = 'test.png'
        file.seek(0)

        return file

    def get_logged_in_user(self):
        """
        Get logged in user.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, self.user_data, format='json')
        # set bearer token for authentication
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + login_response.data.get('access'))

        return login_response.data.get('id')

    def tearDown(self):
        return super().tearDown()


