from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from django.core.validators import FileExtensionValidator
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

from .models import User, CameraSetting


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=User.objects.all(),
        message='Account with this email already exists.',
        lookup="iexact"
    )], )
    profile_image = serializers.ImageField(required=False,
                                           validators=[FileExtensionValidator(['jpg', 'tiff', 'png', 'jpeg'])])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'location', 'profile_image')
        extra_kwargs = {'password': {'write_only': True}}


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        # data = super().validate(attrs)
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            self.user = User.objects.get(email__iexact=authenticate_kwargs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'No active account found with the given credentials.'},
                                              code=401)
        if not self.user.check_password(authenticate_kwargs["password"]):
            raise serializers.ValidationError({'detail': 'No active account found with the given credentials.'},
                                              code=401)

        data = {}
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['id'] = self.user.id
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['email'] = self.user.email

        self.user.last_login = timezone.now()
        self.user.save(update_fields=['last_login'])

        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=User.objects.all(),
        message='user with this email already exists.',
        lookup="iexact"
    )], )
    location = serializers.CharField(required=True)
    profile_image = serializers.ImageField(required=False,
                                           validators=[FileExtensionValidator(['jpg', 'tiff', 'png', 'jpeg'])])

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'location', 'profile_image')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(first_name=validated_data['first_name'], last_name=validated_data['last_name'],
                                   email=validated_data['email'], location=validated_data['location'],
                                   profile_image=validated_data.get('profile_image', ''))
        user.set_password(validated_data['password'])
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, validate_data):
        print(f"validate: {validate_data}")
        old_password = validate_data['old_password']
        new_password = validate_data['new_password']
        confirm_password = validate_data['confirm_password']
        user = self.context.get('user')

        user = authenticate(username=user.email, password=old_password)
        if user:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()

            else:
                raise serializers.ValidationError({'details': 'New password and confirm password does not match.'},
                                                  code=400)
        else:
            raise serializers.ValidationError({'details': 'Old password is incorrect.'}, code=400)

        return validate_data


class CameraSettingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CameraSetting
        fields = '__all__'

    def create(self, validated_data):
        camera_setting = CameraSetting.objects.create(**validated_data)
        if not validated_data.get('observation_settings'):
            # TODO: For differentiating camera settings in profile and settings used in observations upload form.
            camera_setting.is_profile_camera_settings = False
            camera_setting.save()

        return camera_setting
