from django.contrib import admin
from.models import SiteUsers,CrimeRecord,Crime
from.models import Criminal,Person,Profile

# Register your models here.

# admin.site.register(SiteUsers)
# admin.site.register(CrimeRecord)
# admin.site.register(Criminal)
admin.site.register(Person)
admin.site.register(Crime)
admin.site.register(Profile)




