from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django import forms
from .models import Familia, Perfil


class CadastroResponsavelForm(forms.Form):
    nome_completo = forms.CharField(max_length=200, label='Nome completo')
    nome_usuario = forms.CharField(max_length=150, label='Usuário')
    sobrenome_familia = forms.CharField(max_length=100, label='Sobrenome da família')
    email = forms.EmailField(max_length=254, label='E-mail')
    celular = forms.CharField(max_length=16, label='Celular', widget=forms.TextInput(attrs={'inputmode': 'numeric', 'placeholder': '(99) 99999-9999', 'data-phone-mask': 'true'}))
    senha = forms.CharField(widget=forms.PasswordInput, label='Senha')
    confirmar_senha = forms.CharField(widget=forms.PasswordInput, label='Confirmar senha')

    def clean_nome_usuario(self):
        username = self.cleaned_data['nome_usuario']
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Esse usuário já está em uso.')
        return username

    def clean_nome_completo(self):
        return ' '.join(self.cleaned_data['nome_completo'].split())

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_celular(self):
        value = self.cleaned_data['celular']
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) != 11 or digits[:2] in ('00', '01'):
            raise ValidationError('Informe um celular com DDD no formato (99) 99999-9999.')
        return f'({digits[:2]}) {digits[2:7]}-{digits[7:]}'

    def clean(self):
        data = super().clean()
        if data.get('senha') and data.get('confirmar_senha') and data['senha'] != data['confirmar_senha']:
            self.add_error('confirmar_senha', 'As senhas não conferem.')
        if data.get('senha'):
            try:
                validate_password(data['senha'])
            except ValidationError as exc:
                self.add_error('senha', exc)
        return data


class CriarCriancaForm(forms.Form):
    nome_completo = forms.CharField(max_length=200, label='Nome completo')
    nome_usuario = forms.CharField(max_length=150, label='Usuário para login')
    senha = forms.CharField(widget=forms.PasswordInput, label='Senha inicial')

    def clean_nome_usuario(self):
        username = self.cleaned_data['nome_usuario']
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Esse usuário já está em uso.')
        return username

    def clean_nome_completo(self):
        return ' '.join(self.cleaned_data['nome_completo'].split())

    def clean_senha(self):
        password = self.cleaned_data['senha']
        validate_password(password)
        return password


class EditarCriancaForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nome_completo']
        labels = {'nome_completo': 'Nome completo'}

    def clean_nome_completo(self):
        return ' '.join(self.cleaned_data['nome_completo'].split())


class EditarFamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = ['sobrenome']
        labels = {'sobrenome': 'Nome da família'}
