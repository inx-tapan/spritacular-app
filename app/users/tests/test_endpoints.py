from .test_setup import TestSetUp


class TestEndPoints(TestSetUp):

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
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.login_url, self.user_data, format='json')

