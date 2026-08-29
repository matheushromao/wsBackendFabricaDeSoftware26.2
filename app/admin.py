from django.contrib import admin
from .models import AtletaEscalado, Time

# Register your models here.

@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ("nome", "usuario", "criado_em")
    search_fields = ("nome", "usuario_username")
    
    
@admin.register(AtletaEscalado)
class AtletaEscaladoAdmin(admin.ModelAdmin):
    list_display = ("apelido", "clube", "posicao", "preco_cartoletas", "time")
    list_filter = ("posicao", "clube")
    search_fields = ("apelido", "clube")