from celery import shared_task
from sentry_sdk import capture_exception

from .models import BlogImageData


@shared_task(name='delete_unpublished_images')
def delete_unpublished_images():
    try:
        for img in BlogImageData.objects.all():
            if not img.is_published:
                img.delete()
    except Exception as e:
        capture_exception(e)
        print(f"----delete_unpublished_images tasks---- {e}")
