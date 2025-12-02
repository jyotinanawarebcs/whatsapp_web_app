from django.urls import path
from . import views

app_name = 'contacts'  # Add this for namespace

urlpatterns = [
    # -------------------------
    # File Management Routes
    # -------------------------
    path('files/upload/', views.upload_contacts, name='upload_contacts'),
    path('files/', views.list_files, name='list_files'),
    path('files/<str:filename>/', views.contacts_by_file, name='contacts_by_file'),
    path('files/<str:filename>/delete/', views.delete_by_file, name='delete_by_file'),
    
    # -------------------------
    # Contact Management Routes
    # -------------------------
    path('', views.list_contacts, name='list_contacts'),
    path('create/', views.create_contact, name='create_contact'),
    path('search/', views.search_contacts, name='search_contacts'),
    
    # -------------------------
    # Single Contact Operations
    # -------------------------
    path('<int:pk>/', views.retrieve_contact, name='retrieve_contact'),
    path('<int:pk>/update/', views.update_contact, name='update_contact'),
    path('<int:pk>/delete/', views.delete_contact, name='delete_contact'),
]