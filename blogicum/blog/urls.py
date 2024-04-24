from django.urls import path

from .views import (
    CategoryListView, PostCreateView, add_comment,
    CommentUpdateView, CommentDeleteView, PostUpdateView,
    PostDeleteView, ProfileUpdateView, ProfileListView, IndexListView,
    PostDetailView
)

app_name = 'blog'

urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('posts/create/',
         PostCreateView.as_view(),
         name='create_post'
         ),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/edit/',
         PostUpdateView.as_view(),
         name='edit_post'
         ),
    path('posts/<int:post_id>/delete/',
         PostDeleteView.as_view(),
         name='delete_post'
         ),
    path('category/<slug:category_slug>/',
         CategoryListView.as_view(),
         name='category_posts'
         ),
    path('profile/<str:username>/', ProfileListView.as_view(), name='profile'),
    path('edit_profile/',
         ProfileUpdateView.as_view(),
         name='edit_profile'
         ),
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:post_id>/comment/<int:comment_id>',
         CommentUpdateView.as_view(),
         name='edit_comment'
         ),
    path('posts/<int:post_id>/comment/<int:comment_id>/delete_comment/',
         CommentDeleteView.as_view(),
         name='delete_comment'
         ),
]
