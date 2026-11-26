"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from familia import views as familia_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', familia_views.inicio, name='inicio'),
    path('cadastro/', familia_views.cadastro, name='cadastro'),
    path('entrar/', familia_views.entrar, name='entrar'),
    path('sair/', familia_views.sair, name='sair'),
    path('responsavel/', familia_views.painel_responsavel, name='painel_responsavel'),
    path('crianca/', familia_views.painel_crianca, name='painel_crianca'),
    path('criancas/nova/', familia_views.nova_crianca, name='nova_crianca'),
    path('criancas/<int:perfil_id>/editar/', familia_views.editar_crianca, name='editar_crianca'),
    path('criancas/<int:perfil_id>/alternar/', familia_views.alternar_crianca, name='alternar_crianca'),
    path('familia/editar/', familia_views.editar_familia, name='editar_familia'),
    path('tarefas/', include('tarefas.urls')),
    path('recompensas/', include('recompensas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
