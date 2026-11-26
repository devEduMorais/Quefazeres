"""Cria dados de demonstração para apresentar o Quefazeres.

Uso:  python manage.py demo
O comando não apaga nada. Se a família de demonstração já existir, ele avisa e para.
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from familia.models import Familia, Perfil
from recompensas.models import Recompensa, Resgate
from tarefas.models import Envio, Tarefa

SENHA_DEMO = 'demo12345'
USUARIOS = ('responsavel.demo', 'ana.demo', 'pedro.demo')


class Command(BaseCommand):
    help = 'Cria uma família de demonstração com crianças, tarefas, prêmios e envios.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Apaga SOMENTE a família de demonstração (contas *.demo e seus dados) e recria tudo.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self._apagar_demo()
        if User.objects.filter(username__in=USUARIOS).exists():
            self.stdout.write(self.style.WARNING('Os dados de demonstração já existem. Nada foi alterado.'))
            self._credenciais()
            return

        with transaction.atomic():
            familia = Familia.objects.create(sobrenome='Silva')
            resp = self._perfil('responsavel.demo', familia, Perfil.RESPONSAVEL, 'Maria Silva', celular='(62) 99999-0000')
            ana = self._perfil('ana.demo', familia, Perfil.CRIANCA, 'Ana Silva')
            pedro = self._perfil('pedro.demo', familia, Perfil.CRIANCA, 'Pedro Silva')

            # Tarefas concluídas (geram saldo)
            for crianca, descricao, pontos in [(ana, 'Escovar os dentes', 5), (ana, 'Arrumar a cama', 10), (pedro, 'Guardar os brinquedos', 8)]:
                tarefa = Tarefa.objects.create(familia=familia, crianca=crianca, descricao=descricao, pontos=pontos, estado=Tarefa.CONCLUIDA)
                self._envio(tarefa, 'escovar-dentes.png' if 'dente' in descricao else 'arrumar-cama.png' if 'cama' in descricao else 'brinquedos.png', Envio.APROVADO)

            # Tarefa pendente de análise (aparece em Análises)
            pendente = Tarefa.objects.create(familia=familia, crianca=ana, descricao='Organizar o quarto', pontos=15, estado=Tarefa.PENDENTE)
            self._envio(pendente, 'organizar-quarto.png', Envio.PENDENTE)

            # Tarefas disponíveis
            Tarefa.objects.create(familia=familia, crianca=ana, descricao='Guardar os brinquedos', pontos=8)
            Tarefa.objects.create(familia=familia, crianca=pedro, descricao='Arrumar a cama', pontos=10)
            Tarefa.objects.create(familia=familia, crianca=pedro, descricao='Lavar a louça', pontos=7)

            # Prêmios
            balinha = Recompensa.objects.create(familia=familia, nome='Balinha', custo=5)
            Recompensa.objects.create(familia=familia, nome='Pirulito', custo=10)
            Recompensa.objects.create(familia=familia, nome='1 hora de TV', custo=20)
            Recompensa.objects.create(familia=familia, nome='Videogame no fim de semana', custo=30)

            # Um resgate já feito
            Resgate.objects.create(familia=familia, crianca=ana, recompensa=balinha, custo_pago=balinha.custo)

        self.stdout.write(self.style.SUCCESS('Dados de demonstração criados.'))
        self._credenciais()

    def _apagar_demo(self):
        """Remove apenas as famílias que contêm contas de demonstração."""
        familias = Familia.objects.filter(perfis__usuario__username__in=USUARIOS).distinct()
        outros = Perfil.objects.filter(familia__in=familias).exclude(usuario__username__in=USUARIOS)
        if outros.exists():
            self.stdout.write(self.style.ERROR('A família de demonstração tem contas que não são de demonstração. Nada foi apagado.'))
            raise SystemExit(1)
        with transaction.atomic():
            fotos = [e.foto for e in Envio.objects.filter(tarefa__familia__in=familias)]
            # Resgates primeiro: Resgate -> Recompensa usa PROTECT para preservar o histórico.
            Resgate.objects.filter(familia__in=familias).delete()
            familias.delete()  # remove perfis, tarefas, envios e prêmios da família
            User.objects.filter(username__in=USUARIOS).delete()
        for foto in fotos:
            if foto.name.rsplit('/', 1)[-1].startswith('demo-'):
                foto.storage.delete(foto.name)
        self.stdout.write(self.style.WARNING('Dados de demonstração anteriores removidos.'))

    def _perfil(self, username, familia, papel, nome, celular=''):
        usuario = User.objects.create_user(username, password=SENHA_DEMO)
        return Perfil.objects.create(usuario=usuario, familia=familia, papel=papel, nome_completo=nome, celular=celular)

    def _envio(self, tarefa, arte, estado):
        caminho = settings.BASE_DIR / 'static' / 'familia' / 'arte' / arte
        with caminho.open('rb') as arquivo:
            envio = Envio(tarefa=tarefa, estado=estado)
            if estado != Envio.PENDENTE:
                envio.analisado_em = timezone.now()
            envio.foto.save(f'demo-{arte}', File(arquivo), save=False)
            envio.save()

    def _credenciais(self):
        self.stdout.write('')
        self.stdout.write('Contas de demonstração (senha de todas: %s):' % SENHA_DEMO)
        self.stdout.write('  Responsável: responsavel.demo')
        self.stdout.write('  Criança:     ana.demo  (saldo 10 pontos, 1 envio pendente)')
        self.stdout.write('  Criança:     pedro.demo  (saldo 8 pontos)')
