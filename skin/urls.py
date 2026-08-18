from django.urls import path
from . import views

urlpatterns = [
    # Dashboard and Skin Analysis URLs
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),

    # Scan History and Scan Detail URLs
    path("scan-history/", views.scan_history, name="scan_history"),
    path("scan/<uuid:scan_id>/", views.scan_detail, name="scan_detail"),
    path("scan/<uuid:scan_id>/delete/", views.delete_scan, name="delete_scan"),

    path('about', views.about, name="about"),

    # User Authentication URLs
    path('signup', views.signup, name="signup"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),

    # User Profile URL
    path('profile', views.profile, name="profile"), 

    path('skin_profile', views.skin_profile, name="skin_profile"),  # URL for overall skin profile

    path('skin_profile/edit', views.edit_skin_profile, name="edit_skin_profile"),  # URL for editing skin profile

    # Report 
    path("report/download/", views.download_report, name="download_report"),


    #Chat URL
    path("chat", views.chat_page, name="chat"),
    path("chat/new/", views.new_chat, name="new_chat"),
    path("chat/send/", views.send_message, name="send_message"),
    path("chat/history/<uuid:session_id>/", views.chat_history, name="chat_history"),
    #path("chat/sessions/", views.chat_sessions, name="chat_sessions"),
    path("chat/delete/", views.delete_chat, name="delete_chat"),
]
