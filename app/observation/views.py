import json

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ImageMetadataSerializer
from rest_framework import viewsets, status


class ImageMetadataViewSet(APIView):
    serializer_class = ImageMetadataSerializer
    # permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response_data = serializer.get_exif_data(serializer.validated_data)
            # print(type(json.loads(str(response_data))))
            # {'ImageWidth': response_data['ImageWidth'], 'ImageLength': response_data['ImageLength'], 'GPSInfo': response_data['GPSInfo']}
            return Response(json.loads(json.dumps(str(response_data))), status=status.HTTP_200_OK)
            # return Response(json.dumps(response_data), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

