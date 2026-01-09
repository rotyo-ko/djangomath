from django.urls import path, include

from . import views

app_name = "mymath"

urlpatterns = [
    path("", views.index, name="index"),
    path("exam/<int:exam_id>/<int:number>/", views.exam, name="exam"),    
    path("exam/<int:exam_id>/<int:number>/answer/", views.answer, name="answer"),
    path("exam/<int:exam_id>/result/", views.result, name="result"),
]