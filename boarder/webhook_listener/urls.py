from django.urls import path

from . import views

urlpatterns = [
    path("", views.BoardingProcessListView.as_view(), name="BoardingView"),
    path("webhook", views.webhook, name="webhook"),
    path('boarding/<int:pk>/', views.BoardingProcessDetailView.as_view(), name='boarding_process_detail'),
    path('boarding/lookup/<int:pk>/', views.DeviceNetboxLookup, name='device_netbox_lookup'),
    path('boarding/approve/<int:pk>/', views.BoardingProcessApproval, name='boarding_process_approve'),
    path('boarding/deny/<int:pk>/', views.BoardingProcessDeny, name='boarding_process_deny'),
    path('boarding/delete/<int:pk>/', views.BoardingProcessDelete, name='boarding_process_delete')
]