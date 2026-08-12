from django.urls import path
from . import views

urlpatterns = [
    path('floor-plan-data/', views.floor_plan_data, name='floor_plan_data'),
    path('floor-plan/', views.floor_plan_editor, name='floor_plan_editor'),
    path('<int:table_id>/update-position/', views.update_table_position, name='update_table_position'),
]