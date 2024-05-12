from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.user_login, name='user_login'),
    path('signup', views.user_signup, name='user_signup'),
    path('logout', views.user_logout, name='user_logout'),
    path('generate-transcript', views.generateTranscript, name='generate-transcript'),
    path('delete-post/<int:pk>/', views.deletePost, name='delete-post'),
    path('export-text/<int:pk>/', views.exportText, name='export-text'),
    path('transcript-list', views.transcript_list, name='transcript-list'),
    path('transcript-details/<int:pk>/', views.transcript_details, name='transcript-details')
]
