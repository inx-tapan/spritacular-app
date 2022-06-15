import sys
import uuid
from io import BytesIO

from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image(obs_image, file_name):
    """
    Image compression function
    :param obs_image: InMemoryFileObject
    :param file_name: image file name
    :return: new compressed InMemoryFileObject
    """
    im = Image.open(obs_image)

    if im.width == im.height:
        new_size = (int(im.width/2), int(im.height/2))
    elif im.width > im.height:
        new_size = (int(im.width/3), int(im.height/2))
    else:
        new_size = (int(im.width/2), int(im.height/3))

    im.thumbnail(new_size)

    output = BytesIO()
    ext = im.format
    if im.format == 'PNG':
        im = im.convert(
            mode='P',  # use mode='PA' for transparency
            palette=Image.ADAPTIVE
        )
    im.save(output, format=ext, quality=90)
    output.seek(0)

    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{file_name.split('.')[0]}.{file_name.split('.')[-1]}",
        f"image/{file_name.split('.')[-1]}",
        sys.getsizeof(output),
        None,
    )


def compress_and_save_image_locally(image_obj):
    """
    function for saving inMemoryFileObject of image locally.
    :param image_obj:
    :return: filename
    """
    newfile_name = f"{uuid.uuid4()}.{image_obj.name.split('.')[-1]}"  # creating unique file name

    # First saving original file locally.
    fs = FileSystemStorage(location="")
    file_name = fs.save(newfile_name, image_obj)
    image_file_name = fs.url(file_name)

    compressed_image = compress_image(image_obj, newfile_name)  # Compression function call

    return image_file_name, compressed_image

