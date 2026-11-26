from django import forms
from .models import Recompensa


class RecompensaForm(forms.ModelForm):
    class Meta:
        model = Recompensa
        fields = ['nome', 'custo']
        labels = {'nome': 'Recompensa', 'custo': 'Custo em pontos'}

    def clean_custo(self):
        custo = self.cleaned_data['custo']
        if custo < 1:
            raise forms.ValidationError('O custo deve ser maior que zero.')
        return custo
