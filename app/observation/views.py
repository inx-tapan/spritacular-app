import datetime
import json
import time

import pytz
from django.core.cache import cache
from django.db.models import Q, Prefetch, OuterRef, Exists, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (ObservationSerializer, ObservationCommentSerializer)
from rest_framework import status, viewsets
from users.serializers import CameraSettingSerializer
from users.permissions import IsAdminOrTrained, IsAdmin
from .models import (Observation, Category, ObservationComment, ObservationLike, ObservationWatchCount,
                     VerifyObservation, ObservationReasonForReject, ObservationImageMapping, ObservationCategoryMapping)
from constants import NOT_FOUND, OBS_FORM_SUCCESS, SOMETHING_WENT_WRONG
from rest_framework.pagination import PageNumberPagination
import pandas as pd


# class ImageMetadataViewSet(APIView):
#     serializer_class = ImageMetadataSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             response_data = serializer.get_exif_data(serializer.validated_data)
#             return Response(json.loads(json.dumps(str(response_data))), status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        data = []
        for tle in self.queryset:
            category_details = {
                'id': tle.pk,
                'name': tle.title
            }
            data.append(category_details)

        return Response(data, status=status.HTTP_200_OK)


class HomeViewSet(ListAPIView):
    serializer_class = ObservationSerializer

    def get(self, request, *args, **kwargs):
        # latest_observation = Observation.objects.filter(is_verified=True,
        #                                                 observationimagemapping__image__isnull=False,
        #                                                 observationimagemapping__compressed_image__isnull=False
        #                                                 ).order_by('-pk').distinct('pk')[:4]

        latest_observation = Observation.objects.filter(is_verified=True) \
                                 .exclude(Q(observationimagemapping__image=None) |
                                          Q(observationimagemapping__image='') |
                                          Q(observationimagemapping__compressed_image=None) |
                                          Q(observationimagemapping__compressed_image='')) \
                                 .order_by('-pk').distinct('id') \
                                 .prefetch_related('user', 'camera', 'observationimagemapping_set',
                                                   Prefetch('observationcategorymapping_set',
                                                            queryset=ObservationCategoryMapping.objects.prefetch_related(
                                                                'category'))
                                                   ,
                                                   Prefetch('observationlike_set',
                                                            queryset=ObservationLike.objects.all())
                                                   ,
                                                   Prefetch('observationwatchcount_set',
                                                            queryset=ObservationWatchCount.objects.all())
                                                   )[:4]

        observation_counts = Observation.objects.aggregate(
            self_count=Count('pk', distinct=True),
            country_count=Count('observationimagemapping__country_code', distinct=True),
            user_count=Count('user', distinct=True)
        )

        # observation_count = Observation.objects.filter().count()
        # observation_country_count = Observation.objects.distinct('observationimagemapping__country_code')
        # observation_user_count = Observation.objects.filter().distinct('user_id').count()

        serializer = self.serializer_class(latest_observation, many=True,
                                           context={'user_observation_collection': True, 'request': request})

        return Response({'data': {'latest_observation': serializer.data,
                                  'observation_count': observation_counts['self_count'],
                                  'observation_country_count': observation_counts['country_count'],
                                  'observation_user_count': observation_counts['user_count']}},
                        status=status.HTTP_200_OK)


class UploadObservationViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for observations
    """
    serializer_class = ObservationSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = json.loads(request.data['data'])

        for i in request.FILES:
            data['map_data'][int(i.split('_')[-1])]['image'] = request.FILES[i]

        camera_data = data.pop('camera')

        obs_context = {'request': request, 'observation_settings': True}
        if 'is_draft' in data:
            # Adding is_draft for eliminating validations check.
            obs_context['is_draft'] = True

        # if isinstance(camera_data, dict):
        camera_serializer = CameraSettingSerializer(data=camera_data, context=obs_context)

        obs_context['camera_data'] = camera_data

        observation_serializer = self.serializer_class(data=data, context=obs_context)
        if observation_serializer.is_valid(raise_exception=True) and camera_serializer.is_valid(
                raise_exception=True):
            observation_serializer.save()

            return Response(OBS_FORM_SUCCESS, status=status.HTTP_201_CREATED)

        return Response({'observation_errors': observation_serializer.errors,
                         'camera_errors': camera_serializer.errors, 'status': 0}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            obs_obj = Observation.objects.get(pk=kwargs.get('pk'), user=request.user, is_submit=False)
        except Observation.DoesNotExist:
            return Response(NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        data = json.loads(request.data['data'])

        for file in request.FILES:
            data['map_data'][int(file.split('_')[-1])]['image'] = request.FILES[file]

        camera_data = data.pop('camera')

        obs_context = {'request': request, 'observation_settings': True}
        if 'is_draft' in data:
            print("yes")
            # Adding is_draft for eliminating validations check.
            obs_context['is_draft'] = True

        camera_serializer = CameraSettingSerializer(instance=obs_obj.camera, data=camera_data, context=obs_context)
        observation_serializer = self.serializer_class(instance=obs_obj, data=data, context=obs_context)

        if observation_serializer.is_valid(raise_exception=True) and camera_serializer.is_valid(raise_exception=True):
            obs_obj = observation_serializer.save()
            camera_obj = camera_serializer.save()
            obs_obj.camera = camera_obj
            obs_obj.save()
            return Response(OBS_FORM_SUCCESS, status=status.HTTP_200_OK)

        return Response({'observation_errors': observation_serializer.errors,
                         'camera_errors': camera_serializer.errors, 'status': 0}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            obs_obj = Observation.objects.get(pk=kwargs.get('pk'), user=request.user, is_submit=False)
        except Observation.DoesNotExist:
            return Response(NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(obs_obj, context={'user_observation_collection': True, 'request': request})

        return Response({'data': serializer.data, 'status': 1}, status=status.HTTP_200_OK)

    def user_observation_collection(self, request, *args, **kwargs):
        data = request.query_params
        filters = Q(user=request.user)
        if data.get('type') == 'verified':
            filters = filters & Q(is_submit=True, is_verified=True)
        elif data.get('type') == 'unverified':
            filters = filters & Q(is_submit=True, is_verified=False)
        elif data.get('type') == 'denied':
            filters = filters & Q(is_submit=True, is_reject=True)
        elif data.get('type') == 'draft':
            filters = filters & Q(is_submit=False)

        verified_count = Observation.objects.filter(user=request.user, is_verified=True, is_submit=True).count()
        unverified_count = Observation.objects.filter(user=request.user, is_verified=False, is_submit=True).count()
        denied_count = Observation.objects.filter(user=request.user, is_reject=True, is_submit=True).count()
        draft_count = Observation.objects.filter(user=request.user, is_submit=False).count()

        # observation_filter = Observation.objects.filter(filters).order_by('-pk')

        is_like = ObservationLike.objects.filter(observation=OuterRef('pk'), user=request.user)
        is_watch = ObservationWatchCount.objects.filter(observation=OuterRef('pk'), user=request.user)
        is_voted = VerifyObservation.objects.filter(observation=OuterRef('pk'), user=request.user)
        observation_filter = Observation.objects.filter(filters). \
            exclude(Q(observationimagemapping__image=None) | Q(observationimagemapping__image='')) \
            .order_by('-pk').distinct('id') \
            .prefetch_related('user', 'camera', 'observationimagemapping_set',
                              Prefetch('observationcategorymapping_set',
                                       queryset=ObservationCategoryMapping.objects.prefetch_related('category'))
                              ,
                              Prefetch('observationlike_set',
                                       queryset=ObservationLike.objects.all())
                              ,
                              Prefetch('observationwatchcount_set',
                                       queryset=ObservationWatchCount.objects.all())
                              ).annotate(is_like=Exists(is_like),
                                         is_watch=Exists(is_watch),
                                         is_voted=Exists(is_voted)
                                         )

        page = self.paginate_queryset(observation_filter)
        if not page:
            serializer = self.serializer_class(observation_filter, many=True,
                                               context={'user_observation_collection': True, 'request': request})

            return Response({'results': {'data': serializer.data, 'verified_count': verified_count,
                                         'unverified_count': unverified_count, 'denied_count': denied_count,
                                         'draft_count': draft_count}}, status=status.HTTP_200_OK)
        else:
            serializer = self.serializer_class(page, many=True,
                                               context={'user_observation_collection': True, 'request': request})

            return self.get_paginated_response({'data': serializer.data, 'verified_count': verified_count,
                                                'unverified_count': unverified_count, 'denied_count': denied_count,
                                                'draft_count': draft_count})


class ObservationImageCheck(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            obs_obj = Observation.objects.get(pk=kwargs.get('pk'), user_id=request.user.id)
        except Observation.DoesNotExist:
            return Response(NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        image_data = []
        for im in ObservationImageMapping.objects.filter(observation=obs_obj).order_by('pk'):
            image_data.append(im.image.url if im.image else None)

        return Response({'data': image_data, 'status': 1}, status=status.HTTP_200_OK)


class ObservationCommentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for observation comments
    """
    serializer_class = ObservationCommentSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        observation = get_object_or_404(Observation, pk=kwargs.get('pk'))
        observation_comment_obj = ObservationComment.objects.filter(observation=observation)
        serializer = self.serializer_class(observation_comment_obj, many=True)
        return Response({'data': serializer.data, 'status': 1}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        get_object_or_404(Observation, pk=kwargs.get('pk'))
        data['observation'] = kwargs.get('pk')
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'data': serializer.data, 'status': 1}, status=status.HTTP_201_CREATED)

        return Response({'detail': serializer.errors, 'status': 0}, status=status.HTTP_400_BAD_REQUEST)


class ObservationLikeViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        get_object_or_404(Observation, pk=kwargs.get('pk'))
        data = request.data
        if data.get('is_like') == '1':
            if ObservationLike.objects.filter(observation_id=kwargs.get('pk'), user=request.user).exists():
                like_count = ObservationLike.objects.filter(observation_id=kwargs.get('pk')).count()
                return Response({'like_count': like_count, 'status': 0}, status=status.HTTP_400_BAD_REQUEST)

            ObservationLike.objects.create(observation_id=kwargs.get('pk'), user=request.user)
            like_status = True
        else:
            # Observation Dislike
            ObservationLike.objects.filter(observation_id=kwargs.get('pk'), user=request.user).delete()
            like_status = False

        like_count = ObservationLike.objects.filter(observation_id=kwargs.get('pk')).count()
        return Response({'like_count': like_count, 'status': 1, 'like': like_status}, status=status.HTTP_200_OK)


class ObservationWatchCountViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        get_object_or_404(Observation, pk=kwargs.get('pk'))
        if not ObservationWatchCount.objects.filter(observation_id=kwargs.get('pk'), user=request.user).exists():
            ObservationWatchCount.objects.create(observation_id=kwargs.get('pk'), user=request.user)

        watch_count = ObservationWatchCount.objects.filter(observation_id=kwargs.get('pk')).count()

        return Response({'watch_count': watch_count, 'status': 1}, status=status.HTTP_200_OK)


