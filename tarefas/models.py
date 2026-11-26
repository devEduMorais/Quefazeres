from django.db import models

# Create your models here.
from django.db import models
from familia.models import Familia, Perfil


class Tarefa(models.Model):
    DISPONIVEL = 'disponivel'
    PENDENTE = 'pendente'
    CONCLUIDA = 'concluida'
    ESTADOS = [(DISPONIVEL, 'Disponível'), (PENDENTE, 'Pendente'), (CONCLUIDA, 'Concluída')]
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='tarefas')
    crianca = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='tarefas')
    descricao = models.CharField(max_length=200)
    pontos = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=DISPONIVEL)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['estado', '-criada_em']

    def __str__(self):
        return self.descricao

    @property
    def envio_atual(self):
        return self.envios.order_by('-enviado_em').first()


class Envio(models.Model):
    PENDENTE = 'pendente'
    APROVADO = 'aprovado'
    REPROVADO = 'reprovado'
    ESTADOS = [(PENDENTE, 'Pendente'), (APROVADO, 'Aprovado'), (REPROVADO, 'Reprovado')]
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE, related_name='envios')
    foto = models.FileField(upload_to='comprovantes/%Y/%m/')
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDENTE)
    enviado_em = models.DateTimeField(auto_now_add=True)
    analisado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-enviado_em']
