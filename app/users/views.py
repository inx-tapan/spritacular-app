import constants

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import MyTokenObtainPairSerializer

from .models import User, CameraSetting
from .serializers import UserRegisterSerializer, ChangePasswordSerializer, CameraSettingSerializer
from .permissions import IsOwnerOrAdmin


class RootView(APIView):
    def get(self, request):
        return HttpResponse(constants.WELCOME, status=status.HTTP_200_OK)


class UserRegisterViewSet(viewsets.ModelViewSet):
    """
    User CRUD
    User registration and profile viewset.
    for profile data retrieve method will be called.
    for profile image upload or profile data update profile_update() will be called.
    """
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        permission_classes = []
        if self.action in [
            'retrieve',
            'patch',
            'profile_update',
            'put',
            'update_user_profile',
            'get_user_details',
        ]:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response('Already logged in')
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def retrieve(self, request, *args, **kwargs):
    #     user = get_object_or_404(User, pk=self.kwargs['pk'])
    #     self.check_object_permissions(request, user)
    #     serializer = self.serializer_class(user)
    #     return Response(serializer.data)

    def profile_update(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        return super(UserRegisterViewSet, self).partial_update(request=request, pk=pk)

    def update_user_profile(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer_obj = self.serializer_class(instance, data=request.data,
                                               context={'request': request, 'method': 'PUT'})
        serializer_obj.is_valid(raise_exception=True)
        # data = serializer_obj.update(instance, serializer_obj.validated_data)
        serializer_obj.save()
        return Response(serializer_obj.data, status=status.HTTP_200_OK)

    def get_user_details(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user).data
        is_check = False
        camera_obj = None
        camera = None

        try:
            camera_obj = CameraSetting.objects.get(user=user, is_profile_camera_settings=True)
            is_check = True
        except CameraSetting.DoesNotExist:
            camera = None
        except CameraSetting.MultipleObjectsReturned:
            camera_obj = CameraSetting.objects.filter(user=user, is_profile_camera_settings=True).last()
            is_check = True

        if is_check:
            camera = {
                'camera_type': camera_obj.camera_type,
                'iso': camera_obj.iso,
                'shutter_speed': camera_obj.shutter_speed,
                'fps': camera_obj.fps,
                'lens_type': camera_obj.lens_type,
                'focal_length': camera_obj.focal_length,
                'aperture': camera_obj.aperture,
                'question_field_one': camera_obj.question_field_one,
                'question_field_two': camera_obj.question_field_two
            }

        serializer['camera'] = camera
        serializer['is_superuser'] = request.user.is_superuser
        serializer['is_trained'] = request.user.is_trained
        serializer['is_user'] = not request.user.is_superuser and not request.user.is_trained
        return Response(serializer, status=status.HTTP_200_OK)


class CustomObtainTokenPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ChangePasswordViewSet(APIView):
    """
    Change password viewset for user.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def put(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        data = request.data
        data['user'] = user
        serializer = self.serializer_class(data=data, context={"user": user})
        if serializer.is_valid():
            # request.user.auth_token.delete()
            # logout(request)
            # ----- JWT
            # refresh_token = request.data["refresh_token"]
            # token = RefreshToken(refresh_token)
            # token.blacklist()
            return Response({"Success": True, "message": constants.CHANGE_PASS_SUCCESS}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CameraSettingsApiView(viewsets.ModelViewSet):
    """
    User profile camera setting CRUD.
    """
    serializer_class = CameraSettingSerializer
    permission_classes = [IsAuthenticated]
    queryset = CameraSetting.objects.all()
    http_method_names = ['get', 'post', 'patch']

    def get_object(self, pk=None):
        """
        Customizing get_object method.
        Adding is_profile_camera_settings filter in the query.
        :return: Authenticated user CameraSetting object if exists else 404.
        """
        try:
            return CameraSetting.objects.get(user_id=self.request.user.id, is_profile_camera_settings=True)
        except CameraSetting.DoesNotExist:
            raise Http404
        except CameraSetting.MultipleObjectsReturned:
            return CameraSetting.objects.filter(user_id=self.request.user.id, is_profile_camera_settings=True).last()


