from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate,login
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from .forms import CrimeRecordForm,PersonForm
from .models import CrimeRecord
from .models import Criminal
from django.urls import reverse
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import base64
import os
import json
from django.conf import settings
from django.http import JsonResponse
import base64
import os
from django.conf import settings
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.utils.timezone import now
import cv2
from django.shortcuts import render
from django.http import StreamingHttpResponse
import face_recognition
import os
import threading
import numpy as np
from django.urls import reverse
from .forms import PersonForm, CrimeForm  
from .models import Person
from .models import Crime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Crime, Person
from .forms import CrimeForm, PersonForm
from django.shortcuts import render, get_object_or_404
from .models import Criminal, Crime
from django.templatetags.static import static
import logging
from django.db.models import Count  
import pandas as pd
from django.http import JsonResponse
from .utils import load_data, preprocess_data, train_model as train_nn_model, load_saved_model,save_model, predict_and_decode_similar_crimes,generate_graph
import json
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from io import BytesIO
import io
import base64
from io import BytesIO
from sklearn.neighbors import NearestNeighbors
from .forms import CrimeForm
from django.views.decorators.http import require_POST
import logging
from .models import Crime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import logging
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.timezone import now


def loginn(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        print(f'Username: {username}, Password: {password}')
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            print("userlogin")
            
            loginn(request, user)
            messages.success(request, "Login successful")

            return redirect('home')
        else:
            return HttpResponse("Invalid Credentials")
      
    return render(request, 'login.html')

def view_profile(request):
    context={
        'user': request.user
    }
    return render(request,'profile.html',context)

@login_required
def profile_update(request):
      
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)  # Create a profile if missing
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect to the profile view
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        profile_picture_url = user.profile.profile_picture.url if user.profile.profile_picture else '/static/images/default-profile.png'
    
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_picture_url': profile_picture_url,  # Pass this to template
}
    return render(request, 'profile_edit.html', context)


def crime_page(request):
    crimes = Crime.objects.select_related('person').all()

    query = request.GET.get('search', '')  # Get the search query from the request
    if query:
        crimes = Crime.objects.filter(person__name__icontains=query)  # Filter crimes by person's name
    else:
        crimes = Crime.objects.all()  # Show all crimes if no query
    return render(request, 'crime_list.html', {'crimes': crimes})

def edit_crime(request, id):
    person = get_object_or_404(Person, id=id)
    # Handle profile picture URL
    if person.profile_picture and hasattr(person.profile_picture, 'url'):
        profile_picture_url = person.profile_picture.url
    else:
        profile_picture_url = '/static/images/default-profile.png'
    person_form = PersonForm(request.POST or None, request.FILES or None, instance=person)

    if request.method == 'POST':
        if person_form.is_valid():
            person_form.save()
            messages.success(request, 'Record has been updated successfully.')
            return redirect('edit_crime', id=person.id)  # Redirect to see updated data
        else:
            print(person_form.errors)  # Debug form errors if invalid

    return render(request, 'edit_crime_record.html', {
        'person_form': person_form,
        'person': person,
        'profile_picture_url': profile_picture_url,
    })


def edit_crime_person(request, crime_id):
    crime = get_object_or_404(Crime, id=crime_id)  # Fetch the crime object
    if request.method == "POST":
        form = CrimeForm(request.POST, instance=crime)
        if form.is_valid():
            form.save()
            return redirect('crime_list')  # Redirect to crime list after saving
    else:
        form = CrimeForm(instance=crime)  # Populate form with existing data
    return render(request, 'edit_crime.html', {'form': form})

def crime1_page(request):
    # Fetch the person or persons you want to display
    persons = Person.objects.all()  # You can modify this to filter as needed
    # Pass the persons to the template
    return render(request, 'crimes.html', {'persons': persons})

def criminals_list(request):
    crimes = Crime.objects.select_related('person').all()
    seen_names = set()
    unique_crimes = []

    for crime in crimes:
        if crime.person.name not in seen_names:
            seen_names.add(crime.person.name)
            unique_crimes.append(crime)

    return render(request, 'criminals_list.html', {'crimes': unique_crimes})

def delete_criminal(request, criminal_id):
    if request.method == 'POST':
        criminal = get_object_or_404(Criminal, id=criminal_id)
        criminal.delete()  # This will delete the entire record, including the image.
        messages.success(request, f"{criminal.name}'s record has been deleted.")
    return redirect('criminals_list')  # Redirect to the list of criminals after deletion

def custom_logout_view(request):
    logout(request)  
    return redirect('index')  

# View for Camera Page
def camera_page(request):
    return render(request, 'camerapage.html')

def open_camera(request):
    # This view simply renders the camera feed template.
    return render(request, 'camerafeed.html')

def camera_feed(request, name):
    person = get_object_or_404(Person, name=name)
    return render(request, 'camera_feed.html', {'id': person.id}) 


