import tempfile
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from recompensas.services import saldo_da_crianca
from tarefas.models import Envio, Tarefa
from .models import Familia, Perfil


class PainelResponsavelTests(TestCase):
    def setUp(self):
        self.familia = Familia.objects.create(sobrenome='Morais')
        self.responsavel = User.objects.create_user('responsavel', password='Senha-forte-123')
        Perfil.objects.create(usuario=self.responsavel, familia=self.familia, papel=Perfil.RESPONSAVEL)
        self.crianca_user = User.objects.create_user('crianca', password='Senha-forte-123')
        self.crianca = Perfil.objects.create(usuario=self.crianca_user, familia=self.familia, papel=Perfil.CRIANCA, nome_completo='Criança')
        self.client.login(username='responsavel', password='Senha-forte-123')

    def test_painel_contem_quatro_paineis_e_conteudos(self):
        response = self.client.get(reverse('painel_responsavel'))
        self.assertEqual(response.status_code, 200)
        for panel in ('tab-tarefas', 'tab-premios', 'tab-familia', 'tab-analises'):
            self.assertContains(response, f'id="{panel}"')
        self.assertContains(response, 'guardian-tabs.js')

    def test_historico_fica_abaixo_das_pendencias_em_analises(self):
        response = self.client.get(reverse('painel_responsavel'))
        html = response.content.decode()
        tarefas_panel = html.split('id="tab-tarefas"', 1)[1].split('id="tab-premios"', 1)[0]
        analises_panel = html.split('id="tab-analises"', 1)[1]
        self.assertNotIn('Histórico de tarefas', tarefas_panel)
        self.assertLess(analises_panel.index('Pendências'), analises_panel.index('Histórico de tarefas'))

    def test_atualiza_nome_da_familia(self):
        response = self.client.post(reverse('editar_familia'), {'sobrenome': 'Nova Família'})
        self.familia.refresh_from_db()
        self.assertEqual(self.familia.sobrenome, 'Nova Família')
        self.assertRedirects(response, '/responsavel/#tab-familia', fetch_redirect_response=False)

    def test_desativa_crianca_sem_apagar_perfil(self):
        response = self.client.post(reverse('alternar_crianca', args=[self.crianca.id]))
        self.crianca.refresh_from_db()
        self.assertFalse(self.crianca.ativo)
        self.assertRedirects(response, '/responsavel/#tab-familia', fetch_redirect_response=False)

    def test_perfil_de_outra_familia_nao_pode_ser_alterado(self):
        outra_familia = Familia.objects.create(sobrenome='Outra')
        outro_usuario = User.objects.create_user('outra_crianca', password='Senha-forte-123')
        outra_crianca = Perfil.objects.create(usuario=outro_usuario, familia=outra_familia, papel=Perfil.CRIANCA)
        response = self.client.post(reverse('alternar_crianca', args=[outra_crianca.id]))
        self.assertEqual(response.status_code, 404)
        outra_crianca.refresh_from_db()
        self.assertTrue(outra_crianca.ativo)

    def test_crianca_desativada_nao_consegue_entrar(self):
        self.crianca.ativo = False
        self.crianca.save(update_fields=['ativo'])
        self.client.logout()
        response = self.client.post(reverse('entrar'), {'nome_usuario': 'crianca', 'senha': 'Senha-forte-123'})
        self.assertContains(response, 'Usuário ou senha inválidos.')
        self.assertFalse('_auth_user_id' in self.client.session)


class ContaSemPerfilTests(TestCase):
    def test_superusuario_sem_perfil_vai_para_admin_sem_ciclo(self):
        User.objects.create_superuser('admin', password='Senha-forte-123')
        self.client.login(username='admin', password='Senha-forte-123')
        response = self.client.get(reverse('inicio'))
        self.assertRedirects(response, reverse('admin:index'), fetch_redirect_response=False)

    def test_usuario_comum_sem_perfil_e_desconectado(self):
        User.objects.create_user('solto', password='Senha-forte-123')
        self.client.login(username='solto', password='Senha-forte-123')
        response = self.client.get(reverse('inicio'), follow=True)
        self.assertContains(response, 'não está ligada a uma família')
        self.assertFalse('_auth_user_id' in self.client.session)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ComandoDemoTests(TestCase):
    def test_demo_reset_recria_dados_sem_tocar_em_outras_familias(self):
        outra = Familia.objects.create(sobrenome='Real')
        call_command('demo', stdout=StringIO())
        Tarefa.objects.filter(estado=Tarefa.PENDENTE).update(estado=Tarefa.CONCLUIDA)  # simula uso
        call_command('demo', '--reset', stdout=StringIO())
        ana = Perfil.objects.get(usuario__username='ana.demo')
        self.assertEqual(saldo_da_crianca(ana), 10)
        self.assertEqual(Envio.objects.filter(estado=Envio.PENDENTE).count(), 1)
        self.assertEqual(Familia.objects.filter(sobrenome='Silva').count(), 1)
        self.assertTrue(Familia.objects.filter(pk=outra.pk).exists())
