from django.urls import path
from .views import recognize_face,stream,stop_camera

urlpatterns = [
    path('camera/recognize/', recognize_face, name='recognize_face'),
    path('stream/', stream, name='stream'),
    path('stop_camera/', stop_camera, name='stop_camera'),

   
]

