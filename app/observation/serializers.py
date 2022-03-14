import datetime

from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from PIL import Image
# from exif import Image
from PIL.ExifTags import TAGS, GPSTAGS
from .utils import dms_coordinates_to_dd_coordinates
from .models import ObservationImageMapping, Observation, Category, ObservationCategoryMapping
from users.models import CameraSetting
from users.serializers import UserRegisterSerializer
from constants import FIELD_REQUIRED


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
            # required_data = ['GPSInfo', 'FocalLength', 'FocalLengthIn35mmFilm', 'ISOSpeedRatings',
            #                  'ExposureTime', 'Make', 'DateTime', 'ApertureValue']

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


class ObservationCategory(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False,
                                                  allow_null=True)
    is_other = serializers.BooleanField(default=False)
    custom_category = serializers.CharField(required=False)

    class Meta:
        model = ObservationCategoryMapping
        fields = ('category', 'is_other', 'custom_category')


class ObservationImageSerializer(serializers.ModelSerializer):
    item = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'tiff', 'png', 'jpeg'])])
    category_map = ObservationCategory(required=False)

    class Meta:
        model = ObservationImageMapping
        fields = ('item', 'location', 'place_uid', 'country_code', 'latitude', 'longitude', 'obs_date', 'obs_time',
                  'timezone', 'azimuth', 'category_map')


class ObservationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    map_data = ObservationImageSerializer(many=True)
    camera = serializers.PrimaryKeyRelatedField(queryset=CameraSetting.objects.all(), allow_null=True, required=False)
    images = serializers.SerializerMethodField('get_image', read_only=True)
    user_data = serializers.SerializerMethodField('get_user', read_only=True)

    class Meta:
        model = Observation
        fields = ('user', 'image_type', 'camera', 'map_data', 'elevation_angle', 'video_url', 'story', 'images',
                  'user_data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user_observation_collection' in self.context:
            del self.fields['map_data']
            del self.fields['camera']

    def get_image(self, data):
        obj = ObservationImageMapping.objects.filter(observation=data)
        return ObservationImageSerializer(obj, many=True).data

    def get_user(self, data):
        user = data.user
        return UserRegisterSerializer(user).data

    # def validate(self, data):
    #     image_data = data.get('map_data')
    #     error_field = {}
    #     is_error_flag = False
    #     if self.context.get('is_draft') is None:
    #         for count, i in enumerate(image_data):
    #             print(f"@@{i}@@")
    #             error_field[count] = {}
    #             if not i['category_map']['category']:
    #                 is_error_flag = True
    #                 error_field[count]['category'] = FIELD_REQUIRED.format("Category")
    #
    #             elif not i['location']:
    #                 is_error_flag = True
    #                 error_field[count]['location'] = FIELD_REQUIRED.format("Location")
    #
    #             elif not i['longitude']:
    #                 is_error_flag = True
    #                 error_field[count]['longitude'] = FIELD_REQUIRED.format("Longitude")
    #
    #             elif not i['latitude']:
    #                 is_error_flag = True
    #                 error_field[count]['latitude'] = FIELD_REQUIRED.format("Latitude")
    #
    #             elif not i['timezone']:
    #                 is_error_flag = True
    #                 error_field[count]['timezone'] = FIELD_REQUIRED.format("Timezone")
    #
    #             elif not i['obs_date']:
    #                 is_error_flag = True
    #                 error_field[count]['obs_date'] = FIELD_REQUIRED.format("Obs_date")
    #
    #             elif not i['obs_time']:
    #                 is_error_flag = True
    #                 error_field[count]['obs_time'] = FIELD_REQUIRED.format("Obs_time")
    #
    #             elif not i['azimuth']:
    #                 is_error_flag = True
    #                 error_field[count]['azimuth'] = FIELD_REQUIRED.format("Azimuth")
    #
    #         if is_error_flag:
    #             raise serializers.ValidationError(error_field, code=400)
    #
    #     return data

    def create(self, validated_data):
        image_data = validated_data.pop('map_data')
        camera_data = self.context.get('camera_data')
        print(f"@@{camera_data}")
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
                    ObservationCategoryMapping.objects.create(observation_id=observation.id, category=tle)

            test_image = image_data[i].pop('item')
            ObservationImageMapping.objects.create(**image_data[i], observation_id=observation.id, image=test_image)

        return observation

    @staticmethod
    def validate_image_length(validated_data, image_data):
        if validated_data.get('image_type') == 1 and len(image_data) > 1:
            raise serializers.ValidationError('Number of the images should not be more than 1.', code=400)

        elif (validated_data.get('image_type') == 2 or validated_data.get('image_type') == 3) and len(image_data) > 3:
            raise serializers.ValidationError('Number of the images should not be more than 3', code=400)

    @staticmethod
    def create_camera_observation(camera_data, validated_data, submit_flag):
        if isinstance(camera_data, dict):
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
        else:
            camera_obj = camera_data

        observation = Observation.objects.create(**validated_data, is_submit=submit_flag, camera=camera_obj)

        return camera_obj, observation

    def update(self, instance, validated_data):
        image_data = validated_data.pop('map_data')
        submit_flag = self.context.get('is_draft') is None

        if validated_data.get('image_type') == 1 and len(image_data) > 1:
            raise serializers.ValidationError('Number of the images should not be more than 1.', code=400)

        elif validated_data.get('image_type') == 2 and len(image_data) > 1:
            raise serializers.ValidationError('Number of the images should not be more than 1', code=400)

        # if submit
        instance.is_submit = submit_flag
        instance.save()

        category_data = image_data[0].get('category_map')
        ObservationCategoryMapping.objects.filter(observation=instance).delete()

        for tle in category_data.get('category'):
            ObservationCategoryMapping.objects.create(observation_id=instance.id, category=tle)

        map_obj = ObservationImageMapping.objects.filter(observation=instance).order_by('pk')
        for i in map_obj:
            i.image = image_data[0].get('image')
            i.location = image_data[0].get('location')
            i.timezone = image_data[0].get('timezone')
            i.longitude = image_data[0].get('longitude')
            i.latitude = image_data[0].get('latitude')
            i.azimuth = image_data[0].get('azimuth')
            i.obs_date = image_data[0].get('obs_date')
            i.obs_time = image_data[0].get('obs_time')
            i.save()

        # TODO: submit draft or update draft
        return instance
