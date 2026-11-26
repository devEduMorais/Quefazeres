from django.db.models import Sum
from tarefas.models import Tarefa
from .models import Resgate


def saldo_da_crianca(crianca):
    ganhos = Tarefa.objects.filter(crianca=crianca, estado=Tarefa.CONCLUIDA).aggregate(total=Sum('pontos'))['total'] or 0
    gastos = Resgate.objects.filter(crianca=crianca).aggregate(total=Sum('custo_pago'))['total'] or 0
    return ganhos - gastos
