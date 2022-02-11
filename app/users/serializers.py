from django.contrib.auth import authenticate
from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from rest_framework.validators import UniqueValidator

from .models import User


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


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=User.objects.all(),
        message='user with this email already exists.',
        lookup="iexact"
    )],)
    profile_image = serializers.ImageField(required=False,
                                           validators=[FileExtensionValidator(['jpg', 'tiff', 'png', 'jpeg'])])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'location', 'profile_image')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print("inside create call")
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

