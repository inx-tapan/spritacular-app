import json

from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ImageMetadataSerializer, ObservationSerializer
from rest_framework import status, viewsets
from users.serializers import CameraSettingSerializer
from .models import Observation


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


class UploadObservationViewSet(viewsets.ModelViewSet):
    serializer_class = ObservationSerializer
    # permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # data = request.data
        data = json.loads(request.data['data'])

        for i in request.FILES:
            data['map_data'][int(i.split('_')[-1])]['image'] = request.FILES[i]

        print(f"DATA {data}")
        # if isinstance(data.get('camera'), dict):
        #     camera_serializer = CameraSettingSerializer(data=data['camera'],
        #                                                 context={'request': request, 'observation_settings': True})
        #     camera_serializer.is_valid(raise_exception=True)
        #     camera_id = camera_serializer.create(camera_serializer.validated_data)
        #     data['camera'] = camera_id.id
        camera_data = data.pop('camera')
        obs_context = {'request': request}
        if 'is_draft' in data:
            obs_context['is_draft'] = True
        observation_serializer = self.serializer_class(data=data, context=obs_context)
        if observation_serializer.is_valid(raise_exception=True):
            obs_id = observation_serializer.save()
            return Response({'id': obs_id.id}, status=status.HTTP_201_CREATED)

        return Response(observation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        obs_obj = get_object_or_404(Observation, pk=kwargs.get('pk'))
        data = json.loads(request.data['data'])

        for i in request.FILES:
            data['map_data'][int(i.split('_')[-1])]['image'] = request.FILES[i]

        if obs_obj.camera is None and isinstance(data.get('camera'), dict):
            camera_serializer = CameraSettingSerializer(data=data['camera'],
                                                        context={'request': request, 'observation_settings': True})
            camera_serializer.is_valid(raise_exception=True)
            camera_id = camera_serializer.create(camera_serializer.validated_data)
            data['camera'] = camera_id.id

        elif (obs_obj.camera and obs_obj.camera.is_profile_camera_settings) and isinstance(data.get('camera'), dict):
            camera_serializer = CameraSettingSerializer(data=data['camera'],
                                                        context={'request': request, 'observation_settings': True})
            camera_serializer.is_valid(raise_exception=True)
            camera_id = camera_serializer.create(camera_serializer.validated_data)
            data['camera'] = camera_id.id

        elif (obs_obj.camera and not obs_obj.camera.is_profile_camera_settings) and isinstance(data.get('camera'), dict):
            camera_serializer = CameraSettingSerializer(instance=obs_obj.camera, data=data['camera'],
                                                        context={'request': request, 'observation_settings': True})
            camera_serializer.is_valid(raise_exception=True)
            camera_serializer.save()

        elif (obs_obj.camera and not obs_obj.camera.is_profile_camera_settings) and isinstance(data.get('camera'), int):
            # Delete the old camera setting instance.
            pass

        obs_context = {'request': request}
        if 'is_draft' in data:
            obs_context['is_draft'] = True
        observation_serializer = self.serializer_class(instance=obs_obj, data=data, context=obs_context)
        if observation_serializer.is_valid(raise_exception=True):
            observation_serializer.save()
            return Response({"success": True}, status=status.HTTP_200_OK)

        return Response(observation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



