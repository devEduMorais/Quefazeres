from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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
