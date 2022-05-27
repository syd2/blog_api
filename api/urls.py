from django.urls import path
from .views import post_list, post_create, post_detail, PostComment, post_delete, DetailPostComment, PostUpdate

urlpatterns = [
    path('posts/', post_list),
    path('posts/create/', post_create),
    path('posts/<int:id>/', post_detail),
    path('posts/<int:id>/delete/', post_delete),
    path('posts/<int:pk>/comments/', PostComment.as_view()),
    path('posts/<int:pk>/comments/<int:comment_pk>/', DetailPostComment.as_view()),
    path('posts/<int:pk>/update/', PostUpdate.as_view())
]
