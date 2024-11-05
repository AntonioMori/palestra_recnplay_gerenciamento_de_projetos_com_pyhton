from django import forms
from .models import Procedimento

class ProcedimentoForm(forms.ModelForm):
    class Meta:
        model = Procedimento
        fields = ['nome', 'descricao', 'passos']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do procedimento'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a descrição do procedimento',
                'rows': 3
            }),
            'passos': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva os passos do procedimento',
                'rows': 5
            }),
        }
