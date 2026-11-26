from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Recompensa, Resgate

admin.site.register(Recompensa)
admin.site.register(Resgate)
