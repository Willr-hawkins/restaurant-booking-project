from django.urls import path
from . import views

urlpatterns = [
    path('floor-plan-data/', views.floor_plan_data, name='floor_plan_data'),
    path('floor-plan/', views.floor_plan_editor, name='floor_plan_editor'),
    path('<int:table_id>/update-position/', views.update_table_position, name='update_table_position'),
    path('', views.table_list, name='table_list'),
    path('add/', views.table_create, name='table_create'),
    path('<int:table_id>/edit/', views.table_edit, name='table_edit'),
    path('<int:table_id>/delete/', views.table_delete, name='table_delete'),
    path('booking/<int:booking_id>/reassign/', views.reassign_booking, name='reassign_booking'),
]