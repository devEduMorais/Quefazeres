import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from familia.models import Familia, Perfil
from recompensas.services import saldo_da_crianca
from .models import Envio, Tarefa

SENHA = 'Senha-forte-123'
MEDIA_TEMP = tempfile.mkdtemp()


def criar_perfil(username, familia, papel):
    usuario = User.objects.create_user(username, password=SENHA)
    return Perfil.objects.create(usuario=usuario, familia=familia, papel=papel, nome_completo=username.title())


@override_settings(MEDIA_ROOT=MEDIA_TEMP)
class FluxoTarefaTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMP, ignore_errors=True)

    def setUp(self):
        self.familia = Familia.objects.create(sobrenome='Silva')
        self.responsavel = criar_perfil('resp', self.familia, Perfil.RESPONSAVEL)
        self.crianca = criar_perfil('ana', self.familia, Perfil.CRIANCA)
        self.tarefa = Tarefa.objects.create(familia=self.familia, crianca=self.crianca, descricao='Arrumar a cama', pontos=10)

    def enviar_foto(self):
        self.client.login(username='ana', password=SENHA)
        foto = SimpleUploadedFile('foto.png', b'\x89PNG\r\n\x1a\n', content_type='image/png')
        return self.client.post(reverse('enviar_tarefa'), {'tarefa_id': self.tarefa.id, 'foto': foto})

    def test_responsavel_cria_tarefa(self):
        self.client.login(username='resp', password=SENHA)
        self.client.post(reverse('criar_tarefa'), {'descricao': 'Lavar a louça', 'crianca': self.crianca.id, 'pontos': 7})
        self.assertTrue(Tarefa.objects.filter(descricao='Lavar a louça', familia=self.familia).exists())

    def test_crianca_nao_cria_tarefa(self):
        self.client.login(username='ana', password=SENHA)
        self.client.post(reverse('criar_tarefa'), {'descricao': 'Hack', 'crianca': self.crianca.id, 'pontos': 999})
        self.assertFalse(Tarefa.objects.filter(descricao='Hack').exists())

    def test_envio_deixa_tarefa_pendente(self):
        self.enviar_foto()
        self.tarefa.refresh_from_db()
        self.assertEqual(self.tarefa.estado, Tarefa.PENDENTE)
        self.assertEqual(self.tarefa.envios.get().estado, Envio.PENDENTE)

    def test_envio_rejeita_arquivo_que_nao_e_imagem(self):
        self.client.login(username='ana', password=SENHA)
        arquivo = SimpleUploadedFile('nota.txt', b'texto', content_type='text/plain')
        self.client.post(reverse('enviar_tarefa'), {'tarefa_id': self.tarefa.id, 'foto': arquivo})
        self.assertFalse(Envio.objects.exists())

    def test_aprovar_credita_pontos_uma_unica_vez(self):
        self.enviar_foto()
        envio = Envio.objects.get()
        self.client.login(username='resp', password=SENHA)
        self.client.post(reverse('aprovar_tarefa'), {'envio_id': envio.id})
        self.client.post(reverse('aprovar_tarefa'), {'envio_id': envio.id})  # segunda tentativa
        self.tarefa.refresh_from_db()
        self.assertEqual(self.tarefa.estado, Tarefa.CONCLUIDA)
        self.assertEqual(saldo_da_crianca(self.crianca), 10)

    def test_reprovar_nao_credita_e_libera_novo_envio(self):
        self.enviar_foto()
        envio = Envio.objects.get()
        self.client.login(username='resp', password=SENHA)
        self.client.post(reverse('reprovar_tarefa'), {'envio_id': envio.id})
        self.tarefa.refresh_from_db()
        self.assertEqual(self.tarefa.estado, Tarefa.DISPONIVEL)
        self.assertEqual(saldo_da_crianca(self.crianca), 0)

    def test_responsavel_de_outra_familia_nao_aprova(self):
        self.enviar_foto()
        envio = Envio.objects.get()
        outra = Familia.objects.create(sobrenome='Souza')
        criar_perfil('intruso', outra, Perfil.RESPONSAVEL)
        self.client.login(username='intruso', password=SENHA)
        response = self.client.post(reverse('aprovar_tarefa'), {'envio_id': envio.id})
        self.assertEqual(response.status_code, 404)
        envio.refresh_from_db()
        self.assertEqual(envio.estado, Envio.PENDENTE)

    def test_svg_com_script_e_rejeitado(self):
        self.client.login(username='ana', password=SENHA)
        svg = SimpleUploadedFile('x.svg', b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', content_type='image/svg+xml')
        response = self.client.post(reverse('enviar_tarefa'), {'tarefa_id': self.tarefa.id, 'foto': svg}, follow=True)
        self.assertFalse(Envio.objects.exists())
        self.assertContains(response, 'Formato não aceito')

    def test_arquivo_com_extensao_de_imagem_mas_conteudo_falso_e_rejeitado(self):
        self.client.login(username='ana', password=SENHA)
        falso = SimpleUploadedFile('foto.png', b'<html>nada</html>', content_type='image/png')
        self.client.post(reverse('enviar_tarefa'), {'tarefa_id': self.tarefa.id, 'foto': falso})
        self.assertFalse(Envio.objects.exists())

    def test_foto_grande_mostra_mensagem_clara(self):
        self.client.login(username='ana', password=SENHA)
        grande = SimpleUploadedFile('foto.jpg', b'\xff\xd8\xff' + b'0' * (11 * 1024 * 1024), content_type='image/jpeg')
        response = self.client.post(reverse('enviar_tarefa'), {'tarefa_id': self.tarefa.id, 'foto': grande}, follow=True)
        self.assertFalse(Envio.objects.exists())
        self.assertContains(response, 'A foto é muito grande')

    def test_foto_jpg_de_celular_ate_10mb_e_aceita(self):
        self.client.login(username='ana', password=SENHA)
        foto = SimpleUploadedFile('IMG_0001.JPG', b'\xff\xd8\xff\xe0' + b'0' * (6 * 1024 * 1024), content_type='image/jpeg')
        self.client.post(reverse('enviar_tarefa'), {'tarefa_id': self.tarefa.id, 'foto': foto})
        self.assertTrue(Envio.objects.exists())

    def test_envio_id_invalido_retorna_404(self):
        self.client.login(username='resp', password=SENHA)
        response = self.client.post(reverse('aprovar_tarefa'), {'envio_id': 'abc'})
        self.assertEqual(response.status_code, 404)
