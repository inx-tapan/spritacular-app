from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from PIL import Image
# from exif import Image
from PIL.ExifTags import TAGS, GPSTAGS
from .utils import dms_coordinates_to_dd_coordinates


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

            if 'GPSInfo' in exif:
                for key, val in exif['GPSInfo'].items():
                    name = GPSTAGS.get(key, key)
                    print(f"{name}: {exif['GPSInfo'][key]}")
                    gps[name] = val

                if gps.get('GPSLatitude') and gps.get('GPSLatitudeRef'):
                    latitude = dms_coordinates_to_dd_coordinates(gps['GPSLatitude'], gps['GPSLatitudeRef'])
                    print(f"Latitude (DD): {dms_coordinates_to_dd_coordinates(gps['GPSLatitude'], gps['GPSLatitudeRef'])}")

                if gps.get('GPSLongitude') and gps.get('GPSLongitudeRef'):
                    longitude = dms_coordinates_to_dd_coordinates(gps['GPSLongitude'], gps['GPSLongitudeRef'])
                    print(f"Longitude (DD): {dms_coordinates_to_dd_coordinates(gps['GPSLongitude'], gps['GPSLongitudeRef'])}\n")

        except Exception as e:
            print(f"---{e}")

        # print(f"Latitude (DD): {dms_coordinates_to_dd_coordinates(img.gps_latitude, img.gps_latitude_ref)}")
        # print(f"Longitude (DD): {dms_coordinates_to_dd_coordinates(img.gps_longitude, img.gps_longitude_ref)}\n")
        # print(f"Focal Length: {img.focal_length}")
        # # print(f"Aperture: {img.max_aperture_value}")
        # # print(f"shutter_speed_value: {img.shutter_speed_value}")
        # print(f"Date Time: {img.datetime}")
        # print(f"Camera: {img.software}")

        return {"latitude": latitude, "longitude": longitude, "FocalLength": exif.get('FocalLength'),
                "DateTime": exif.get('DateTime'), "ISOSpeedRatings": exif.get('ISOSpeedRatings'),
                "ApertureValue": exif.get('ApertureValue')}








