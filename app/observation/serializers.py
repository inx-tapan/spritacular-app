import datetime

from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from PIL import Image
# from exif import Image
from PIL.ExifTags import TAGS, GPSTAGS
from .utils import dms_coordinates_to_dd_coordinates
from .models import ObservationImageMapping, Observation, Category, ObservationCategoryMapping
from users.models import CameraSetting


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
    image = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'tiff', 'png', 'jpeg'])])
    category_map = ObservationCategory(required=False)

    class Meta:
        model = ObservationImageMapping
        fields = ('image', 'location', 'latitude', 'longitude', 'obs_date', 'obs_time',
                  'timezone', 'azimuth', 'category_map')


class ObservationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    map_data = ObservationImageSerializer(many=True)
    camera = serializers.PrimaryKeyRelatedField(queryset=CameraSetting.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Observation
        fields = ('user', 'image_type', 'camera', 'map_data')

    def validate(self, data):
        image_data = data.get('map_data')
        error_field = {}
        if self.context.get('is_draft') is None:
            for i in image_data:
                print(f"@@{i}@@")
                error_field[i['image_id']] = {}
                if not i['category_map']['category']:
                    error_field[i['image_id']]['category'] = 'Category is a required field.'

                if not i['location']:
                    error_field[i['image_id']]['location'] = 'Location is a required field.'

                if not i['longitude']:
                    error_field[i['image_id']]['longitude'] = 'Longitude is a required field.'

                if not i['latitude']:
                    error_field[i['image_id']]['latitude'] = 'Latitude is a required field.'

                if not i['timezone']:
                    error_field[i['image_id']]['timezone'] = 'timezone is a required field.'

                if not i['obs_date']:
                    error_field[i['image_id']]['obs_date'] = 'Obs_date is a required field.'

                if not i['obs_time']:
                    error_field[i['image_id']]['obs_time'] = 'Obs_time is a required field.'

                if not i['azimuth']:
                    error_field[i['image_id']]['azimuth'] = 'Azimuth is a required field.'

            if error_field:
                raise serializers.ValidationError(error_field, code=400)

            if data.get('camera') is None:
                raise serializers.ValidationError('Equipment details not provided.', code=400)

        return data

    def create(self, validated_data):
        print("\n-----------------------------------------------\n")
        print(validated_data)
        print("\n-----------------------------------------------\n")
        image_data = validated_data.pop('map_data')
        observation = None
        category_data = {}

        if validated_data.get('image_type') == 1 and len(image_data) > 1:
            raise serializers.ValidationError('Number of the images should not be more than 1.', code=400)

        elif (validated_data.get('image_type') == 2 or validated_data.get('image_type') == 3) and len(image_data) > 3:
            raise serializers.ValidationError('Number of the images should not be more than 3', code=400)

        elif validated_data.get('image_type') == 3 and len(image_data) <= 3:
            observation = Observation.objects.create(**validated_data)

        for i, data in enumerate(image_data):
            if image_data[i].get('category_map'):
                category_data = image_data[i].pop('category_map')

            if validated_data.get('image_type') != 3:
                observation = Observation.objects.create(**validated_data)

            ObservationImageMapping.objects.create(**image_data[i], observation_id=observation.id)

            if category_data.get('category'):
                for tle in category_data['category']:
                    ObservationCategoryMapping.objects.create(observation_id=observation.id, category=tle)

        return observation
