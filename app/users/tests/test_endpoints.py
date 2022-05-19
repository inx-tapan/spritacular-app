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

