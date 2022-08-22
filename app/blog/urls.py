from django.urls import path
from .views import BlogViewSet, GetImageUrlViewSet, BlogCategoryListViewSet, MeetTheTeamViewSet
urlpatterns = [
    # List of blog category
    path('get_blog_category_list/', BlogCategoryListViewSet.as_view(), name='get_blog_category_list'),
    # Create Blog
    path('create_blog/', BlogViewSet.as_view({'post': 'create', 'get': 'retrieve'}), name='blog'),
    # Get Blog details
    path('get_blog/<slug:slug>/', BlogViewSet.as_view({'get': 'retrieve'}), name='get_blog'),
    # Update Blog/Tutorial
    path('update_blog/<slug:slug>/', BlogViewSet.as_view({'put': 'update'}), name='update_blog'),
    # Delete Blog/Tutorial
    path('delete_blog/<slug:slug>/', BlogViewSet.as_view({'delete': 'destroy'}), name='delete_blog'),
    # Get list of all blogs
    path('get_all_blog/<int:type>/', BlogViewSet.as_view({'get': 'list'}), name='get_all_blog'),
    # Upload Image
    path('upload/', GetImageUrlViewSet.as_view({'post': 'create'}), name="upload"),
    # path('destroy/<int:pk>/', GetImageUrlViewSet.as_view({'delete': 'destroy'}), name="destroy")
    # List spritacular team
    path('list_team/', MeetTheTeamViewSet.as_view({'get': 'list'}, name='list_team')),
    # Meet the team create
    path('add_team_member/', MeetTheTeamViewSet.as_view({'post': 'create'}, name='add_team_member')),
    # Meet the team update
    path('update_team_member/<int:pk>/', MeetTheTeamViewSet.as_view({'put': 'update'}, name='update_team_member')),
    # Meet the team retrieve
    path('get_team_member/<int:pk>/', MeetTheTeamViewSet.as_view({'get': 'retrieve'}, name='get_team_member')),
    # Meet the team delete
    path('delete_team_member/<int:pk>/', MeetTheTeamViewSet.as_view({'delete': 'destroy'}, name='delete_team_member')),
]

