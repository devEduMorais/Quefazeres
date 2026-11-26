from django import forms
from .models import Tarefa


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['descricao', 'crianca', 'pontos']
        labels = {'descricao': 'Atividade', 'crianca': 'Designar para', 'pontos': 'Pontos'}

    def __init__(self, *args, familia, **kwargs):
        super().__init__(*args, **kwargs)
        from familia.models import Perfil
        self.fields['crianca'].queryset = Perfil.objects.filter(familia=familia, papel=Perfil.CRIANCA, ativo=True).select_related('usuario')

    def clean_pontos(self):
        pontos = self.cleaned_data['pontos']
        if pontos < 1:
            raise forms.ValidationError('Os pontos devem ser maiores que zero.')
        return pontos

    def save(self, commit=True):
        tarefa = super().save(commit=False)
        if self.fields['crianca'].queryset.count() == 0:
            raise forms.ValidationError('Cadastre uma conta infantil antes de criar tarefas.')
        if commit:
            tarefa.save()
        return tarefa


class EnvioForm(forms.Form):
    tarefa_id = forms.IntegerField(widget=forms.HiddenInput)
    foto = forms.FileField(label='Foto de comprovação')

    def clean_foto(self):
        foto = self.cleaned_data['foto']
        if foto.size > TAMANHO_MAXIMO_FOTO:
            raise forms.ValidationError('A foto é muito grande. Envie uma imagem de até 10 MB.')
        extensao = foto.name.rsplit('.', 1)[-1].lower() if '.' in foto.name else ''
        inicio = foto.read(12)
        foto.seek(0)
        if extensao not in EXTENSOES_PERMITIDAS or not _assinatura_de_imagem(inicio):
            raise forms.ValidationError('Formato não aceito. Envie uma foto JPG, PNG, GIF ou WEBP.')
        return foto


TAMANHO_MAXIMO_FOTO = 10 * 1024 * 1024
EXTENSOES_PERMITIDAS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def _assinatura_de_imagem(inicio):
    """Confere os primeiros bytes do arquivo para garantir que é mesmo uma imagem."""
    return (
        inicio.startswith(b'\xff\xd8\xff')                       # JPEG
        or inicio.startswith(b'\x89PNG\r\n\x1a\n')               # PNG
        or inicio[:6] in (b'GIF87a', b'GIF89a')                  # GIF
        or (inicio[:4] == b'RIFF' and inicio[8:12] == b'WEBP')   # WEBP
    )
