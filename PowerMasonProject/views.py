
from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html', {'active_tab': 'dashboard'})

def projects(request):
    return render(request, 'projects.html', {'active_tab': 'projects'})

def costs(request):
    return render(request, 'costs.html', {'active_tab': 'costs'})

def estimation(request):
    return render(request, 'estimation.html', {'active_tab': 'estimation'})

def reports(request):
    return render(request, 'reports.html', {'active_tab': 'reports'})
