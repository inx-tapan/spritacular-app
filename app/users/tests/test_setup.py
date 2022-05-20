from rest_framework.test import APITestCase, APIClient
from django.urls import reverse


class TestSetUp(APITestCase):

    def setUp(self):
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

        return super().setUp()

    def tearDown(self):
        return super().tearDown()


