import json

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ImageMetadataSerializer, ObservationSerializer
from rest_framework import status, viewsets
from users.serializers import CameraSettingSerializer


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

        print(f"DD {data}")
        if isinstance(data['camera'], dict):
            camera_serializer = CameraSettingSerializer(data=data['camera'], context={'request': request})
            camera_serializer.is_valid(raise_exception=True)
            camera_id = camera_serializer.create(camera_serializer.validated_data)
            data['camera'] = camera_id.id

        observation_serializer = self.serializer_class(data=data, context={'request': request})
        if observation_serializer.is_valid(raise_exception=True):
            obs_id = observation_serializer.save()
            return Response({'id': obs_id.id}, status=status.HTTP_200_OK)

        return Response(observation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