class ObservationGalleryViewSet(ListAPIView):
    """
    Observation gallery page api with paginated response.
    """
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Observation.objects.all() \
            .exclude(Q(observationimagemapping__image=None) | Q(observationimagemapping__image='')) \
            .order_by('-pk').distinct('id') \
            .prefetch_related('user', 'camera', 'observationimagemapping_set',
                              Prefetch('observationcategorymapping_set',
                                       queryset=ObservationCategoryMapping.objects.prefetch_related('category'))
                              ,
                              Prefetch('observationlike_set',
                                       queryset=ObservationLike.objects.all())
                              ,
                              Prefetch('observationwatchcount_set',
                                       queryset=ObservationWatchCount.objects.all())
                              )

    def get(self, request, *args, **kwargs):
        data = request.query_params

        # Storing gallery filters
        filters = Q(is_submit=True, is_reject=False)
        if data.get('country'):
            filters = filters & Q(observationimagemapping__country_code__iexact=data.get('country'))
        if data.get('category'):
            filters = filters & Q(observationcategorymapping__category__title__iexact=data.get('category'))
        if data.get('status') == 'verified':
            filters = filters & Q(is_verified=True)
        if data.get('status') == 'unverified':
            filters = filters & Q(is_verified=False)

        if request.user.is_authenticated and (request.user.is_trained or request.user.is_superuser):
            # Trained user can see both verified and unverified observation on gallery screen.
            is_like = ObservationLike.objects.filter(observation=OuterRef('pk'), user=request.user)
            is_watch = ObservationWatchCount.objects.filter(observation=OuterRef('pk'), user=request.user)
            is_voted = VerifyObservation.objects.filter(observation=OuterRef('pk'), user=request.user)

            observation_filter = self.get_queryset().filter(filters).annotate(is_like=Exists(is_like),
                                                                              is_watch=Exists(is_watch),
                                                                              is_voted=Exists(is_voted)
                                                                              )

        elif request.user.is_authenticated:
            # For normal users
            is_like = ObservationLike.objects.filter(observation=OuterRef('pk'), user=request.user)
            is_watch = ObservationWatchCount.objects.filter(observation=OuterRef('pk'), user=request.user)
            is_voted = VerifyObservation.objects.filter(observation=OuterRef('pk'), user=request.user)

            observation_filter = self.get_queryset().filter(is_submit=True, is_verified=True).annotate(
                is_like=Exists(is_like),
                is_watch=Exists(is_watch),
                is_voted=Exists(is_voted)
            )

        else:
            # For unauthenticated users
            observation_filter = self.get_queryset().filter(is_submit=True, is_verified=True)

        page = self.paginate_queryset(observation_filter)
        if not page:
            serializer = ObservationSerializer(observation_filter, many=True,
                                               context={'user_observation_collection': True, 'request': request})
            return Response({'results': {'data': serializer.data, 'status': 1}}, status=status.HTTP_200_OK)

        else:
            serializer = ObservationSerializer(page, many=True, context={'user_observation_collection': True,
                                                                         'request': request})
            return self.get_paginated_response({'data': serializer.data})


