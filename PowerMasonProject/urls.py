from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.projects, name='projects'),
    path('costs/', views.costs, name='costs'),
    path('estimation/', views.estimation, name='estimation'),
    path('reports/', views.reports, name='reports'),
]