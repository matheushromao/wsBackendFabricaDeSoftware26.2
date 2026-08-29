from django import forms

from .models import Time

class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ["nome"]
        widgets = {
            "nome" : forms.TextInput(attrs={"placeholder": "Ex: Fúria FC"}),
        }
        labels = {
            "nome" : "Nome do time"
        }