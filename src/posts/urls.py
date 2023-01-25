from django.urls import path
from . import views


app_name = 'posts'

urlpatterns = [
    path('', views.post_comment_create_list_view, name='main-post-view'),
    path('like-dislike-post', views.like_dislike_post, name='like-dislike-post-view'),
    path('<pk>/delete', views.PostDeleteView.as_view(), name='post-delete'),
    path('<pk>/update', views.PostUpdateView.as_view(), name='post-update'),
    path('search-post/', views.PostListByName.as_view(), name='post-search'),
    path('not-found/', views.PostListByName.as_view(), name='not-found'),
]
