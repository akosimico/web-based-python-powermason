from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface URL
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.projects, name='projects'),
    path('costs/', views.costs, name='costs'),
    path('estimation/', views.estimation, name='estimation'),
    path('reports/', views.reports, name='reports'),
    path('import_excel/', views.import_excel, name='import_excel'),
]
