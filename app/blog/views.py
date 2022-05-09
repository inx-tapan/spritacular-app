import constants

from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from blog.models import BlogCategory, Blog


class BlogCategoryListViewSet(APIView):
    queryset = BlogCategory.objects.all()

    def get(self, request, *args, **kwargs):
        data = []
        for i in self.queryset:
            category_details = {
                'id': i.pk,
                'name': i.title
            }
            data.append(category_details)

        return Response(data, status=status.HTTP_200_OK)


class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Blog.objects.all()

    def list(self, request, *args, **kwargs):
        blog_data = []
        for i in self.queryset:
            record = {"title": i.title,
                      "description": i.description,
                      "content": i.content}

            blog_data.append(record)

        return Response({'data': blog_data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user
        Blog.objects.create(**data)
        return Response(constants.BLOG_FORM_SUCCESS, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            blog_obj = Blog.objects.get(pk=kwargs.get('pk'))
        except Blog.DoesNotExist:
            return Response(constants.NOT_FOUND, status=status.HTTP_404_NOT_FOUND)

        return Response({"data": {"title": blog_obj.title, "description": blog_obj.description,
                         "content": blog_obj.content}}, status=status.HTTP_200_OK)

