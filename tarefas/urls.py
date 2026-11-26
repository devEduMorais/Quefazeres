from django.urls import path
from . import views

urlpatterns = [
    path('nova/', views.nova_tarefa, name='nova_tarefa'),
    path('criar/', views.criar_tarefa, name='criar_tarefa'),
    path('enviar/', views.enviar_tarefa, name='enviar_tarefa'),
    path('analise/', views.analise, name='analise'),
    path('aprovar/', views.aprovar, name='aprovar_tarefa'),
    path('reprovar/', views.reprovar, name='reprovar_tarefa'),
]
