from dataclasses import dataclass

import requests
from django.core.cache import cache

URL_MERCADO = "https://api.cartolafc.globo.com/atletas/mercado"
TIMEOUT = 10
CACHE_KEY = "cartola_mercado"
CACHE_SEGUNDOS = 60 * 10

class CartolaError(Exception):
    pass

class CartolaIndisponivelError(CartolaError):
    pass    
class CartolaRespostaInvalidaError(CartolaError):
    pass

@dataclass
class AtletaExterno:
    
    atleta_id: int
    apelido: str
    clube: str
    posicao: str
    preco: float
    pontos: float
    foto_url: str

def listar_atletas(posicao_id = None):
    dados = _buscar_mercado()
    
    clubes = dados.get("clubes", ())
    posicoes = dados.get("posicoes", ())
    atletas_brutos = dados.get("atletas", ())
    
    atletas = []
    for bruto in atletas_brutos:
        if posicao_id and bruto.get("posicao_id") != int(posicao_id):
            continue
        atletas.append(_montar_atleta(bruto, clubes, posicoes))
    
    atletas.sort(key=lambda a: a.preco, reverse=True)
    return atletas

def listar_posicoes():
    dados = _buscar_mercado()
    posicoes = dados.get("posicoes", {})
    return sorted(
        ({"id": p.get("id"), "nome": p.get("nome")} for p in posicoes.values()),
        key=lambda p: p["id"],
    )

def buscar_atleta_por_id(atleta_id):
    for atleta in listar_atletas():
        if atleta.atleta_id == int(atleta_id):
            return atleta
    return None

def _buscar_mercado():
    
    em_cache = cache.get(CACHE_KEY)
    if em_cache is not None:
        return em_cache
    
    try:
        resposta = requests.get(URL_MERCADO, timeout=TIMEOUT)
        resposta.raise_for_status()
    except requests.exceptions.Timeout as erro:
        raise CartolaIndisponivelError(
            "O Cartola FC demorou demais para responder. Já já ele volta, tenta de novo!"
        ) from erro
    except requests.exceptions.HTTPError as erro:
        raise CartolaIndisponivelError(
            f"O Cartola FC respondeu com erro (status {resposta.status_code})."
        ) from erro
    except requests.exceptions.RequestException as erro:
        raise CartolaIndisponivelError(
            "Não foi possível se conectar ao Cartola FC."
        ) from erro
    
    
    try:
        dados = resposta.json()
    except ValueError as erro:
        raise CartolaRespostaInvalidaError(
            "O Cartola FC devolveu uma resposta que não é JSON válido."
        ) from erro
    
    if "atletas" not in dados:
        raise CartolaRespostaInvalidaError(
            "A resposta do Cartola FC não contém a lista de atletas."
        )
        
    cache.set(CACHE_KEY, dados, CACHE_SEGUNDOS)
    return dados

def _montar_atleta(bruto, clubes, posicoes):
    clube_id = str(bruto.get("clube_id", ""))
    posicao_id = str(bruto.get("posicao_id", ""))
    
    return AtletaExterno(
        atleta_id=bruto.get("atleta_id", 0),
        apelido=bruto.get("apelido", "Sem nome"),
        clube=clubes.get(clube_id, {}).get("nome", ""),
        posicao=posicoes.get(posicao_id, {}).get("nome", ""),
        preco=float(bruto.get("preco_num") or 0),
        pontos=float(bruto.get("pontos_num") or 0),
        foto_url=(bruto.get("foto") or "").replace("FORMATO", "140x140"),
    )