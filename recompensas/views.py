from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from familia.views import crianca_obrigatoria, responsavel_obrigatorio
from .forms import RecompensaForm
from .models import Recompensa, Resgate
from .services import saldo_da_crianca


@responsavel_obrigatorio
def nova_recompensa(request):
    return render(request, 'familia/formulario.html', {'form': RecompensaForm(), 'titulo': 'Criar recompensa', 'voltar': 'painel_responsavel', 'acao': 'criar_recompensa'})


@responsavel_obrigatorio
@require_POST
def criar_recompensa(request):
    form = RecompensaForm(request.POST)
    if form.is_valid():
        recompensa = form.save(commit=False)
        recompensa.familia = request.user.perfil.familia
        recompensa.save()
        messages.success(request, 'Recompensa cadastrada.')
    else:
        messages.error(request, 'Confira o nome e o custo em pontos.')
    return redirect('/responsavel/#tab-premios')


@crianca_obrigatoria
@require_POST
def resgatar(request):
    perfil = request.user.perfil
    try:
        recompensa = Recompensa.objects.get(pk=request.POST.get('recompensa_id'), familia=perfil.familia, ativa=True)
    except (Recompensa.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Essa recompensa não está disponível.')
        return redirect('painel_crianca')
    with transaction.atomic():
        saldo = saldo_da_crianca(perfil)
        if saldo < recompensa.custo:
            messages.error(request, 'Ainda faltam pontos para esse prêmio. Continue fazendo tarefas!')
        else:
            Resgate.objects.create(familia=perfil.familia, crianca=perfil, recompensa=recompensa, custo_pago=recompensa.custo)
            messages.success(request, f'Oba! Você trocou seus pontos por: {recompensa.nome}.')
    return redirect('painel_crianca')
