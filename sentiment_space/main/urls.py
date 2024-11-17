from django.urls import path
from .views import register, user_login, reset_password
from .views import home, create_post, add_comment,logout_view,new_password,my_posts
from . import views




urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('reset-password/', reset_password, name='reset_password'),
    path('', home, name='home'),
    path('new-password/', new_password, name='new_password'),
    path('logout/', logout_view, name='logout'),
    path('create-post/', create_post, name='create_post'),
    path('my-posts/', my_posts, name='my_posts'),
    path('add_comment/<int:post_id>/add-comment/', add_comment, name='add_comment'),
    path('analyze_sentiment/', views.analyze_sentiment, name='analyze_sentiment'),
]
