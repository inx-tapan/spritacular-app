import constants
import json

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from blog.models import BlogCategory, Blog, BlogImageData


class BlogCategoryListViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = []
        for i in BlogCategory.objects.all():
            category_details = {
                'id': i.pk,
                'name': i.title
            }
            data.append(category_details)

        return Response(data, status=status.HTTP_200_OK)


class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Blog.objects.all()

    def list(self, request, *args, **kwargs):
        blog_data = []
        for i in self.get_queryset():
            record = {
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "content": i.content,
                "thumbnail_image": i.thumbnail_image.url,
                "category": i.category.id
            }

            blog_data.append(record)

        return Response({'data': blog_data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        if not request.data.get('thumbnail_image'):
            return Response({'detail': 'Thumbnail image not provided.', 'status': 0}, status=status.HTTP_404_NOT_FOUND)
        if not request.data.get('category'):
            return Response({'detail': 'Category not selected.', 'status': 0}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'thumbnail_image': request.data.get('thumbnail_image'),
            'user': request.user,
            'title': request.data.get('title'),
            'content': request.data.get('content'),
            'description': request.data.get('description')
        }
        category = request.data.get('category')
        image_ids_data = request.data.get('image_ids') or []
        image_ids = json.loads(image_ids_data)

        Blog.objects.create(**data, category_id=category)

        for i in image_ids:
            try:
                BlogImageData.objects.filter(id=i.get('id')).update(is_published=True)
            except BlogImageData.DoesNotExist:
                pass
        return Response(constants.BLOG_FORM_SUCCESS, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            blog_obj = Blog.objects.get(pk=kwargs.get('pk'))
        except Blog.DoesNotExist:
            return Response(constants.NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        return Response({"data": {"id": blog_obj.id,
                                  "title": blog_obj.title,
                                  "description": blog_obj.description,
                                  "content": blog_obj.content,
                                  "category": blog_obj.category.id}}, status=status.HTTP_200_OK)


class GetImageUrlViewSet(viewsets.ModelViewSet):

    def create(self, request, *args, **kwargs):
        image = request.FILES.get('image')
        blog_image_obj = BlogImageData.objects.create(image_file=image)

        return Response({"uploaded": True,
                         "url": blog_image_obj.image_file.url,
                         "image_id": blog_image_obj.id},
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            image_obj = BlogImageData.objects.get(pk=kwargs.get('pg'))
        except BlogImageData.DoesNotExist:
            return Response(constants.NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        image_obj.delete()

        return Response({'status': 1}, status=status.HTTP_200_OK)
