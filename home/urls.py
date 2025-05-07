from django.urls import path
from .import views 
from .views import profile_update
from .views import criminals_list ,delete_criminal
from .views import custom_logout_view 
from .views import save_image
from django.conf import settings
from django.conf.urls.static import static
# from .views import find_similar_crimes
# If views are inside an app named 'home'
from home import views  # Make sure this reflects the actual location
from django.contrib.auth.decorators import login_required
from .views import edit_crime_person

urlpatterns = [

    path('edit/', views.profile_update, name='profile-update'),
    path('profile/', views.view_profile, name='profile'),
    path('', views.home, name='home'),
    path('crime/', views.crime_page, name='crime_list'),  
    path('criminals/', views.criminals_list, name='criminals_list'),
    path('crimes/', views.crime1_page, name='crimes'),
    path('camera/', views.camera_page, name='camerapage'),
    path('crimes/detectcrime/',views.detect_crime,name='detectcrime'),
    path('logout/', custom_logout_view, name='logout'),  
    path('delete_criminal/<int:criminal_id>/', views.delete_criminal, name='delete_criminal'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('stops_camera/', views.stops_camera, name='stops_camera'),  
    path('camera/open/', views.open_camera, name='open_camera'),
    path('camerafeed/<str:name>/', views.camera_feed, name='camerafeed'),
    path('register/person/', views.registers_person, name='register_person'),
    path('register/crime/<int:person_id>/', views.register_crime, name='register_crime'),
    path('crime/delete/<int:crime_id>/', views.delete_crime, name='delete_crime'),
    path('edit-person-list/', views.edit_person_list, name='edit_person_list'),  
    path('criminal/', views.criminal_list, name='criminal_list'),
    path('view-all-crimes/<int:criminal_id>/', views.view_all_crimes, name='view_all_crimes'),
    path('update-crime/<int:criminal_id>/', views.add_crime, name='update_crime'),
    path('criminal_details/<int:person_id>/', views.criminal_details, name='criminal_details'),
    path('crimes/view/<int:criminal_id>/', views.view_all_crimes, name='view_all_crimes'),
    path('crimes/updates/<int:criminal_id>/', views.add_crime, name='updates_crime'),
    path('save-image/', views.save_image, name='save_image'),
    path('crime-report/', views.crime_reporting, name='crime_report'),
    path('predict/', views.predict_page, name='predict_page'),
    path('edit/<int:id>/', views.edit_crime, name='edit_crime'),
    path('crime/edit/<int:crime_id>/', edit_crime_person, name='edit_crime_person'), 


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

