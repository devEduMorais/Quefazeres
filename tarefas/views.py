from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from familia.views import crianca_obrigatoria, responsavel_obrigatorio
from .forms import TarefaForm, EnvioForm
from .models import Tarefa, Envio


@responsavel_obrigatorio
def nova_tarefa(request):
    form = TarefaForm(familia=request.user.perfil.familia)
    return render(request, 'familia/formulario.html', {'form': form, 'titulo': 'Criar atividade', 'voltar': 'painel_responsavel', 'acao': 'criar_tarefa'})


@responsavel_obrigatorio
@require_POST
def criar_tarefa(request):
    form = TarefaForm(request.POST, familia=request.user.perfil.familia)
    if form.is_valid():
        tarefa = form.save(commit=False)
        tarefa.familia = request.user.perfil.familia
        tarefa.save()
        messages.success(request, 'Atividade designada para a criança.')
    else:
        messages.error(request, 'Não foi possível criar a atividade. Confira os dados e cadastre uma criança primeiro.')
    return redirect('/responsavel/#tab-tarefas')


@crianca_obrigatoria
@require_POST
def enviar_tarefa(request):
    form = EnvioForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, 'Envie uma foto válida para comprovar a atividade.')
        return redirect('painel_crianca')
    tarefa = get_object_or_404(Tarefa, pk=form.cleaned_data['tarefa_id'], crianca=request.user.perfil, estado=Tarefa.DISPONIVEL)
    Envio.objects.create(tarefa=tarefa, foto=form.cleaned_data['foto'])
    tarefa.estado = Tarefa.PENDENTE
    tarefa.save(update_fields=['estado'])
    messages.success(request, 'Foto enviada para análise do responsável.')
    return redirect('painel_crianca')


@responsavel_obrigatorio
def analise(request):
    envios = Envio.objects.filter(tarefa__familia=request.user.perfil.familia, estado=Envio.PENDENTE).select_related('tarefa', 'tarefa__crianca__usuario')
    return render(request, 'familia/analises.html', {'envios': envios})


@responsavel_obrigatorio
@require_POST
def aprovar(request):
    with transaction.atomic():
        envio = get_object_or_404(Envio, pk=request.POST.get('envio_id'), tarefa__familia=request.user.perfil.familia, estado=Envio.PENDENTE)
        envio.estado = Envio.APROVADO
        envio.analisado_em = timezone.now()
        envio.save(update_fields=['estado', 'analisado_em'])
        envio.tarefa.estado = Tarefa.CONCLUIDA
        envio.tarefa.save(update_fields=['estado'])
    messages.success(request, f'Atividade aprovada. {envio.tarefa.pontos} pontos creditados.')
    return redirect('/responsavel/#tab-analises')


@responsavel_obrigatorio
@require_POST
def reprovar(request):
    with transaction.atomic():
        envio = get_object_or_404(Envio, pk=request.POST.get('envio_id'), tarefa__familia=request.user.perfil.familia, estado=Envio.PENDENTE)
        envio.estado = Envio.REPROVADO
        envio.analisado_em = timezone.now()
        envio.save(update_fields=['estado', 'analisado_em'])
        envio.tarefa.estado = Tarefa.DISPONIVEL
        envio.tarefa.save(update_fields=['estado'])
    messages.info(request, 'Envio reprovado. A atividade está disponível para nova tentativa.')
    return redirect('/responsavel/#tab-analises')
