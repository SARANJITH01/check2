"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views


urlpatterns = [

    path ('',views.home,name='home'),
    path('login/',views.login,name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('user_registration/',views.user_registration,name='user_registration'),

    # ------------------------------------------ ADMIN ------------------------------------------------------------------------------------

    path('admin_home/',views.admin_home,name='admin_home'),
    path('admin_view_users/',views.admin_view_users,name='admin_view_users'),
    path('admin_view_complaints/',views.admin_view_complaints,name='admin_view_complaints'),
    path('admin_view_feedback/',views.admin_view_feedback,name='admin_view_feedback'),


    # ------------------------------------------ USERS ------------------------------------------------------------------------------------

    path('user_home/',views.user_home,name='user_home'),
    path('user_send_complaint/',views.user_send_complaint,name='user_send_complaint'),
    path('user_delete_complaint/<int:id>/',views.user_delete_complaint, name = 'user_delete_complaint'),
    path('user_send_feedback/',views.user_send_feedback,name='user_send_feedback'),
    path('user_delete_feedback/<int:id>/',views.user_delete_feedback, name = 'user_delete_feedback'),
    path('mouse_control_eye/',views.mouse_control_eye,name='mouse_control_eye'),
    path('mouse_control_hand/',views.mouse_control_hand,name='mouse_control_hand'),
    path('mouse_control/', views.mouse_control_page, name='mouse_control_page'),
    path('stop_mouse_control/', views.stop_mouse_control, name='stop_mouse_control'),
    path('api/get_available_cameras/', views.get_available_cameras, name='get_available_cameras'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('api/stop_stream/', views.stop_stream_api, name='stop_stream_api'),
    path('api/stream_status/', views.stream_status_api, name='stream_status_api'),
    path('api/set_mouse_control/', views.set_mouse_control_api, name='set_mouse_control_api'),
    path('api/recalibrate_center/', views.recalibrate_center_api, name='recalibrate_center_api'),
]


