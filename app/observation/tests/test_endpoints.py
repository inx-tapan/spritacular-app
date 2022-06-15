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

    def test_successful_observation_upload(self):
        """
        User successful single, multiple image observation upload
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('upload_observation'), self.multiple_image_observation_data,
                                    format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_multiple_observation_upload_with_single_image_type(self):
        """
        User multiple image observation upload with single image type selected
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('upload_observation'), self.invalid_single_image_observation_data,
                                    format='multipart')
        self.assertEqual(response.data[0], constants.SINGLE_IMAGE_VALID)
        self.assertEqual(response.status_code, 400)

    def test_more_than_three_observation_upload_in_multiple_type(self):
        """
        user giving more than 3 images in multiple observation upload type
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('upload_observation'), self.invalid_multiple_image_observation_data,
                                    format='multipart')
        self.assertEqual(response.data[0], constants.MULTIPLE_IMAGE_VALID)
        self.assertEqual(response.status_code, 400)

    def test_user_save_as_draft_observation_upload(self):
        """
        user successful save observation as draft
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('upload_observation'), self.draft_observation_data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_user_draft_observation_to_submit(self):
        """
        user successful submit draft observation
        """
        user_id = self.get_logged_in_user()
        draft_response = self.client.post(reverse('upload_observation'), self.draft_observation_data,
                                          format='multipart')
        observation_id = Observation.objects.filter().last().id
        self.assertEqual(draft_response.status_code, 201)
        submit_response = self.client.put(reverse('update_observation', kwargs={'pk': observation_id}),
                                          self.observation_data, format='multipart')
        self.assertEqual(submit_response.status_code, 200)

    def test_user_draft_observation_invalid_data_submit(self):
        user_id = self.get_logged_in_user()
        draft_response = self.client.post(reverse('upload_observation'), self.draft_observation_data,
                                          format='multipart')
        self.assertEqual(draft_response.status_code, 201)
        wrong_submit_response = self.client.put(reverse('update_observation', kwargs={'pk': 1000}),
                                                self.observation_data, format='multipart')
        self.assertEqual(wrong_submit_response.status_code, 404)

    def test_user_observation_comment(self):
        """
        user observation comment
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        comment_response = self.client.post(reverse('observation_comment', kwargs={'pk': observation_id}),
                                            {'text': 'hello world comment testing!'}, format='json')
        self.assertEqual(comment_response.status_code, 201)

    def test_observation_comment_list(self):
        """
        observation comment list test
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        comment_response = self.client.get(reverse('observation_comment', kwargs={'pk': observation_id}), format='json')
        self.assertEqual(comment_response.status_code, 200)

    def test_user_observation_comment_without_observation_id(self):
        """
        test wrong observation id from frontend for user comment on observation.
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('observation_comment', kwargs={'pk': 100}),
                                    {'text': 'hello world comment testing!'},
                                    format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.get('detail'), 'Not found.')

    def test_user_observation_like(self):
        """
        User successful like to a observation
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('observation_like', kwargs={'pk': observation_id}), {'is_like': '1'},
                                    format='json')
        self.assertEqual(response.status_code, 200)

    def test_user_observation_like_on_invalid_data(self):
        """
         user like observation with invalid observation id
        """
        user_id = self.get_logged_in_user()
        response = self.client.post(reverse('observation_like', kwargs={'pk': 100}), {'is_like': '1'},
                                    format='json')
        self.assertEqual(response.data.get('detail'), 'Not found.')
        self.assertEqual(response.status_code, 404)

    def test_user_observation_dislike(self):
        """
        user observation dislike test
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('observation_like', kwargs={'pk': observation_id}), {'is_like': '0'},
                                    format='json')
        self.assertEqual(response.status_code, 200)

    def test_user_observation_watch_count(self):
        """
        user observation watch count test
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('observation_watch_count', kwargs={'pk': observation_id}), format='json')
        self.assertEqual(response.status_code, 200)

    def test_admin_user_observation_verification(self):
        """
        Admin user approving observation test
        """
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.save(update_fields=['is_superuser', 'is_staff'])
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('observation_approve_reject', kwargs={'pk': observation_id}),
                                    self.observation_approve_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('success'), 'Observation Approved.')

    def test_admin_user_observation_reject(self):
        """
        Admin user rejecting observation test
        """
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.save(update_fields=['is_superuser', 'is_staff'])
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('observation_approve_reject', kwargs={'pk': observation_id}),
                                    self.observation_reject_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('success'), 'Observation Rejected.')

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

    def test_home_view(self):
        """
        test home page api
        """
        response = self.client.get(reverse('home'), format='json')
        self.assertEqual(response.status_code, 200)

    def test_user_observation_collection(self):
        """
        test user observation collection api
        """
        user_id = self.get_logged_in_user()
        response = self.client.get(reverse('user_observation_collection'), formmat='json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"{reverse('user_observation_collection')}?type=verified&page=1", formmat='json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"{reverse('user_observation_collection')}?type=unverified&page=1", formmat='json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"{reverse('user_observation_collection')}?type=denied&page=1", formmat='json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"{reverse('user_observation_collection')}?type=draft&page=1", formmat='json')
        self.assertEqual(response.status_code, 200)

    def test_check_exists_observation_image(self):
        """
        test observation image check api
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('get_observation_details', kwargs={'pk': observation_id}), formmat='json')
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_observation_gallery(self):
        """
        test gallery api
        """
        user_id = self.get_logged_in_user()
        response = self.client.get(reverse('gallery'), formmat='json')
        self.assertEqual(response.status_code, 200)
        user_obj = User.objects.get(id=user_id)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.save(update_fields=['is_superuser', 'is_staff'])
        response = self.client.get(reverse('gallery'), formmat='json')
        self.assertEqual(response.status_code, 200)

    def test_observation_gallery_with_params(self):
        """
        test gallery api with query params
        """
        user_id = self.get_logged_in_user()
        response = self.client.get(f"{reverse('gallery')}?country=US&category=Sprite&status=unverified&page=1",
                                   formmat='json')
        self.assertEqual(response.status_code, 200)

    def test_normal_user_observation_dashboard_access(self):
        user_id = self.get_logged_in_user()
        response = self.client.get(reverse('dashboard'), formmat='json')
        self.assertEqual(response.data.get('detail'), 'You must be a admin user.')
        self.assertEqual(response.status_code, 403)

    def test_admin_user_observation_dashboard_access(self):
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.save(update_fields=['is_superuser', 'is_staff'])
        response = self.client.post(reverse('dashboard'), formmat='json')
        self.assertEqual(response.status_code, 200)

    def test_admin_user_observation_dashboard_access_with_query_params(self):
        """
        test dashboard api with query params
        """
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.save(update_fields=['is_superuser', 'is_staff'])
        response = self.client.post(f"{reverse('dashboard')}?country=US&category=Sprite&status=unverified&page=1",
                                    formmat='json')
        self.assertEqual(response.status_code, 200)

    def test_category_list(self):
        user_id = self.get_logged_in_user()
        response = self.client.get(reverse('get_category_list'), format='json')
        self.assertEqual(response.status_code, 200)

    def test_admin_user_observation_dashboard_with_payload(self):
        """
        test dashboard api with payload data
        """
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.save(update_fields=['is_superuser', 'is_staff'])
        payload = {'from_obs_data': '01/05/2022 22:09', 'to_obs_data': '02/05/2022 22:10',
                   'obs_start_date': '2022-05-01', 'obs_end_date': '2022-05-02', 'obs_start_time': '22:09',
                   'obs_end_time': '22:10', 'camera_type': 'Canon', 'fps': '50 FPS', 'iso': '100', 'fov': '11 mm',
                   'shutter_speed': '100', 'lens_type': 'Standard'}
        response = self.client.post(f"{reverse('dashboard')}?country=US&category=Sprite&status=unverified&page=1",
                                    data=payload, formmat='json')
        self.assertEqual(response.status_code, 200)

    def test_generate_observation_csv(self):
        """
        generate observation csv test
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        response = self.client.post(reverse('get_observation_csv'), {'observation_ids': [observation_id]}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_trained_user_observation_vote(self):
        """
        observation category vote by trained user test
        """
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_trained = True
        user_obj.save(update_fields=['is_trained'])
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        payload = {"votes": [{"category_id": 1, "vote": 1}]}
        response = self.client.post(reverse('observation_vote', kwargs={'pk': observation_id}), payload, format='json')
        self.assertEqual(response.status_code, 200)

    def test_admin_user_observation_vote(self):
        """
        observation category vote by admin user test
        """
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_superuser = True
        user_obj.is_staff = True
        user_obj.save(update_fields=['is_superuser', 'is_staff'])
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        payload = {"votes": [{"category_id": 1, "vote": 1}]}
        response = self.client.post(reverse('observation_vote', kwargs={'pk': observation_id}), payload, format='json')
        self.assertEqual(response.status_code, 200)

    def test_normal_user_observation_vote_restrictions(self):
        """
        test observation vote restricted to normal users
        """
        user_id = self.get_logged_in_user()
        self.client.post(reverse('upload_observation'), self.observation_data, format='multipart')
        observation_id = Observation.objects.filter().last().id
        payload = {"votes": [{"category_id": 1, "vote": 1}]}
        response = self.client.post(reverse('observation_vote', kwargs={'pk': observation_id}), payload, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get('detail'), 'You must be a trained or a admin user.')

    def test_trained_user_invalid_observation_vote(self):
        user_id = self.get_logged_in_user()
        user_obj = User.objects.get(id=user_id)
        user_obj.is_trained = True
        user_obj.save(update_fields=['is_trained'])
        payload = {"votes": [{"category_id": 1, "vote": 1}]}
        response = self.client.post(reverse('observation_vote', kwargs={'pk': 100}), payload, format='json')
        self.assertEqual(response.status_code, 404)
