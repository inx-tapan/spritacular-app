# from django.contrib.auth import login, logout
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from .serializers import MyTokenObtainPairSerializer

from .models import User, CameraSetting
from .serializers import UserRegisterSerializer, UserSerializer, ChangePasswordSerializer, CameraSettingSerializer
from .permissions import IsOwnerOrAdmin


class UserRegisterViewSet(viewsets.ModelViewSet):
    """
    User registration and profile viewset.
    for profile data retrieve method will be called.
    for profile image upload or profile data update profile_update() will be called.
    """
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        permission_classes = []
        if self.action == 'retrieve' or self.action == 'patch' or self.action == 'profile_update'\
                or self.action == 'put':
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

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        self.check_object_permissions(request, user)
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def profile_update(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        return super(UserRegisterViewSet, self).partial_update(request=request, pk=pk)


class CustomObtainTokenPairView(TokenObtainPairView):
    # permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class ChangePasswordViewSet(APIView):
    """
    Change password viewset for user.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        print(f"** {request.user.is_authenticated}")
        self.check_object_permissions(request, user)
        return Response(f'Change password for user: {user.first_name} {user.last_name}')

    def put(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        data = request.data
        data['user'] = user
        serializer = self.serializer_class(data=data, context={"user": user})
        print("------------")
        if serializer.is_valid():
            # request.user.auth_token.delete()
            # logout(request)
            # ----- JWT
            # refresh_token = request.data["refresh_token"]
            # token = RefreshToken(refresh_token)
            # token.blacklist()
            return Response({"Success": True, "message": "Password successfully changed."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO: Blackout refresh token once the user logout.
class LogoutViewSet(APIView):
    """
    Logout user viwset.
    refresh token will be blacklisted once the user opt to logout.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CameraSettingsApiView(viewsets.ModelViewSet):
    serializer_class = CameraSettingSerializer
    permission_classes = [IsAuthenticated]
    queryset = CameraSetting.objects.all()
    http_method_names = ['get', 'post', 'patch']

    def get_object(self, pk=None):
        print(f"--{self.action}")
        try:
            return CameraSetting.objects.get(user_id=self.request.user.id, is_profile_camera_settings=True)
        except CameraSetting.DoesNotExist:
            raise Http404

