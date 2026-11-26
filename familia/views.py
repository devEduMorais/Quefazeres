from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST
from .forms import CadastroResponsavelForm, CriarCriancaForm, EditarCriancaForm, EditarFamiliaForm
from .models import Familia, Perfil


def inicio(request):
    if not request.user.is_authenticated:
        return redirect('entrar')
    perfil = getattr(request.user, 'perfil', None)
    if perfil is None:
        # Conta sem perfil (ex.: superusuário do /admin/). Evita o ciclo inicio <-> entrar.
        if request.user.is_staff:
            return redirect('admin:index')
        logout(request)
        messages.error(request, 'Esta conta não está ligada a uma família. Entre com outra conta.')
        return redirect('entrar')
    return redirect('painel_responsavel' if perfil.papel == Perfil.RESPONSAVEL else 'painel_crianca')


@require_http_methods(['GET', 'POST'])
def cadastro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    form = CadastroResponsavelForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            familia = Familia.objects.create(sobrenome=form.cleaned_data['sobrenome_familia'])
            usuario = User.objects.create_user(form.cleaned_data['nome_usuario'], password=form.cleaned_data['senha'], email=form.cleaned_data['email'])
            Perfil.objects.create(usuario=usuario, familia=familia, papel=Perfil.RESPONSAVEL, nome_completo=form.cleaned_data['nome_completo'], celular=form.cleaned_data['celular'])
        login(request, usuario)
        return redirect('painel_responsavel')
    return render(request, 'familia/formulario.html', {'form': form, 'titulo': 'Criar família e responsável', 'voltar': 'entrar'})


