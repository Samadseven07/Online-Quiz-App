from django.urls import path
from .views import howe_page

urlpatterns = [
    path("", howe_page, name= "home")
]
