from django.urls import path,include
from.import views

urlpatterns = [
    path('',views.index,name="index"),
    path('register/',views.register,name="register"),
    path('login/',views.loginn,name="login"),
    path('home/', views.home, name="home"), 


    


    
   
]

 