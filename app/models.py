from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Time(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="time")
    nome = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome

class AtletaEscalado(models.Model):
    time = models.ForeignKey(Time, on_delete=models.CASCADE, related_name="atletas")
    
    atleta_id_cartola = models.PositiveIntegerField(help_text="ID do atleta -> Cartola FC")
    apelido = models.CharField(max_length=100)
    clube = models.CharField(max_length=100, blank=True)
    posicao = models.CharField(max_length=50, blank=True)
    preco_cartoletas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    pontos_num = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    foto_url = models.URLField(blank=True)
    adicionado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("time", "atleta_id_cartola")
        ordering = ["-adicionado_em"]
        
        def __str__(self):
            return f"{self.apelido} ({self.time.nome})"