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
        if not foto.content_type.startswith('image/'):
            raise forms.ValidationError('Envie um arquivo de imagem.')
        if foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError('A imagem deve ter no máximo 5 MB.')
        return foto
