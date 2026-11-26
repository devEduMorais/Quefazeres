from django.urls import path
from . import views

urlpatterns = [
    path('nova/', views.nova_recompensa, name='nova_recompensa'),
    path('criar/', views.criar_recompensa, name='criar_recompensa'),
    path('resgatar/', views.resgatar, name='resgatar'),
]
