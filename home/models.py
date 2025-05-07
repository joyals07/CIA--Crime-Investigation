from django.db import models
from django.contrib.auth.models import User
from django.db import models
import numpy as np
import pickle
from django.db import models
from django.contrib.postgres.fields import ArrayField  # Use JSONField if needed
from datetime import date
from django.contrib.auth import get_user_model

class SiteUsers(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    date_of_birth =models.DateField()
    profile_picture=models.ImageField(default=',default_profile_picture.jpg',upload_to='profile_pictures')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=20, blank=True)
    gender =models.CharField(max_length=20,blank=True)

    profile_picture = models.FileField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True, 
        default='profile_pictures/default-profile.png'
    )

    def __str__(self):
        return f'{self.user.username} Profile'


class Person(models.Model):
    name = models.CharField(max_length=255,default="")
    age = models.IntegerField(default=0)  # Set a default value for age
    address = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True, null=True)
    date_registered = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name



class Criminal(models.Model):
    name = models.CharField(max_length=255, default='Unknown')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='criminal_records')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)


    def __str__(self):
        return f"Criminal: {self.person.name}"


class Crime(models.Model):
    CRIME_TYPES = [
        ('theft', 'Theft'),
        ('assault', 'Assault'),
        ('fraud', 'Fraud'),
        ('vandalism', 'Vandalism'),
        ('murder','Murder'),
        ('cybercrime','Cybercrime'),
        ('other', 'Other'),
    ]
    crime_type = models.CharField(max_length=50, choices=CRIME_TYPES)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='crimes', null=True, blank=True)
    description = models.TextField()
    date_committed = models.DateField()
    location = models.CharField(max_length=255, default="Unknown Location")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.crime_type} committed by {self.person}"
    


class CrimeRecord(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True) 
    number_of_crimes = models.IntegerField()
    crimes_done = models.TextField()
    date_committed = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.person.name} - {self.number_of_crimes} crimes"
    












