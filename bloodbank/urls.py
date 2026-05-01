from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test-modern/', lambda request: render(request, 'bloodbank/test_modern.html'), name='test_modern'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('request-blood/', views.BloodRequestCreateView.as_view(), name='request_blood'),
    path('requests/', views.BloodRequestListView.as_view(), name='request_list'),
    path('approve-request/<int:pk>/', views.approve_request, name='approve_request'),
    path('fulfill-request/<int:pk>/', views.fulfill_request, name='fulfill_request'),
    path('cancel-request/<int:pk>/', views.cancel_blood_request, name='cancel_request'),
    path('accept-donation/<int:pk>/', views.accept_donation, name='accept_donation'),
    path('cancel-donation/<int:pk>/', views.cancel_donation, name='cancel_donation'),
    path('update-stock/<int:pk>/', views.BloodStockUpdateView.as_view(), name='update_stock'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('verify-user/<int:pk>/', views.verify_user, name='verify_user'),
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
]
