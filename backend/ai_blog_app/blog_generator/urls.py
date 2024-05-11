from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.user_login, name='user_login'),
    path('signup', views.user_signup, name='user_signup'),
    path('logout', views.user_logout, name='user_logout'),
    path('generate-blog', views.generateBlog, name='generate-blog'),
    path('transcript-list', views.transcript_list, name='transcript-list'),
    path('transcript-details/<int:pk>/', views.transcript_details, name='transcript-details')
]
