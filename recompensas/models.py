from django.db import models
from familia.models import Familia, Perfil


class Recompensa(models.Model):
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='recompensas')
    nome = models.CharField(max_length=120)
    custo = models.PositiveIntegerField()
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nome} ({self.custo} pontos)'


class Resgate(models.Model):
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='resgates')
    crianca = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='resgates')
    recompensa = models.ForeignKey(Recompensa, on_delete=models.PROTECT, related_name='resgates')
    custo_pago = models.PositiveIntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