def predict_page(request):
    if request.method == 'POST':
        # Get the form values from the POST request
        time_occ = request.POST.get('TIME_OCC')
        area = request.POST.get('AREA')
        rpt_dist_no = request.POST.get('Rpt_Dist_No')
        vict_age = request.POST.get('Vict_Age')
        premis_cd = request.POST.get('Premis_Cd')
        weapon_used_cd = request.POST.get('Weapon_Used_Cd')
        lat = request.POST.get('LAT')
        lon = request.POST.get('LON')

        # Print the values to the console (or server logs)
        print("Time Occurred:", time_occ)
        print("Area:", area)
        print("Report District Number:", rpt_dist_no)
        print("Victim Age:", vict_age)
        print("Premises Code:", premis_cd)
        print("Weapon Used Code:", weapon_used_cd)
        print("Latitude:", lat)
        print("Longitude:", lon)

        df = load_data()
        df,_ ,_,_= preprocess_data(df)
        model, scaler, label_encoders = load_saved_model()

        new_crime = {
            'TIME OCC': time_occ,
            'AREA': area,
            'Rpt Dist No': rpt_dist_no,
            'Vict Age': vict_age,
            'Premis Cd': premis_cd,
            'Weapon Used Cd': weapon_used_cd,
            'LAT': lat,
            'LON': lon
        }

        data=predict_and_decode_similar_crimes(new_crime, df, model, scaler, label_encoders)
        context = {
            'time_occs': sorted(df['TIME OCC'].unique()),
            'areas': sorted(df['AREA'].unique()),
            'report_districts': sorted(df['Rpt Dist No'].unique()),
            'victim_ages': sorted(df['Vict Age'].unique()),
            'premises_codes': sorted(df['Premis Cd'].unique()),
            'weapon_used_codes': sorted(df['Weapon Used Cd'].unique()),
            'default_lat': 34.2464,
            'default_lon': -118.6091,
            'similar_crimes_df': data.to_html(classes='crime-results-table', index=False)  # Rendered as an HTML table
        }

        return render(request, 'predict.html', context)
    
    df = load_data()
    df,_ ,_,_= preprocess_data(df)

    # Extract unique values for dropdowns
    context = {
        'time_occs': sorted(df['TIME OCC'].unique()),
        'areas': sorted(df['AREA'].unique()),
        'report_districts': sorted(df['Rpt Dist No'].unique()),
        'victim_ages': sorted(df['Vict Age'].unique()),
        'premises_codes': sorted(df['Premis Cd'].unique()),
        'weapon_used_codes': sorted(df['Weapon Used Cd'].unique()),
        'default_lat': 34.2464,  # Default latitude
        'default_lon': -118.6091,  # Default longitude
    }
    return render(request, 'predict.html', context)


def home(request):
    return render(request,'home.html')

# Reference to the global video capture
video_capture = cv2.VideoCapture(0)

def stop_camera(request):
    global video_capture
    if video_capture.isOpened():
        video_capture.release()
        cv2.destroyAllWindows()
    return JsonResponse({"status": "Camera stopped"})

