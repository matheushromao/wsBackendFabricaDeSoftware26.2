from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect ,render

# Create your views here.

def cadastro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("login")
    else:
        form = UserCreationForm()
        
    return render(request, "app/cadastro.html", {"form": form})