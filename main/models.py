# models.py
from django.db import models

class Procedimento(models.Model):
    nome = models.CharField(max_length=200, unique=True)
    descricao = models.TextField()
    passos = models.TextField()      
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome
