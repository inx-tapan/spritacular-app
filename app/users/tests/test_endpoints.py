import io

import constants
from .test_setup import TestSetUp
from django.urls import reverse
from PIL import Image
from django_rest_passwordreset.models import ResetPasswordToken


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

    def test_user_unsuccessful_change_password_old_pass_is_wrong(self):
        """
        test for invalid old password
        """
        user_id = self.get_logged_in_user()
        data = self.invalid_change_password_data_one
        response = self.client.put(reverse('change-password', kwargs={'pk': user_id}), data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('details')[0], constants.INVALID_OLD_PASS)

    def test_user_unsuccessful_change_password_new_and_confirm_pass_does_not_match(self):
        """
        test for invalid new and confirm password
        """
        user_id = self.get_logged_in_user()
        data = self.invalid_change_password_data_two
        response = self.client.put(reverse('change-password', kwargs={'pk': user_id}), data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('details')[0], constants.NEW_PASS_CONFIRM_PASS_INVALID)

    def test_user_successful_change_password(self):
        """
        test for successful changes password
        """
        user_id = self.get_logged_in_user()
        data = self.valid_change_password_data
        response = self.client.put(reverse('change-password', kwargs={'pk': user_id}), data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_user_unsuccessful_request_password_reset_link(self):
        """
        test for unsuccessful request password reset link
        """
        response = self.client.post('http://127.0.0.1:8000/api/users/password_reset/', data={'email': 'test@gmail.com'}, format='json')
        self.assertEqual(
            response.data.get('email')[0],
            "We couldn't find an account associated with that email. Please try a different e-mail address.")
        self.assertEqual(response.status_code, 400)

    def test_user_successful_request_password_reset_link(self):
        """
        test for successful request password reset link
        """
        user_id = self.get_logged_in_user()
        response = self.client.post('http://127.0.0.1:8000/api/users/password_reset/',
                                    data={'email': 'testemail@gmail.com'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_user_successful_password_reset_link(self):
        """
        test for unsuccessful user password reset
        """
        user_id = self.get_logged_in_user()
        self.client.post('http://127.0.0.1:8000/api/users/password_reset/',
                         data={'email': 'testemail@gmail.com'}, format='json')

        token = ResetPasswordToken.objects.filter().latest('id').key
        response = self.client.post('http://127.0.0.1:8000/api/users/password_reset/confirm/',
                                    data={'password': 'testing@1234', 'token': token}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('status'), 'OK')

        # Login after password reset with new password.
        login_response = self.client.post(self.login_url, {'email': 'testemail@gmail.com', 'password': 'testing@1234'},
                                          format='json')

        self.assertEqual(login_response.status_code, 200)

    def test_user_add_camera_settings_with_incomplete_data(self):
        """
        test user adding camera settings with incomplete data
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('camera_setting'), self.invalid_camera_data, format='json')
        self.assertEqual(response.data.get('camera_type')[0], 'This field may not be blank.')
        self.assertEqual(response.data.get('focal_length')[0], 'This field may not be blank.')

    def test_user_add_camera_settings(self):
        """
        test user adding camera settings with complete data
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('camera_setting'), self.camera_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_user_update_camera_settings(self):
        """
        test user updating camera settings
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('camera_setting'), self.camera_data, format='json')
        new_data = {"camera_type": "sony", "iso": 100, "shutter_speed": 2, "fps": 60, "lens_type": "prime",
                    "focal_length": "12", "aperture": 1.4, "question_field_one": "Camera Time",
                    "question_field_two": "Polarizing Filter"}
        response = self.client.patch(reverse('camera_setting'), new_data, format='json')
        self.assertEqual(response.status_code, 200)



