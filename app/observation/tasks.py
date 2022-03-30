import sys

from celery import shared_task
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from observation.models import ObservationImageMapping


@shared_task(name='observation_image_compression')
def observation_image_compression(obs_image_map_id):
    obs_image_map_obj = ObservationImageMapping.objects.get(pk=obs_image_map_id)
    img_file = obs_image_map_obj.image
    file_name = img_file.name.split('/')[-1]
    im = Image.open(img_file)
    output = BytesIO()
    ext = im.format
    if im.format == 'PNG':
        im = im.convert(
            mode='P',  # use mode='PA' for transparency
            palette=Image.ADAPTIVE
        )
    im.save(output, format=ext, quality=70)
    output.seek(0)

    image_file = InMemoryUploadedFile(
        output,
        'ImageField',
        f"{file_name.split('.')[0]}.{file_name.split('.')[-1]}",
        f"image/{file_name.split('.')[-1]}",
        sys.getsizeof(output),
        None,
    )

    obs_image_map_obj.compressed_image = image_file
    obs_image_map_obj.save()