@require_http_methods(['GET', 'POST'])
def entrar(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    erro = None
    if request.method == 'POST':
        usuario = authenticate(request, username=request.POST.get('nome_usuario', ''), password=request.POST.get('senha', ''))
        if usuario and getattr(getattr(usuario, 'perfil', None), 'ativo', True):
            login(request, usuario)
            return redirect('inicio')
        erro = 'Usuário ou senha inválidos.'
    return render(request, 'familia/entrar.html', {'erro': erro})


@require_POST
@login_required
def sair(request):
    logout(request)
    return redirect('entrar')


def com_papel(papel):
    def decorator(view):
        from functools import wraps
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            perfil = getattr(request.user, 'perfil', None)
            if perfil is None or perfil.papel != papel or (papel == Perfil.CRIANCA and not perfil.ativo):
                if perfil and perfil.papel == Perfil.CRIANCA and not perfil.ativo:
                    logout(request)
                messages.error(request, 'Você não tem permissão para acessar essa página.')
                return redirect('inicio')
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


responsavel_obrigatorio = com_papel(Perfil.RESPONSAVEL)
crianca_obrigatoria = com_papel(Perfil.CRIANCA)


@responsavel_obrigatorio
def painel_responsavel(request):
    perfil = request.user.perfil
    from tarefas.models import Tarefa, Envio
    from recompensas.models import Recompensa, Resgate
    criancas = list(Perfil.objects.filter(familia=perfil.familia, papel=Perfil.CRIANCA, ativo=True).select_related('usuario'))
    criancas_inativas = Perfil.objects.filter(familia=perfil.familia, papel=Perfil.CRIANCA, ativo=False).select_related('usuario')
    tarefas = Tarefa.objects.filter(familia=perfil.familia).select_related('crianca__usuario')
    envios = Envio.objects.filter(tarefa__familia=perfil.familia, estado=Envio.PENDENTE).select_related('tarefa', 'tarefa__crianca__usuario')
    recompensas = Recompensa.objects.filter(familia=perfil.familia, ativa=True)
    resgates = Resgate.objects.filter(familia=perfil.familia).select_related('crianca__usuario', 'recompensa')[:10]
    tarefas_historico = tarefas.exclude(estado=Tarefa.DISPONIVEL)
    from recompensas.services import saldo_da_crianca
    for crianca in criancas:
        crianca.saldo = saldo_da_crianca(crianca)
    from tarefas.forms import TarefaForm
    from recompensas.forms import RecompensaForm
    familia_form = EditarFamiliaForm(instance=perfil.familia)
    tarefa_form = TarefaForm(familia=perfil.familia)
    recompensa_form = RecompensaForm()
    return render(request, 'familia/painel_responsavel.html', {'perfil': perfil, 'criancas': criancas, 'criancas_inativas': criancas_inativas, 'tarefas': tarefas, 'tarefas_abertas': tarefas.exclude(estado=Tarefa.CONCLUIDA).count(), 'tarefas_historico': tarefas_historico, 'envios': envios, 'recompensas': recompensas, 'resgates': resgates, 'familia_form': familia_form, 'tarefa_form': tarefa_form, 'recompensa_form': recompensa_form})


@crianca_obrigatoria
def painel_crianca(request):
    perfil = request.user.perfil
    from tarefas.models import Tarefa
    from recompensas.models import Recompensa, Resgate
    from recompensas.services import saldo_da_crianca
    tarefas = Tarefa.objects.filter(crianca=perfil)
    saldo = saldo_da_crianca(perfil)
    recompensas = list(Recompensa.objects.filter(familia=perfil.familia, ativa=True).order_by('custo'))
    for recompensa in recompensas:
        recompensa.falta = max(recompensa.custo - saldo, 0)
        recompensa.progresso = min(100, max(0, saldo) * 100 // recompensa.custo) if recompensa.custo else 100
    resgates = Resgate.objects.filter(crianca=perfil).select_related('recompensa')[:10]
    # Apenas para exibição: barra "X de Y tarefas feitas".
    tarefas_total = tarefas.count()
    tarefas_feitas = tarefas.filter(estado=Tarefa.CONCLUIDA).count()
    progresso_tarefas = tarefas_feitas * 100 // tarefas_total if tarefas_total else 0
    return render(request, 'familia/painel_crianca.html', {'perfil': perfil, 'tarefas': tarefas, 'recompensas': recompensas, 'resgates': resgates, 'saldo': saldo, 'tarefas_total': tarefas_total, 'tarefas_feitas': tarefas_feitas, 'progresso_tarefas': progresso_tarefas})


@responsavel_obrigatorio
@require_http_methods(['GET', 'POST'])
def nova_crianca(request):
    form = CriarCriancaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            usuario = User.objects.create_user(form.cleaned_data['nome_usuario'], password=form.cleaned_data['senha'])
            Perfil.objects.create(usuario=usuario, familia=request.user.perfil.familia, papel=Perfil.CRIANCA, nome_completo=form.cleaned_data['nome_completo'])
        messages.success(request, f'Conta criada para {form.cleaned_data["nome_completo"]}. Entregue o usuário e a senha à criança.')
        return redirect('/responsavel/#tab-familia')
    return render(request, 'familia/formulario.html', {'form': form, 'titulo': 'Criar conta da criança', 'voltar': 'painel_responsavel'})


@responsavel_obrigatorio
@require_http_methods(['GET', 'POST'])
def editar_crianca(request, perfil_id):
    crianca = get_object_or_404(Perfil, pk=perfil_id, familia=request.user.perfil.familia, papel=Perfil.CRIANCA)
    form = EditarCriancaForm(request.POST or None, instance=crianca)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil da criança atualizado.')
        return redirect('/responsavel/#tab-familia')
    return render(request, 'familia/formulario.html', {'form': form, 'titulo': 'Editar criança', 'voltar': 'painel_responsavel'})


@responsavel_obrigatorio
@require_POST
def alternar_crianca(request, perfil_id):
    crianca = get_object_or_404(Perfil, pk=perfil_id, familia=request.user.perfil.familia, papel=Perfil.CRIANCA)
    crianca.ativo = not crianca.ativo
    crianca.save(update_fields=['ativo'])
    messages.success(request, 'Conta da criança ativada.' if crianca.ativo else 'Conta da criança desativada.')
    return redirect('/responsavel/#tab-familia')


@responsavel_obrigatorio
@require_POST
def editar_familia(request):
    familia = request.user.perfil.familia
    form = EditarFamiliaForm(request.POST, instance=familia)
    if form.is_valid():
        form.save()
        messages.success(request, 'Perfil da família atualizado.')
    else:
        messages.error(request, 'Informe um nome válido para a família.')
    return redirect('/responsavel/#tab-familia')
