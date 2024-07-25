from django.contrib import admin
from django.urls import path ,include
from .views import *
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'), 
    path('upload/file/', FileUploadView.as_view(), name='upload_file'),
    path('review-requests/', ReviewRequestsView.as_view(), name='review_requests'), 
    path('review_request/<int:pk>/', ReviewRequestDetailView.as_view(), name='review_request_detail'),
    path('user/files/', UserFilesView.as_view(), name='user_files'),
    path('access-denied/', AccessDeniedView.as_view(), name='access_denied'), 
    path('all_files/',AllFilesView.as_view(),name='all_files'),
    path('supervisor_requests/', SupervisorRequestsView.as_view(), name='supervisor_requests'),
    path('file-requests/', FileRequestListView.as_view(), name='file_requests'),
    path('file-requests/add/', FileRequestCreateView.as_view(), name='add_file_request'),
    path('manage-requests/', UserFileRequestListView.as_view(), name='manage_requests'),
    path('request/<int:pk>/', FileRequestDetailView.as_view(), name='request_detail'),





]