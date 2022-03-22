import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image(obs_image):
    file_name = obs_image.name
    im = Image.open(obs_image)
    output = BytesIO()
    ext = im.format
    if im.format == 'PNG':
        im = im.convert(
            mode='P',  # use mode='PA' for transparency
            palette=Image.ADAPTIVE
        )
    im.save(output, format=ext, quality=50)
    output.seek(0)

    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{file_name.split('.')[0]}.{file_name.split('.')[-1]}",
        f"image/{file_name.split('.')[-1]}",
        sys.getsizeof(output),
        None,
    )
