"""
URL configuration for ocr_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from . import views

urlpatterns = [
    path("ocr/", views.ocr_job, name="ocr-process-file"),
    path("ocr/<str:job_id>/", views.ocr_result, name="ocr-get-result"),
    path("", views.health_check, name="health-check"),
    path("ocr/abort/<str:task_id>/", views.abort_task, name="abort-task"),  # Cancel an OCR job
]
