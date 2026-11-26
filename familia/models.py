from django.db import models

# Create your models here.
import uuid
from django.conf import settings
from django.db import models


class Familia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sobrenome = models.CharField(max_length=100)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sobrenome} ({self.id})'


class Perfil(models.Model):
    RESPONSAVEL = 'responsavel'
    CRIANCA = 'crianca'
    PAPEIS = [(RESPONSAVEL, 'Responsável'), (CRIANCA, 'Criança')]
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='perfis')
    papel = models.CharField(max_length=20, choices=PAPEIS)
    nome_completo = models.CharField(max_length=200, blank=True)
    celular = models.CharField(max_length=16, blank=True)
    ativo = models.BooleanField(default=True)

    @property
    def nome_exibicao(self):
        return self.nome_completo or self.usuario.get_full_name() or self.usuario.username

    def __str__(self):
        return f'{self.usuario.username} - {self.get_papel_display()}'
