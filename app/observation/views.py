import json

from django.db.models import Q
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CameraSetting
from .serializers import ImageMetadataSerializer, ObservationSerializer, ObservationCategorySerializer
from rest_framework import status, viewsets
from users.serializers import CameraSettingSerializer
from .models import Observation, Category


class ImageMetadataViewSet(APIView):
    serializer_class = ImageMetadataSerializer
    # permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response_data = serializer.get_exif_data(serializer.validated_data)
            # print(type(json.loads(str(response_data))))
            # return Response({'success': True}, status=status.HTTP_200_OK)
            return Response(json.loads(json.dumps(str(response_data))), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
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
    serializer_class = ObservationSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = json.loads(request.data['data'])

        for i in request.FILES:
            data['map_data'][int(i.split('_')[-1])]['image'] = request.FILES[i]

        camera_data = data.pop('camera')

        obs_context = {'request': request, 'observation_settings': True}
        if 'is_draft' in data:
            obs_context['is_draft'] = True

        if isinstance(camera_data, dict):
            camera_serializer = CameraSettingSerializer(data=camera_data, context=obs_context)

            obs_context['camera_data'] = camera_data

            observation_serializer = self.serializer_class(data=data, context=obs_context)
            if observation_serializer.is_valid(raise_exception=True) and camera_serializer.is_valid(
                    raise_exception=True):
                observation_serializer.save()

                return Response({'success': 'Form submitted successfully.'}, status=status.HTTP_201_CREATED)

        return Response({'observation_errors': observation_serializer.errors,
                         'camera_errors': camera_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            obs_obj = Observation.objects.get(pk=kwargs.get('pk'), is_submit=False)
        except Observation.DoesNotExist:
            return Http404

        data = json.loads(request.data['data'])

        for i in request.FILES:
            data['map_data'][int(i.split('_')[-1])]['image'] = request.FILES[i]

        camera_data = data.pop('camera')

        obs_context = {'request': request, 'observation_settings': True}
        if 'is_draft' in data:
            obs_context['is_draft'] = True

        camera_flag = isinstance(data.get('camera'), dict)

        # if obs_obj.camera is None and isinstance(camera_data, dict):
        #     camera_serializer = CameraSettingSerializer(data=data['camera'],
        #                                                 context={'request': request, 'observation_settings': True})

        if (obs_obj.camera and obs_obj.camera.is_profile_camera_settings) and isinstance(camera_data, dict):
            camera_serializer = CameraSettingSerializer(data=camera_data, context=obs_context)

        elif (obs_obj.camera and not obs_obj.camera.is_profile_camera_settings) and isinstance(camera_data, dict):
            camera_serializer = CameraSettingSerializer(instance=obs_obj.camera, data=camera_data,
                                                        context=obs_context)

        elif (obs_obj.camera and not obs_obj.camera.is_profile_camera_settings) and isinstance(camera_data, int):
            # Delete the old camera setting instance.
            try:
                CameraSetting.objects.get(id=obs_obj.camera_id).delete()
            except CameraSetting.DoesNotExist:
                pass

        observation_serializer = self.serializer_class(instance=obs_obj, data=data, context=obs_context)

        if observation_serializer.is_valid(raise_exception=True):
            if not camera_flag:
                camera_serializer.is_valid(raise_exception=True)
                obs_obj = observation_serializer.save()
                camera_obj = camera_serializer.save()
                obs_obj.camera = camera_obj
            else:
                obs_obj = observation_serializer.save()
                obs_obj.camera = camera_data
            obs_obj.save()

            return Response({"success": True}, status=status.HTTP_200_OK)

        return Response({'observation_errors': observation_serializer.errors,
                         'camera_errors': camera_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def user_observation_collection(self, request, *args, **kwargs):
        observation_type = request.GET.get('observation_type')
        # sort_by = request.GET.get('sort_by', 'recent')

        verified_count = Observation.objects.filter(user=request.user, is_verified=True).count()
        unverified_count = Observation.objects.filter(user=request.user, is_verified=False, is_submit=True).count()
        denied_count = Observation.objects.filter(user=request.user, is_reject=True, is_submit=True).count()
        draft_count = Observation.objects.filter(user=request.user, is_submit=False).count()

        filters = Q(user=request.user)
        if observation_type == 'verified':
            filters = filters & Q(is_verified=True)
        elif observation_type == 'unverified':
            filters = filters & Q(is_verified=False, is_submit=True)
        elif observation_type == 'denied':
            filters = filters & Q(is_reject=True, is_submit=True)
        elif observation_type == 'draft':
            filters = filters & Q(is_submit=False)

        observation = Observation.objects.filter(filters)
        serializer = ObservationSerializer(observation, many=True, context={'user_observation_collection': True})

        return Response({'data': serializer.data, 'verified_count': verified_count,
                         'unverified_count': unverified_count, 'denied_count': denied_count,
                         'draft_count': draft_count}, status=status.HTTP_200_OK)

    def get_draft_data(self, request, *args, **kwargs):
        try:
            obs_obj = Observation.objects.get(pk=kwargs.get('pk'), is_submit=False)
        except Observation.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ObservationSerializer(obs_obj, context={'user_observation_collection': True})

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


