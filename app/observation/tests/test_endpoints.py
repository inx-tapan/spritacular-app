from django.urls import reverse

import constants
from users.tests.test_setup import TestSetUp


class TestEndPoints(TestSetUp):

    # def test_successful_observation_upload(self):
    #     """
    #     User successful single, multiple image observation upload
    #     """
    #     user_id = self.get_logged_in_user()
    #     response = self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     self.assertEqual(response.status_code, 201)
    #     response = self.client.post(reverse('upload_observation'), self.multiple_image_observation_data,
    #                                 format='multipart')
    #     self.assertEqual(response.status_code, 201)
    #
    # def test_multiple_observation_upload_with_single_image_type(self):
    #     """
    #     User multiple image observation upload with single image type selected
    #     """
    #     user_id = self.get_logged_in_user()
    #     response = self.client.post(reverse('upload_observation'), self.invalid_single_image_observation_data,
    #                                 format='multipart')
    #     self.assertEqual(response.data[0], constants.SINGLE_IMAGE_VALID)
    #     self.assertEqual(response.status_code, 400)
    #
    # def test_more_than_three_observation_upload_in_multiple_type(self):
    #     """
    #     user giving more than 3 images in multiple observation upload type
    #     """
    #     user_id = self.get_logged_in_user()
    #     response = self.client.post(reverse('upload_observation'), self.invalid_multiple_image_observation_data,
    #                                 format='multipart')
    #     self.assertEqual(response.data[0], constants.MULTIPLE_IMAGE_VALID)
    #     self.assertEqual(response.status_code, 400)

    def test_user_save_as_draft_observation_upload(self):
        """
        user successful save observation as draft
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('upload_observation'), self.draft_observation_data, format='multipart')
        print(response.data)



