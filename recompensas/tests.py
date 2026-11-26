from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from familia.models import Familia, Perfil
from tarefas.models import Tarefa
from .models import Recompensa, Resgate
from .services import saldo_da_crianca

SENHA = 'Senha-forte-123'


class ResgateTests(TestCase):
    def setUp(self):
        self.familia = Familia.objects.create(sobrenome='Silva')
        usuario = User.objects.create_user('ana', password=SENHA)
        self.crianca = Perfil.objects.create(usuario=usuario, familia=self.familia, papel=Perfil.CRIANCA)
        Tarefa.objects.create(familia=self.familia, crianca=self.crianca, descricao='Cama', pontos=10, estado=Tarefa.CONCLUIDA)
        self.balinha = Recompensa.objects.create(familia=self.familia, nome='Balinha', custo=5)
        self.tv = Recompensa.objects.create(familia=self.familia, nome='TV', custo=20)
        self.client.login(username='ana', password=SENHA)

    def test_resgate_com_saldo_debita_pontos(self):
        self.client.post(reverse('resgatar'), {'recompensa_id': self.balinha.id})
        self.assertEqual(Resgate.objects.count(), 1)
        self.assertEqual(saldo_da_crianca(self.crianca), 5)

    def test_resgate_sem_saldo_e_bloqueado(self):
        self.client.post(reverse('resgatar'), {'recompensa_id': self.tv.id})
        self.assertFalse(Resgate.objects.exists())
        self.assertEqual(saldo_da_crianca(self.crianca), 10)

    def test_recompensa_de_outra_familia_nao_pode_ser_resgatada(self):
        outra = Familia.objects.create(sobrenome='Souza')
        alheia = Recompensa.objects.create(familia=outra, nome='Sorvete', custo=1)
        self.client.post(reverse('resgatar'), {'recompensa_id': alheia.id})
        self.assertFalse(Resgate.objects.exists())

    def test_recompensa_id_invalido_nao_quebra(self):
        response = self.client.post(reverse('resgatar'), {'recompensa_id': 'abc'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Resgate.objects.exists())

    def test_lojinha_mostra_quanto_falta(self):
        response = self.client.get(reverse('painel_crianca'))
        self.assertContains(response, 'Faltam 10 pontos')
