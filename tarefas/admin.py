from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Tarefa, Envio

admin.site.register(Tarefa)
admin.site.register(Envio)
