import constants

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
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


class BlogViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user
        Blog.objects.create(**data)
        return Response(constants.BLOG_FORM_SUCCESS, status=status.HTTP_201_CREATED)

