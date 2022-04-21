import datetime
import json

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (ImageMetadataSerializer, ObservationSerializer, ObservationCommentSerializer)
from rest_framework import status, viewsets
from users.serializers import CameraSettingSerializer
from users.permissions import IsAdminOrTrained, IsAdmin
from .models import (Observation, Category, ObservationComment, ObservationLike, ObservationWatchCount,
                     VerifyObservation, ObservationReasonForReject)
from constants import NOT_FOUND, OBS_FORM_SUCCESS, SOMETHING_WENT_WRONG
from rest_framework.pagination import PageNumberPagination


class ImageMetadataViewSet(APIView):
    serializer_class = ImageMetadataSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response_data = serializer.get_exif_data(serializer.validated_data)
            return Response(json.loads(json.dumps(str(response_data))), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        data = []
        for i in self.queryset:
            category_details = {
                'id': i.pk,
                'name': i.title
            }
            data.append(category_details)

        return Response(data, status=status.HTTP_200_OK)


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

        # else:
        #     obs_context['camera_data'] = camera_data
        #     observation_serializer = self.serializer_class(data=data, context=obs_context)
        #     if observation_serializer.is_valid(raise_exception=True):
        #         observation_serializer.save()
        #
        #     return Response(OBS_FORM_SUCCESS, status=status.HTTP_201_CREATED)

        return Response({'observation_errors': observation_serializer.errors,
                         'camera_errors': camera_serializer.errors, 'status': 0}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            obs_obj = Observation.objects.get(pk=kwargs.get('pk'), user=request.user, is_submit=False)
        except Observation.DoesNotExist:
            return Response(NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        data = json.loads(request.data['data'])

        for i in request.FILES:
            data['map_data'][int(i.split('_')[-1])]['image'] = request.FILES[i]

        camera_data = data.pop('camera')

        obs_context = {'request': request, 'observation_settings': True}
        if 'is_draft' in data:
            print("yes")
            # Adding is_draft for eliminating validations check.
            obs_context['is_draft'] = True

        # camera_flag = isinstance(camera_data, dict)

        # if (obs_obj.camera and obs_obj.camera.is_profile_camera_settings) and camera_flag:
        #     # if the profile camera setting toggle is off.
        #     camera_serializer = CameraSettingSerializer(data=camera_data, context=obs_context)
        #
        # elif (obs_obj.camera and not obs_obj.camera.is_profile_camera_settings) and camera_flag:
        #     # if the profile camera setting toggle is off and previous object is not profile setting.
        #     camera_serializer = CameraSettingSerializer(instance=obs_obj.camera, data=camera_data,
        #                                                 context=obs_context)
        #
        # elif (obs_obj.camera and not obs_obj.camera.is_profile_camera_settings) and isinstance(camera_data, int):
        #     # Delete the old camera setting instance.
        #     try:
        #         CameraSetting.objects.get(id=obs_obj.camera_id).delete()
        #     except CameraSetting.DoesNotExist:
        #         pass

        camera_serializer = CameraSettingSerializer(instance=obs_obj.camera, data=camera_data, context=obs_context)

        observation_serializer = self.serializer_class(instance=obs_obj, data=data, context=obs_context)

        # if observation_serializer.is_valid(raise_exception=True):
        #     if camera_flag:
        #         camera_serializer.is_valid(raise_exception=True)
        #         obs_obj = observation_serializer.save()
        #         camera_obj = camera_serializer.save()
        #         obs_obj.camera = camera_obj
        #     else:
        #         obs_obj = observation_serializer.save()
        #         obs_obj.camera = camera_data
        #     obs_obj.save()
        #
        #     return Response(OBS_FORM_SUCCESS, status=status.HTTP_200_OK)

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

        observation_filter = Observation.objects.filter(filters).order_by('-pk')
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
        data['observation'] = kwargs.get('pk')
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'data': serializer.data, 'status': 1}, status=status.HTTP_200_OK)

        return Response({'data': serializer.data, 'status': 1}, status=status.HTTP_200_OK)


class ObservationLikeViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
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
        if not ObservationWatchCount.objects.filter(observation_id=kwargs.get('pk'), user=request.user).exists():
            ObservationWatchCount.objects.create(observation_id=kwargs.get('pk'), user=request.user)

        watch_count = ObservationWatchCount.objects.filter(observation_id=kwargs.get('pk')).count()

        return Response({'watch_count': watch_count, 'status': 1}, status=status.HTTP_200_OK)


class ObservationGalleryViewSet(ListAPIView):
    """
    Observation gallery page api with paginated response.
    """
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        data = request.query_params

        # Storing gallery filters
        filters = Q(is_submit=True, is_reject=False, observationimagemapping__image__isnull=False)
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
            observation_filter = Observation.objects.filter(filters).order_by('-pk').distinct('id')
        else:
            # Unauthenticated and untrained user can see only verified observations.
            observation_filter = Observation.objects.filter(is_submit=True,
                                                            is_verified=True).order_by('-pk').distinct('id')

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
        user = request.user
        data = request.data
        try:
            observation_obj = Observation.objects.get(id=observation_id)
        except Observation.DoesNotExist:
            return Response(SOMETHING_WENT_WRONG, status=status.HTTP_400_BAD_REQUEST)

        is_status_change = False
        for i in data.get('votes'):
            verify_obs_obj = VerifyObservation.objects.create(observation_id=observation_id, user=user,
                                                              category_id=i.get("category_id"), vote=i.get("vote"))

            if verify_obs_obj.user.is_superuser and verify_obs_obj.vote:
                # If an admin votes yes on any category of the observation it will send for verification.
                is_status_change = True

            if VerifyObservation.objects.filter(observation_id=observation_id,
                                                category_id=i.get("category_id"), vote=True).count() > 3:
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
                                                          additional_comment=reason_data.get('additional_comment', None))

            return Response({'success': 'Observation Rejected.'}, status=status.HTTP_200_OK)

        return Response(SOMETHING_WENT_WRONG, status=status.HTTP_400_BAD_REQUEST)


class ObservationDashboardViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = ObservationSerializer
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        query_data = request.query_params
        data = request.data

        filters = Q(is_submit=True, observationimagemapping__image__isnull=False)
        if query_data.get('country'):
            filters = filters & Q(observationimagemapping__country_code__iexact=query_data.get('country'))
        if query_data.get('category'):
            filters = filters & Q(observationcategorymapping__category__title__iexact=query_data.get('category'))
        if query_data.get('status') == 'verified':
            filters = filters & Q(is_verified=True)
        if query_data.get('status') == 'unverified':
            filters = filters & Q(is_verified=False)
        if data.get('from_obs_data'):
            date_time_obj = datetime.datetime.strptime(data.get('from_obs_data'), "%d/%m/%Y %H:%M")
            filters = filters & Q(observationimagemapping__obs_date_time_as_per_utc__gte=date_time_obj)
        if data.get('to_obs_data'):
            date_time_obj = datetime.datetime.strptime(data.get('to_obs_data'), "%d/%m/%Y %H:%M")
            filters = filters & Q(observationimagemapping__obs_date_time_as_per_utc__lte=date_time_obj)
        if data.get('camera_type'):
            filters = filters & Q(camera__camera_type__iexact=data.get('camera_type'))
        if data.get('fps'):
            filters = filters & Q(camera__fps__iexact=data.get('fps'))
        if data.get('iso'):
            filters = filters & Q(camera__iso__iexact=data.get('iso'))
        if data.get('fov'):
            filters = filters & Q()
        if data.get('shutter_speed'):
            filters = filters & Q(camera__shutter_speed__iexact=data.get('shutter_speed'))

        observation_filter = Observation.objects.filter(filters).order_by('-pk').distinct('id')

        page = self.paginate_queryset(observation_filter)
        if not page:
            serializer = self.serializer_class(observation_filter, many=True,
                                               context={'user_observation_collection': True, 'request': request})
            return Response({'results': {'data': serializer.data, 'status': 1}}, status=status.HTTP_200_OK)

        else:
            serializer = self.serializer_class(page, many=True, context={'user_observation_collection': True,
                                                                         'request': request})
            return self.get_paginated_response({'data': serializer.data})


