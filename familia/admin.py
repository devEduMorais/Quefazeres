from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Familia, Perfil

admin.site.register(Familia)
admin.site.register(Perfil)
