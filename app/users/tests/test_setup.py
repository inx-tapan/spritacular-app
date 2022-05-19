from rest_framework.test import APITestCase
from django.urls import reverse


class TestSetUp(APITestCase):

    def setUp(self):
        self.login_url = reverse('token_obtain_pair')
        self.register_url = reverse('register')

        self.user_data = {
            'first_name': "first",
            'last_name': 'last',
            'email': 'testemail@gmail.com',
            'password': 'pass@1234',
            'location': 'Seville, Andalusia, Spain',
            'place_id': 'ChIJkWK-Eg0RSFb-HGIY8DQ',
            'location_metadata': {"lat": 12, "lng": -5}
        }
        return super().setUp()

    def tearDown(self):
        return super().tearDown()


