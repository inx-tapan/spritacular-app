import io

from .test_setup import TestSetUp
from django.urls import reverse
from PIL import Image


class TestEndPoints(TestSetUp):

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

    def test_user_can_unsuccessfully_register(self):
        """
        test for unsuccessful user signup.
        """
        response = self.client.post(self.register_url, format='json')
        self.assertEqual(response.status_code, 400)

    def test_user_can_successfully_register(self):
        """
        test for successful user signup.
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_login_with_wrong_data(self):
        """
        test for unsuccessful login
        """
        response = self.client.post(self.login_url, {'email': 'test@gmail.com', 'password': 'test'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('detail')[0], 'No active account found with the given credentials.')

    def test_login_view_with_data(self):
        """
        test for successful user login
        """
        register_response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(register_response.status_code, 201)
        login_response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(login_response.status_code, 200)

    def test_user_profile_update(self):
        """
        test for successful profile update
        """
        user_id = self.get_logged_in_user()
        response = self.client.patch(reverse('profile_retrieve_update',
                                             kwargs={'pk': user_id}),
                                     {'profile_image': self.generate_photo_file()}, format='multipart')

        self.assertEqual(response.status_code, 200)
