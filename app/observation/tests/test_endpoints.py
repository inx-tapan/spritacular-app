from django.urls import reverse

import constants
from observation.models import Category, Observation
from users.models import User
from users.tests.test_setup import TestSetUp


class TestEndPoints(TestSetUp):

    @classmethod
    def setUpClass(cls):
        super(TestEndPoints, cls).setUpClass()
        print("Category data created")
        data = ["Sprite", "Blue Jet", "Elve", "Halo", "Gigantic Jet", "Secondary Jet"]
        for i in data:
            Category.objects.create(title=i, is_default=True)

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
    #
    # def test_user_save_as_draft_observation_upload(self):
    #     """
    #     user successful save observation as draft
    #     """
    #     user_id = self.get_logged_in_user()
    #     response = self.client.post(reverse('upload_observation'), self.draft_observation_data, format='multipart')
    #     self.assertEqual(response.status_code, 201)
    #
    # def test_user_draft_observation_to_submit(self):
    #     """
    #     user successful submit draft observation
    #     """
    #     user_id = self.get_logged_in_user()
    #     draft_response = self.client.post(reverse('upload_observation'), self.draft_observation_data,
    #                                       format='multipart')
    #     self.assertEqual(draft_response.status_code, 201)
    #     submit_response = self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     self.assertEqual(submit_response.status_code, 201)
    #
    # def test_user_observation_comment(self):
    #     """
    #     user observation comment
    #     """
    #     user_id = self.get_logged_in_user()
    #     self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     observation_id = Observation.objects.filter().last().id
    #     comment_response = self.client.post(reverse('observation_comment', kwargs={'pk': observation_id}),
    #                                         {'text': 'hello world comment testing!'}, format='json')
    #     print(comment_response.data)
    #     self.assertEqual(comment_response.status_code, 201)
    #
    # def test_user_observation_comment_without_observation_id(self):
    #     """
    #     test wrong observation id from frontend for user comment on observation.
    #     """
    #     user_id = self.get_logged_in_user()
    #     response = self.client.post(reverse('observation_comment', kwargs={'pk': 100}),
    #                                 {'text': 'hello world comment testing!'},
    #                                 format='json')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(response.data.get('detail'), 'Not found.')
    #
    # def test_user_observation_like(self):
    #     """
    #     User successful like to a observation
    #     """
    #     user_id = self.get_logged_in_user()
    #     self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     observation_id = Observation.objects.filter().last().id
    #     response = self.client.post(reverse('observation_like', kwargs={'pk': observation_id}), {'is_like': '1'},
    #                                 format='json')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_user_observation_like_on_invalid_data(self):
    #     """
    #      user like observation with invalid observation id
    #     """
    #     user_id = self.get_logged_in_user()
    #     response = self.client.post(reverse('observation_like', kwargs={'pk': 100}), {'is_like': '1'},
    #                                 format='json')
    #     self.assertEqual(response.data.get('detail'), 'Not found.')
    #     self.assertEqual(response.status_code, 404)
    #
    # def test_user_observation_dislike(self):
    #     """
    #     user observation dislike test
    #     :return:
    #     """
    #     user_id = self.get_logged_in_user()
    #     self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     observation_id = Observation.objects.filter().last().id
    #     response = self.client.post(reverse('observation_like', kwargs={'pk': observation_id}), {'is_like': '0'},
    #                                 format='json')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_user_observation_watch_count(self):
    #     """
    #     user observation watch count test
    #     """
    #     user_id = self.get_logged_in_user()
    #     self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     observation_id = Observation.objects.filter().last().id
    #     response = self.client.post(reverse('observation_watch_count', kwargs={'pk': observation_id}), format='json')
    #     self.assertEqual(response.status_code, 200)

    # def test_admin_user_observation_verification(self):
    #     """
    #     Admin user approving observation test
    #     """
    #     user_id = self.get_logged_in_user()
    #     user_obj = User.objects.get(id=user_id)
    #     user_obj.is_superuser = True
    #     user_obj.is_staff = True
    #     user_obj.save(update_fields=['is_superuser', 'is_staff'])
    #     self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     observation_id = Observation.objects.filter().last().id
    #     response = self.client.post(reverse('observation_approve_reject', kwargs={'pk': observation_id}),
    #                                 self.observation_approve_data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data.get('success'), 'Observation Approved.')

    # def test_admin_user_observation_reject(self):
    #     """
    #     Admin user rejecting observation test
    #     """
    #     user_id = self.get_logged_in_user()
    #     user_obj = User.objects.get(id=user_id)
    #     user_obj.is_superuser = True
    #     user_obj.is_staff = True
    #     user_obj.save(update_fields=['is_superuser', 'is_staff'])
    #     self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
    #     observation_id = Observation.objects.filter().last().id
    #     response = self.client.post(reverse('observation_approve_reject', kwargs={'pk': observation_id}),
    #                                 self.observation_reject_data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data.get('success'), 'Observation Rejected.')

    def test_normal_user_trying_to_approve_observation(self):
        """
        Normal user trying to approve/reject observation
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('observation_approve_reject', kwargs={'pk': observation_id}),
                                    self.observation_approve_data, format='json')
        self.assertEqual(response.data.get('detail'), 'You must be a admin user.')
        self.assertEqual(response.status_code, 403)
