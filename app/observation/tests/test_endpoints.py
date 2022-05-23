from django.urls import reverse

from users.tests.test_setup import TestSetUp


class TestEndPoints(TestSetUp):

    def test_successful_observation_upload(self):
        """
        User successful single image observation upload
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        print(response.data)