class ObservationVoteViewSet(APIView):
    """
    Observation vote api.
    Allowed for admin and trained users.
    """
    permission_classes = (IsAuthenticated, IsAdminOrTrained)

    def post(self, request, *args, **kwargs):
        observation_id = kwargs.get('pk')
        data = request.data
        try:
            observation_obj = Observation.objects.get(id=observation_id)
        except Observation.DoesNotExist:
            return Response(NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        is_status_change = False
        for user_vote in data.get('votes'):
            verify_obs_obj = VerifyObservation.objects.create(observation_id=observation_id, user=request.user,
                                                              category_id=user_vote.get("category_id"),
                                                              vote=user_vote.get("vote"))

            if verify_obs_obj.user.is_superuser and verify_obs_obj.vote:
                # If an admin votes yes on any category of the observation it will send for verification.
                is_status_change = True

            if VerifyObservation.objects.filter(observation_id=observation_id,
                                                category_id=user_vote.get("category_id"), vote=True).count() > 3:
                # If any category of the observation have more than 3 yes votes it will send for verification.
                is_status_change = True

        if is_status_change:
            print("status change")
            # Set is_to_be_verify flag to True.
            observation_obj.is_to_be_verify = True
            observation_obj.save(update_fields=['is_to_be_verify'])

        return Response({'success': 'Successfully Voted.', 'status': 1}, status=status.HTTP_200_OK)


class ObservationVerifyViewSet(APIView):
    """
    observation approve and reject api.
    Allowed to admin users only.
    """
    permission_classes = (IsAuthenticated, IsAdmin)

    def post(self, request, *args, **kwargs):
        observation_id = kwargs.get('pk')
        data = request.data
        try:
            observation_obj = Observation.objects.get(id=observation_id)
        except Observation.DoesNotExist:
            return Response(SOMETHING_WENT_WRONG, status=status.HTTP_400_BAD_REQUEST)

        if data.get('name') == "APPROVE":
            # Approved
            observation_obj.is_verified = True
            observation_obj.is_reject = False
            observation_obj.save(update_fields=['is_verified', 'is_reject'])

            return Response({'success': 'Observation Approved.'}, status=status.HTTP_200_OK)

        elif data.get('name') == "REJECT":
            # Reject
            observation_obj.is_reject = True
            observation_obj.is_verified = False
            observation_obj.save(update_fields=['is_reject', 'is_verified'])

            if data.get('reason'):
                reason_data = data.get('reason')
                # Reason for reject
                ObservationReasonForReject.objects.create(observation_id=observation_id,
                                                          inappropriate_image=reason_data.get('inappropriate_image'),
                                                          other=reason_data.get('other'),
                                                          additional_comment=reason_data.get('additional_comment',
                                                                                             None))

            return Response({'success': 'Observation Rejected.'}, status=status.HTTP_200_OK)

        return Response(SOMETHING_WENT_WRONG, status=status.HTTP_400_BAD_REQUEST)


class ObservationDashboardViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = ObservationSerializer
    pagination_class = PageNumberPagination
    queryset = Observation.objects.all()

    def create(self, request, *args, **kwargs):
        # cache.delete('common_observation_cache_data')
        query_data = request.query_params
        data = request.data

        filters = Q(is_submit=True)
        if data.get('from_obs_data'):
            date_time_obj = pytz.utc.localize(datetime.datetime.strptime(data.get('from_obs_data'), "%d/%m/%Y %H:%M"))
            filters = filters & Q(observationimagemapping__obs_date_time_as_per_utc__gte=date_time_obj)
        if data.get('to_obs_data'):
            date_time_obj = pytz.utc.localize(datetime.datetime.strptime(data.get('to_obs_data'), "%d/%m/%Y %H:%M"))
            filters = filters & Q(observationimagemapping__obs_date_time_as_per_utc__lte=date_time_obj)
        if query_data.get('country'):
            filters = filters & Q(observationimagemapping__country_code__iexact=query_data.get('country'))
        if query_data.get('status') == 'verified':
            filters = filters & Q(is_verified=True)
        if query_data.get('status') == 'unverified':
            filters = filters & Q(is_verified=False)
        if query_data.get('category'):
            filters = filters & Q(observationcategorymapping__category__title__iexact=query_data.get('category'))
        if data.get('camera_type'):
            filters = filters & Q(camera__camera_type__iexact=data.get('camera_type'))
        if data.get('fps'):
            filters = filters & Q(camera__fps__iexact=data.get('fps'))
        if data.get('iso'):
            filters = filters & Q(camera__iso__iexact=data.get('iso'))
        # if data.get('fov'):
        #     filters = filters & Q()
        if data.get('shutter_speed'):
            filters = filters & Q(camera__shutter_speed__iexact=data.get('shutter_speed'))

        # get all required ids all api calls
        required_observation_ids = set(Observation.objects.filter(filters).only('id').exclude(
            Q(observationimagemapping__image=None) | Q(observationimagemapping__image='')
        ).values_list('id', flat=True))

        # observation_cache_common = []
        cache_obs_dict = cache.get('common_observation_cache_data')
        diff_ids = set()

        if cache_obs_dict:
            print("yes")
            start_time = time.time()
            diff_ids = required_observation_ids - set(cache_obs_dict)
            print(f"difference length++{len(diff_ids)}")
            print(f"one:{time.time()-start_time}")
            # Using list comprehension instead of set
            start_time = time.time()
            # observation_cache_common = [
            #     cache_obs_dict[i] for i in required_observation_ids if i in cache.get('common_observation_cache_data')]
            # Alternative test for observation_cache_common
            observation_cache_common = [
                cache_obs_dict.get(i) for i in required_observation_ids.intersection(set(cache_obs_dict))]
            print(f"two:{time.time()-start_time}")

        if cache_obs_dict and not diff_ids:
            print("ALL FROM CACHE")
            observation_filter = observation_cache_common

        else:
            start_time = time.time()
            required_obs_ids = diff_ids if cache_obs_dict else required_observation_ids

            is_like = ObservationLike.objects.filter(observation=OuterRef('pk'), user=request.user).only('id')
            is_watch = ObservationWatchCount.objects.filter(observation=OuterRef('pk'), user=request.user).only('id')
            is_voted = VerifyObservation.objects.filter(observation=OuterRef('pk'), user=request.user).only('id')

            observation_filter = list(Observation.objects.filter(id__in=required_obs_ids)
                                      .exclude(
                Q(observationimagemapping__image=None) |
                Q(observationimagemapping__image='')
            ).order_by('-pk').distinct('id')
                                      .prefetch_related('user', 'camera', 'observationimagemapping_set',
                                                        Prefetch('observationcategorymapping_set',
                                                                 queryset=ObservationCategoryMapping.objects.prefetch_related(
                                                                     'category'))
                                                        ,
                                                        Prefetch('observationlike_set',
                                                                 queryset=ObservationLike.objects.all())
                                                        ,
                                                        Prefetch('observationwatchcount_set',
                                                                 queryset=ObservationWatchCount.objects.all())
                                                        ).annotate(is_like=Exists(is_like),
                                                                   is_watch=Exists(is_watch),
                                                                   is_voted=Exists(is_voted)
                                                                   ))

            print(f"Original list length->{len(observation_filter)}")
            print(f"three:{time.time() - start_time}")

            start_time = time.time()
            if not cache_obs_dict:
                print("cache set")
                cache.set('common_observation_cache_data', {})

            cache_obs_dict = cache.get('common_observation_cache_data')

            for obs_obj in observation_filter:
                cache_obs_dict[obs_obj.id] = obs_obj

            cache.set('common_observation_cache_data', cache_obs_dict)
            print(f"four:{time.time() - start_time}")

            observation_filter += observation_cache_common

            # obs_cache_data = {obs_obj.id: obs_obj for obs_obj in observation_filter}
            # for i in observation_cache_common:
            #     observation_filter.append(cache.get('common_observation_cache_data')[i])
            #     obs_cache_data[i] = cache.get('common_observation_cache_data')[i]

        print(f"{len(observation_filter)}--{len(set(observation_filter))}")

        # if len(observation_filter) == len(set(observation_filter)):
        #     # Set cache only if the queryset full of unique instances
        #     print("**cache it**")
        #     cache.set('common_observation_cache_data', obs_cache_data)

        start_time = time.time()
        page = self.paginate_queryset(observation_filter)
        if not page:
            serializer = self.serializer_class(observation_filter, many=True,
                                               context={'user_observation_collection': True, 'request': request})
            return Response({'results': {'data': serializer.data, 'status': 1}}, status=status.HTTP_200_OK)

        else:
            serializer = self.serializer_class(page, many=True, context={'user_observation_collection': True,
                                                                         'request': request})
            sd = serializer.data
            print(f"five:{time.time() - start_time}")
            return self.get_paginated_response({'data': sd})


class GenerateObservationCSVViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        observation_list = request.data.get('observation_ids', [])
        observation_filter = Observation.objects.filter(id__in=observation_list)

        # fields for dataframe
        q = observation_filter.values('id',
                                      'user__first_name',
                                      'user__last_name',
                                      'observationimagemapping__country_code',
                                      'observationimagemapping__location',
                                      'observationimagemapping__latitude',
                                      'observationimagemapping__longitude',
                                      'observationimagemapping__obs_date_time_as_per_utc',
                                      'observationimagemapping__time_accuracy',
                                      'observationimagemapping__is_precise_azimuth',
                                      'observationimagemapping__azimuth',
                                      'observationimagemapping__timezone',
                                      'is_submit',
                                      'is_verified',
                                      'is_reject').distinct('id')

        # converting queryset into dataframe
        df = pd.DataFrame.from_records(q)

        # renaming column for csv file
        df.columns = ['id', 'first_name', 'last_name', 'country_code',
                      'location', 'latitude', 'longitude', 'obs_date_time_as_per_utc',
                      'time_accuracy', 'is_precise_azimuth', 'azimuth', 'timezone', 'is_submit', 'is_verified',
                      'is_reject']

        # csv file generation
        response = HttpResponse(content_type='text/csv', status=status.HTTP_200_OK)
        response['Content-Disposition'] = 'attachment; filename=observation_data.csv'
        df.to_csv(path_or_buf=response, index=False)

        return response
