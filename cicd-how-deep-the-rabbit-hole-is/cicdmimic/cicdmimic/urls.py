"""cicdmimic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from projects.views import IndexView, ProjectAddView, ProjectDetailView, BuildDetailView, BuildRunView, \
    EnvironmentVariableCreateView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('projects/add/', ProjectAddView.as_view(), name='project-add'),
    path('projects/<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('builds/<int:build_id>/', BuildDetailView.as_view(), name='build-detail'),
    path('builds/run/', BuildRunView.as_view(), name='build-run'),
    path('variables/add/', EnvironmentVariableCreateView.as_view(), name='variable-add'),
]
