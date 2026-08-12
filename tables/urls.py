from django.urls import path
from . import views

urlpatterns = [
    path('floor-plan-data/', views.floor_plan_data, name='floor_plan_data'),
]