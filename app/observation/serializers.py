import uuid

from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from .utils import dms_coordinates_to_dd_coordinates
from .models import (ObservationImageMapping, Observation, Category, ObservationCategoryMapping, ObservationComment,
                     ObservationLike, ObservationWatchCount, VerifyObservation)
from users.models import CameraSetting
from users.serializers import UserRegisterSerializer, CameraSettingSerializer
from constants import FIELD_REQUIRED, SINGLE_IMAGE_VALID, MULTIPLE_IMAGE_VALID
from observation.tasks import get_original_image
from spritacular.utils import compress_and_save_image_locally, compress_image


class ImageMetadataSerializer(serializers.Serializer):
    image = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'tiff', 'png', 'jpeg'])])

    def get_exif_data(self, validated_data):
        # img = Image(validated_data.get('image'))
        # print(f"Latitude: {img.gps_latitude} {img.gps_latitude_ref}")
        # print(f"Longitude: {img.gps_longitude} {img.gps_longitude_ref}\n")

        exif = {}
        gps = {}
        latitude = None
        longitude = None
        try:
            image = validated_data.get('image')
            img = Image.open(image)
            if img._getexif():
                for tag, value in img._getexif().items():
                    if tag in TAGS:
                        exif[TAGS[tag]] = value

            trash_data = ['MakerNote', 'UserComment', 'ImageDescription']

            for i in trash_data:
                if i in exif:
                    exif.pop(i)

            print(exif)

            if 'GPSInfo' in exif:
                for key, val in exif['GPSInfo'].items():
                    name = GPSTAGS.get(key, key)
                    print(f"{name}: {exif['GPSInfo'][key]}")
                    gps[name] = val

                if gps.get('GPSLatitude') and gps.get('GPSLatitudeRef'):
                    latitude = dms_coordinates_to_dd_coordinates(gps['GPSLatitude'], gps['GPSLatitudeRef'])
                    print(
                        f"Latitude (DD): {dms_coordinates_to_dd_coordinates(gps['GPSLatitude'], gps['GPSLatitudeRef'])}")

                if gps.get('GPSLongitude') and gps.get('GPSLongitudeRef'):
                    longitude = dms_coordinates_to_dd_coordinates(gps['GPSLongitude'], gps['GPSLongitudeRef'])
                    print(
                        f"Longitude (DD): {dms_coordinates_to_dd_coordinates(gps['GPSLongitude'], gps['GPSLongitudeRef'])}\n")

        except Exception as e:
            print(f"---{e}")

        return {"latitude": latitude, "longitude": longitude, "FocalLength": exif.get('FocalLength'),
                "DateTime": exif.get('DateTime'), "ISOSpeedRatings": exif.get('ISOSpeedRatings'),
                "ApertureValue": exif.get('ApertureValue')}


class ObservationCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False,
                                                  allow_null=True)
    is_other = serializers.BooleanField(default=False)
    custom_category = serializers.CharField(required=False)

    class Meta:
        model = ObservationCategoryMapping
        fields = ('category', 'is_other', 'custom_category')


class ObservationImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])], required=True)
    category_map = ObservationCategorySerializer(required=False)
    # latitude = serializers.DecimalField(coerce_to_string=False, max_digits=22, decimal_places=16, allow_null=True)
    # longitude = serializers.DecimalField(coerce_to_string=False, max_digits=22, decimal_places=16, allow_null=True)

    class Meta:
        model = ObservationImageMapping
        fields = ('id', 'image', 'location', 'place_uid', 'country_code', 'latitude', 'longitude', 'obs_date', 'obs_time',
                  'timezone', 'azimuth', 'category_map', 'obs_date_time_as_per_utc', 'time_accuracy',
                  'is_precise_azimuth', 'compressed_image', 'image_name')


class ObservationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    map_data = ObservationImageSerializer(many=True, write_only=True)
    camera = serializers.PrimaryKeyRelatedField(queryset=CameraSetting.objects.all(), allow_null=True, required=False)
    images = serializers.SerializerMethodField('get_image', read_only=True)
    user_data = serializers.SerializerMethodField('get_user', read_only=True)
    category_data = serializers.SerializerMethodField('get_category_name', read_only=True)
    camera_data = serializers.SerializerMethodField('get_camera', read_only=True)
    like_watch_count_data = serializers.SerializerMethodField('get_like_watch_count_data', read_only=True)

    class Meta:
        model = Observation
        fields = ('id', 'user', 'image_type', 'camera', 'map_data', 'elevation_angle', 'video_url', 'story', 'images',
                  'user_data', 'is_verified', 'category_data', 'camera_data', 'like_watch_count_data', 'is_submit',
                  'is_reject')

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if 'user_observation_collection' in self.context:
    #         del self.fields['map_data']
    #         del self.fields['camera']

    def get_image(self, data):
        obj = ObservationImageMapping.objects.filter(observation=data)
        # for i in obj:
        serialize_data = ObservationImageSerializer(obj, many=True).data
        for i in serialize_data:
            i['category_map'] = {}
            i['category_map']['category'] = self.get_category(data)
        return serialize_data

    def get_user(self, data):
        user = data.user
        serializer = UserRegisterSerializer(user).data
        serializer['is_voted'] = False
        serializer['is_can_vote'] = False
        if self.context.get('request').user.is_authenticated:
            serializer['is_voted'] = VerifyObservation.objects.filter(observation=data,
                                                                      user=self.context.get('request').user).exists()
            serializer['is_can_vote'] = data.user != self.context.get('request').user
        return serializer

    def get_category(self, data):
        obj = ObservationCategoryMapping.objects.filter(observation=data)
        return [i.category.id for i in obj]

    def get_category_name(self, data):
        obj = ObservationCategoryMapping.objects.filter(observation=data)
        return [{"name": i.category.title, "id": i.category.id} for i in obj]

    def get_camera(self, data):
        return CameraSettingSerializer(data.camera).data

    def get_like_watch_count_data(self, data):
        like_count = ObservationLike.objects.filter(observation=data).count()
        is_like = None
        is_watch = None
        if self.context.get('request').user.is_authenticated:
            is_like = ObservationLike.objects.filter(observation=data, user=self.context.get('request').user).exists()
            is_watch = ObservationWatchCount.objects.filter(observation=data,
                                                            user=self.context.get('request').user).exists()
        watch_count = ObservationWatchCount.objects.filter(observation=data).count()

        return {'like_count': like_count, 'is_like': is_like, 'watch_count': watch_count, 'is_watch': is_watch}

    def validate(self, data):
        image_data = data.get('map_data')
        error_field = {}
        is_error_flag = False
        if self.context.get('is_draft') is None:
            for count, i in enumerate(image_data):
                error_field[count] = {}
                if not i['category_map']['category']:
                    is_error_flag = True
                    error_field[count]['category'] = FIELD_REQUIRED.format("Category")

                elif not i['location']:
                    is_error_flag = True
                    error_field[count]['location'] = FIELD_REQUIRED.format("Location")

                elif not i['longitude']:
                    is_error_flag = True
                    error_field[count]['longitude'] = FIELD_REQUIRED.format("Longitude")

                elif not i['latitude']:
                    is_error_flag = True
                    error_field[count]['latitude'] = FIELD_REQUIRED.format("Latitude")

                elif not i['timezone']:
                    is_error_flag = True
                    error_field[count]['timezone'] = FIELD_REQUIRED.format("Timezone")

                elif not i['obs_date']:
                    is_error_flag = True
                    error_field[count]['obs_date'] = FIELD_REQUIRED.format("Observation date")

                elif not i['obs_time']:
                    is_error_flag = True
                    error_field[count]['obs_time'] = FIELD_REQUIRED.format("Observation time")

                elif not i['azimuth']:
                    is_error_flag = True
                    error_field[count]['azimuth'] = FIELD_REQUIRED.format("Azimuth")

                elif (i['azimuth'] and i['azimuth'].isdigit()) and int(i['azimuth']) > 360:
                    is_error_flag = True
                    error_field[count]['azimuth'] = 'Azimuth angle should not be more than 360°.'

            if is_error_flag:
                raise serializers.ValidationError(error_field, code=400)

        return data

    def create(self, validated_data):
        image_data = validated_data.pop('map_data')
        camera_data = self.context.get('camera_data')
        # Flag for submit or draft request
        submit_flag = self.context.get('is_draft') is None
        observation = None

        self.validate_image_length(validated_data, image_data)

        if validated_data.get('image_type') == 3 and len(image_data) <= 3:
            camera_obj, observation = self.create_camera_observation(camera_data, validated_data, submit_flag)

        for i, data in enumerate(image_data):
            if validated_data.get('image_type') != 3:
                camera_obj, observation = self.create_camera_observation(camera_data, validated_data, submit_flag)

            if image_data[i].get('category_map'):
                category_data = image_data[i].pop('category_map')
                for tle in category_data['category']:
                    if not ObservationCategoryMapping.objects.filter(observation_id=observation.id,
                                                                     category=tle).exists():
                        ObservationCategoryMapping.objects.create(observation_id=observation.id, category=tle)

            # Image Compression
            image_file = image_data[i].pop('image')
            # newfile_name = f"{uuid.uuid4()}.{image_file.name.split('.')[-1]}"  # creating unique file name
            #
            # # First saving original file locally.
            # fs = FileSystemStorage(location="")
            # file_name = fs.save(newfile_name, image_file)
            # image_file_name = fs.url(file_name)
            #
            # compressed_image = compress_image(image_file, newfile_name)  # Compression function call

            image_file_name, compressed_image = compress_and_save_image_locally(image_file)  # Compression function call

            obs_image_map_obj = ObservationImageMapping.objects.create(**image_data[i],
                                                                       compressed_image=compressed_image,
                                                                       observation_id=observation.id,
                                                                       image_name=image_file_name)

            # obs_image_map_obj = ObservationImageMapping.objects.create(**image_data[i], observation_id=observation.id)
            obs_image_map_obj.set_utc()
            get_original_image.delay(obs_image_map_obj.id)  # Calling celery task to save original image from local.

        return observation

    @staticmethod
    def validate_image_length(validated_data, image_data):
        if validated_data.get('image_type') == 1 and len(image_data) > 1:
            raise serializers.ValidationError(SINGLE_IMAGE_VALID, code=400)

        elif validated_data.get('image_type') in [2, 3] and len(image_data) > 3:
            raise serializers.ValidationError(MULTIPLE_IMAGE_VALID, code=400)

    @staticmethod
    def create_camera_observation(camera_data, validated_data, submit_flag):
        # if isinstance(camera_data, dict):
        camera_obj = CameraSetting.objects.create(user=validated_data.get('user'),
                                                  camera_type=camera_data.get('camera_type'),
                                                  iso=camera_data.get('iso'),
                                                  shutter_speed=camera_data.get('shutter_speed'),
                                                  fps=camera_data.get('fps'),
                                                  lens_type=camera_data.get('lens_type'),
                                                  focal_length=camera_data.get('focal_length'),
                                                  aperture=camera_data.get('aperture', 'None'),
                                                  question_field_one=camera_data.get('question_field_one'),
                                                  question_field_two=camera_data.get('question_field_two'),
                                                  is_profile_camera_settings=False)
        # else:
        #     try:
        #         camera_obj = CameraSetting.objects.get(pk=camera_data)
        #     except CameraSetting.DoesNotExist:
        #         camera_obj = None

        observation = Observation.objects.create(**validated_data, is_submit=submit_flag, camera=camera_obj)

        return camera_obj, observation

    def update(self, instance, validated_data):
        image_data = validated_data.pop('map_data')
        # Flag for submit or draft request
        submit_flag = self.context.get('is_draft') is None

        if validated_data.get('image_type') in [1, 2] and len(image_data) > 1:
            raise serializers.ValidationError(SINGLE_IMAGE_VALID, code=400)

        elif validated_data.get('image_type') == 3 and len(image_data) > 3:
            raise serializers.ValidationError(MULTIPLE_IMAGE_VALID, code=400)

        # if submit
        instance.is_submit = submit_flag
        instance.save()

        category_data = image_data[0].get('category_map')
        # Deleting all previously selected tle
        ObservationCategoryMapping.objects.filter(observation=instance).delete()

        for tle in category_data.get('category'):
            ObservationCategoryMapping.objects.create(observation_id=instance.id, category=tle)

        if validated_data.get('image_type') != 3:
            map_obj = ObservationImageMapping.objects.filter(observation=instance).order_by('pk')
            for i in map_obj:
                # i.image = image_data[0].get('image')

                # Image Compression
                image_file = image_data[0].get('image')
                # Compression function call
                image_file_name, compressed_image = compress_and_save_image_locally(image_file)

                i.location = image_data[0].get('location')
                i.timezone = image_data[0].get('timezone')
                i.longitude = image_data[0].get('longitude')
                i.latitude = image_data[0].get('latitude')
                i.azimuth = image_data[0].get('azimuth')
                i.obs_date = image_data[0].get('obs_date')
                i.obs_time = image_data[0].get('obs_time')
                i.is_precise_azimuth = image_data[0].get('is_precise_azimuth')
                i.time_accuracy = image_data[0].get('time_accuracy')
                i.image_name = image_file_name
                i.compressed_image = compressed_image
                i.save()
                i.set_utc()
                get_original_image.delay(i.id)  # Calling celery task to save original image from local.

        else:
            ObservationImageMapping.objects.filter(observation=instance).delete()
            for i in image_data:
                i.pop('category_map')

                # Image Compression
                image_file = i.pop('image')
                # Compression function call
                image_file_name, compressed_image = compress_and_save_image_locally(image_file)

                obs_image_map_obj = ObservationImageMapping.objects.create(**i, observation=instance,
                                                                           compressed_image=compressed_image,
                                                                           image_name=image_file_name)
                obs_image_map_obj.set_utc()
                get_original_image.delay(obs_image_map_obj.id)  # Calling celery task to save original image from local.

        # TODO: submit draft or update draft
        return instance


class ObservationCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_data = serializers.SerializerMethodField('get_user_data', read_only=True)

    class Meta:
        model = ObservationComment
        fields = '__all__'

    def get_user_data(self, data):
        user_obj = data.user
        return UserRegisterSerializer(user_obj).data