#face detection
@csrf_exempt
def stops_camera(request):
    if request.method == 'POST':
        # Example: Stop any ongoing video stream or camera process
        return JsonResponse({'status': 'Camera stopped'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

logger = logging.getLogger(__name__)
def save_image(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            person_id = data.get('person_id')
         
            image_data = data.get('image')
            logger.debug(f"Received data - person_id: {person_id}, image_data: {len(image_data) if image_data else 'None'}")
           
            if not person_id:
                return JsonResponse({'success': False, 'error': 'Person ID is missing.'})
            if not image_data:
                return JsonResponse({'success': False, 'error': 'Image data is missing.'})

            # Decode the Base64 image data
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]  # Extract file extension
            decoded_image = ContentFile(base64.b64decode(imgstr), name=f'{person_id}.{ext}')

            # Fetch the person object and update the profile picture
            person = get_object_or_404(Person, id=person_id)
            person.profile_picture = decoded_image
            person.save()

            print(person.profile_picture.url)
            print(person.profile_picture.path)  # To check the file system path

            if person.profile_picture:  
                logger.info(f"Profile picture updated for person_id: {person_id}")
            else:
                logger.warning("Profile picture is not saved!")
            return JsonResponse({'success': True, 'message': 'Image saved successfully!'})

        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def registers_person(request):
    if request.method == 'POST':
        person_form = PersonForm(request.POST)
        if person_form.is_valid():
            person = person_form.save()
            print(f"Redirecting to register_crime with person_id: {person.id}")
            return redirect('register_crime', person_id=person.id)
    else:
        person_form = PersonForm()
    return render(request, 'registers_person.html', {'person_form': person_form})


def register_crime(request, person_id):
    person = get_object_or_404(Person, id=person_id)

    if request.method == 'POST':
        crime_form = CrimeForm(request.POST)
        if crime_form.is_valid():
            crime = crime_form.save(commit=False)
            crime.person = person  # Link the crime to the person
            crime.save()
            return redirect('home')  # Ensure 'home' URL is defined in urls.py
        else:
            print("Form errors:", crime_form.errors)
    else:
        crime_form = CrimeForm()
    return render(request, 'register_crime.html', {'crime_form': crime_form, 'person': person})

# View to handle crime deletion
def delete_crime(request, crime_id):
    # Fetch the Crime instance to be deleted
    crime = get_object_or_404(Crime, id=crime_id)
    
    if request.method == "POST":
        # Delete the crime record
        crime.delete()
        # Redirect to the crime list page after deletion
        return redirect('crime_list')  

    # If not a POST request, redirect back (not typical for delete)
    return redirect('crime_list')  # Adjust as needed


def edit_person_list(request):
    persons = Person.objects.all()
    for person in persons:
        if not person.profile_picture:
            c=person.profile_picture_url = static('images/default-profile.png')
        else:
            c=person.profile_picture_url = person.profile_picture.url
    return render(request, 'edit_person_list.html', {'persons': persons})


def criminal_list(request):
    search_query = request.GET.get('search', '')  # Get the search term from the query parameters
    if search_query:
        # If there's a search query, filter by name and remove duplicates (if any)
        criminals = Person.objects.filter(name__icontains=search_query).distinct()
    else:
        # If no search query, show all criminals and remove duplicates
        criminals = Person.objects.all().distinct()
    return render(request, 'criminal_list.html', {'criminals': criminals})


def view_all_crimes(request, criminal_id):
    # Fetch the person and their crimes
    person = get_object_or_404(Person, pk=criminal_id)
    crimes = person.crimes.all()  # Use related_name from the Crime model

    print(f"Viewing all crimes for person with ID: {criminal_id}")
    return render(request, 'view_all_crimes.html', {'criminal': person, 'crimes': crimes})


def add_crime(request, criminal_id):
    # Fetch the person (formerly criminal) and their associated crimes
    person = get_object_or_404(Person, pk=criminal_id)
    crimes = person.crimes.all()  # Use related_name from the Crime model

    if request.method == 'POST':
        # Handle form submission for updating the crime
        form = CrimeForm(request.POST)
        if form.is_valid():
            # Save or update the crime record
            crime = form.save(commit=False)
            crime.person = person  # Link crime to this specific person
            crime.save()
            return redirect('view_all_crimes', criminal_id=person.id)  # Redirect to the crimes list
    else:
        form = CrimeForm()  # Create an empty form for new crime
    return render(request, 'add_crime.html', {'form': form, 'criminal': person})

def criminal_details(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    return render(request, 'criminal_details.html', {'person': person})

def crime_reporting(request):
    # You can pass any context data here if needed
    return render(request, 'crime_reporting.html')


def detect_crime(request):
    message = None  # Default message is None
    print("detect_crime function called")  # Debug print

    if request.method == 'POST':
        action = request.POST.get('action')  # Get which button was clicked
        print(f"Received POST request with action: {action}")  # Debug print

        if action == 'train':
            try:
                print("Starting model training...")  # Debug print
                df = load_data()
                print("Data loaded successfully.")  # Debug print

                df, X_scaled, scaler, label_encoders = preprocess_data(df)
                print("Data preprocessing completed.")  # Debug print

                nn_model = train_nn_model(X_scaled)
                print("Model training completed.")  # Debug print

                save_model(nn_model, scaler, label_encoders)
                print("Model saved successfully.")  # Debug print

                message = "Model has been trained successfully."
            except Exception as e:
                print(f"Error during training: {e}")  # Debug print
                message = f"An error occurred while training the model: {str(e)}"

        elif action == 'load_model':
            try:
                print("Loading saved model...")  # Debug print
                model, scaler, label_encoders = load_saved_model()  # Assume load_saved_model is implemented

                if model:
                    print("Model loaded successfully.")  # Debug print
                    message = "Model has been loaded successfully."
                else:
                    print("Model loading failed.")  # Debug print
                    message = "Model loading failed."
            except Exception as e:
                print(f"Error while loading model: {e}")  # Debug print
                message = f"An error occurred while loading the model: {str(e)}"

        elif action == 'predict':
            try:
                print("Redirecting to prediction page...")  # Debug print
                return redirect('predict_page')
            except Exception as e:
                print(f"Error while redirecting: {e}")  # Debug print
                message = f"An error occurred while redirecting to prediction: {str(e)}"

        elif action == 'show_graph':
            try:
                graph_type = request.POST.get('graph_type')  # Get the graph type to generate
                print(f"Generating graph: {graph_type}")  # Debug print
                df = load_data()  # Load data for visualization
                graph_url = generate_graph(df, graph_type)
                print("Graph generated successfully.")  # Debug print
                return JsonResponse({'graph_url': graph_url})
            except Exception as e:
                print(f"Error while generating graph: {e}")  # Debug print
                return JsonResponse({'message': f"An error occurred while generating the graph: {str(e)}"})

        print(f"Returning JSON response with message: {message}")  # Debug print
        return JsonResponse({'message': message})

    print("Rendering detectcrime.html template")  # Debug print
    return render(request, 'detectcrime.html', {'message': message})


