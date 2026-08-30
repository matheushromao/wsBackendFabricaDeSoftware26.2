from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404 ,redirect ,render

from .forms import TimeForm
from .models import AtletaEscalado, Time
from .service import cartola

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
            
    
@login_required
def mercado(request):
    time = Time.objects.filter(usuario=request.user).first()
    if not time:
        messages.error(request, "Crie seu time antes de escalar atletas.")
        return redirect("home")
    
    posicao_id = request.GET.get("posicao") or None
    
    try:
        atletas = cartola.listar_atletas(posicao_id=posicao_id)
        posicoes = cartola.listar_posicoes()
    except cartola.CartolaError as erro:
        messages.error(request, str(erro))
        atletas, posicoes = [], []
    
    ja_escalados = set(time.atletas.values_list("atleta_id_cartola", flat=True))
    contexto = {
        "time": time,
        "atletas": atletas[:60],
        "posicoes": posicoes,
        "posicao_selecionada": posicao_id,
        "ja_escalados": ja_escalados,
    }
    return render(request, "app/mercado.html", contexto)

@login_required
def escalar_atleta(request, atleta_id):
    if request.method != "POST":
        return redirect("mercado")
    
    time = get_object_or_404(Time, usuario=request.user)
    
    if AtletaEscalado.objects.filter(time=time, atleta_id_cartola=atleta_id).exists():
        messages.error(request, "Esse atleta já está escalado no seu time.")
        return redirect("mercado")
    
    try:
        atleta = cartola.buscar_atleta_por_id(atleta_id)
    except cartola.CartolaError as erro:
        messages.error(request, str(erro))
        return redirect("mercado")
    
    if atleta is None:
        messages.error(request, "Atleta não encontrado no mercado do Cartola FC.")
        return redirect("mercado")
    
    AtletaEscalado.objects.create(
        time=time,
        atleta_id_cartola=atleta.atleta_id,
        apelido=atleta.apelido,
        clube=atleta.clube,
        posicao=atleta.posicao,
        preco_cartoletas=atleta.preco,
        pontos_num=atleta.pontos,
        foto_url=atleta.foto_url,
    )
    messages.success(request, f"{atleta.apelido} foi escalado no seu time!")
    return redirect("home")

@login_required
def remover_atleta(request, pk):
    atleta = get_object_or_404(AtletaEscalado, pk=pk, time__usuario=request.user)
    
    if request.method == "POST":
        apelido = atleta.apelido
        atleta.delete()
        messages.success(request, f"{apelido} foi removido do seu time.")
        return redirect("home")
    
    return render(request, "app/atleta_confirmar_remocao.html", {"atleta": atleta})