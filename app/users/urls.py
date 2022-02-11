from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from .views import UserRegisterViewSet, ChangePasswordViewSet, LogoutViewSet
# from rest_framework import routers
# router = routers.DefaultRouter()
# router.register('register', UserRegisterViewSet, basename='register')
# urlpatterns = router.urls

urlpatterns = [
    # Login
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # SignUp
    path('register/', UserRegisterViewSet.as_view({'post': 'create'})),
    # User profile image upload or profile update
    path('user_profile/<int:pk>', UserRegisterViewSet.as_view({'patch': 'profile_update', 'get': 'retrieve'}),
         name='profile_retrieve_update'),
    # Change Password
    path('change-password/', ChangePasswordViewSet.as_view(), name='change-password'),
    # Password reset
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # Logout
    path('logout/', LogoutViewSet.as_view(), name='logout'),
]
