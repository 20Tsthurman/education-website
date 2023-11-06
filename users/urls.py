# users/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import delete_discussion

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('account_settings/', views.account_settings, name='account_settings'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.homepage, name='homepage'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('discussions/', views.combined_discussions, name='combined_discussions'),
    path('discussions/<int:discussion_id>/', views.view_discussion, name='view_discussion'),
    path('reply/post/<int:discussion_id>/', views.post_reply, name='post_reply'),
    path('discussion/<int:discussion_id>/delete/', delete_discussion, name='delete_discussion'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)