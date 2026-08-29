from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404 ,redirect ,render

from .forms import TimeForm
from .models import Time

# Create your views here.

def cadastro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("home")
    else:
        form = UserCreationForm()
        
    return render(request, "app/cadastro.html", {"form": form})


@login_required
def home(request):
    time = Time.objects.filter(usuario=request.user).first()
    atletas = time.atletas.all() if time else []
    
    return render(request, "app/home.html", {"time": time, "atletas": atletas})

@login_required
def criar_time(request):
    if Time.objects.filter(usuario=request.user).exists():
        messages.error(request, "Você já possui um time!")
        return redirect("home")
    
    if request.method == "POST":
        form = TimeForm(request.POST)
        if form.is_valid():
            time = form.save(commit=False)
            time.usuario = request.user
            time.save()
            messages.success(request, "Time criado com sucesso")
            return redirect("home")
    else:
        form = TimeForm()
            
    return render(request, "app/time_form.html", {"form": form, "titulo": "Criar time"})
    
    
@login_required
def editar_time(request, pk):
    time = get_object_or_404(Time, pk=pk, usuario=request.user)
    
    if request.method == "POST":
        form = TimeForm(request.POST, instance=time)
        if form.is_valid():
            form.save()
            messages.success(request, "Time atualizado com sucesso")
            return redirect("home")
    else:
            form = TimeForm(instance=time)
            
    return render(request, "app/time_form.html", {"form": form, "titulo": "Editar time"})
    
@login_required
def excluir_time(request, pk):
    time = get_object_or_404(Time, pk=pk, usuario=request.user)

    if request.method == "POST":
        time.delete()
        messages.success(request, "Time excluído com sucesso!")
        return redirect("home")

    return render(request, "app/time_confirmar_exclusao.html", {"time": time})
            
    
    