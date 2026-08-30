# Cartola Manager — wsBackendFabricaDeSoftware26.2

Aplicação web em Django onde o usuário cria seu time de fantasy game e escala
atletas reais do Campeonato Brasileiro, com os dados consumidos em tempo real
da API pública do **Cartola FC**.

Projeto desenvolvido para o Workshop de Backend da Fábrica de Software 26.2.

---

## Funcionalidades

- Cadastro, login e logout de usuários
- CRUD completo do time (criar, visualizar, editar e excluir)
- Listagem dos atletas disponíveis no mercado do Cartola FC, com filtro por posição
- Escalar e remover atletas do time
- Cada usuário só acessa e modifica o próprio time
- Tratamento de erros da API externa (timeout, indisponibilidade, resposta inválida)

---

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.13 | Linguagem |
| Django 6.1 | Framework web |
| PostgreSQL | Banco de dados |
| psycopg2-binary | Driver do PostgreSQL |
| requests | Consumo da API externa |
| python-decouple | Variáveis de ambiente |
| HTML/CSS + Jinja | Interface |

---

## Modelagem

O projeto possui duas entidades relacionadas por chave estrangeira:

```
User (Django)  ──OneToOne──>  Time  ──ForeignKey──>  AtletaEscalado
```

**Time**
| Campo | Tipo | Descrição |
|---|---|---|
| usuario | OneToOneField(User) | Dono do time |
| nome | CharField | Nome do time |
| criado_em | DateTimeField | Data de criação |

**AtletaEscalado**
| Campo | Tipo | Descrição |
|---|---|---|
| time | ForeignKey(Time) | Time ao qual pertence |
| atleta_id_cartola | PositiveIntegerField | ID do atleta na API do Cartola |
| apelido | CharField | Nome do atleta |
| clube | CharField | Clube do atleta |
| posicao | CharField | Posição em campo |
| preco_cartoletas | DecimalField | Preço em cartoletas |
| pontos_num | DecimalField | Pontuação na rodada |
| foto_url | URLField | Foto do atleta |

A restrição `unique_together = ("time", "atleta_id_cartola")` impede que o mesmo
atleta seja escalado duas vezes no mesmo time.

---

## API externa consumida

**Cartola FC** — API pública da Globo, sem necessidade de autenticação.

```
GET https://api.cartolafc.globo.com/atletas/mercado
```

A resposta traz a lista de atletas junto com dicionários de clubes e posições.
Cada atleta referencia clube e posição apenas por ID, então o service cruza
essas informações antes de devolver os dados prontos para a aplicação.

### Tratamento de erros

Toda a comunicação com a API fica isolada em `app/service/cartola.py`.
São tratados cinco cenários de falha:

| Situação | Exceção capturada | Resultado |
|---|---|---|
| API demorou a responder | `requests.exceptions.Timeout` | `CartolaIndisponivelError` |
| Status HTTP 4xx ou 5xx | `requests.exceptions.HTTPError` | `CartolaIndisponivelError` |
| Falha de conexão / DNS | `requests.exceptions.RequestException` | `CartolaIndisponivelError` |
| Resposta não é JSON válido | `ValueError` | `CartolaRespostaInvalidaError` |
| JSON sem a chave esperada | verificação manual | `CartolaRespostaInvalidaError` |

Em qualquer um dos casos a aplicação exibe uma mensagem amigável ao usuário e
continua funcionando, sem retornar erro 500.

Os dados do mercado ficam em cache por 10 minutos, evitando repetir a requisição
a cada interação do usuário.

---

## Como rodar o projeto

### Pré-requisitos
- Python 3.13 ou superior
- PostgreSQL
- Git

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/matheushromao/wsBackendFabricaDeSoftware26.2.git
cd wsBackendFabricaDeSoftware26.2
```

**2. Crie e ative o ambiente virtual**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Crie o banco de dados**

No PostgreSQL, crie um banco para a aplicação:
```sql
CREATE DATABASE cartola_manager;
```

**5. Configure as variáveis de ambiente**

Copie o arquivo de exemplo e preencha com os seus dados:

Windows:
```bash
copy .env.example .env
```

Linux / macOS:
```bash
cp .env.example .env
```

Depois edite o `.env` com as credenciais do seu PostgreSQL:
```
DB_NAME=cartola_manager
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=127.0.0.1
DB_PORT=5432
```

O arquivo `.env` está no `.gitignore` e não é versionado, mantendo as
credenciais fora do repositório.

**6. Aplique as migrations**
```bash
python manage.py migrate
```

**7. (Opcional) Crie um superusuário para acessar o admin**
```bash
python manage.py createsuperuser
```

**8. Rode o servidor**
```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`

---

## Rotas da aplicação

| Rota | Método | Descrição |
|---|---|---|
| `/` | GET | Home — time do usuário e atletas escalados |
| `/cadastro/` | GET, POST | Criar conta |
| `/login/` | GET, POST | Entrar |
| `/logout/` | POST | Sair |
| `/time/novo/` | GET, POST | Criar time |
| `/time/<id>/editar/` | GET, POST | Editar time |
| `/time/<id>/excluir/` | GET, POST | Excluir time |
| `/mercado/` | GET | Listar atletas do Cartola FC |
| `/atleta/<id>/escalar/` | POST | Escalar atleta no time |
| `/atleta/<id>/remover/` | GET, POST | Remover atleta do time |
| `/admin/` | GET | Painel administrativo do Django |

---

## Estrutura do projeto

```
wsBackendFabricaDeSoftware26.2/
├── app/
│   ├── migrations/
│   ├── service/
│   │   ├── __init__.py
│   │   └── cartola.py          # integração com a API do Cartola FC
│   ├── templates/app/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── cadastro.html
│   │   ├── mercado.html
│   │   ├── time_form.html
│   │   ├── time_confirmar_exclusao.html
│   │   └── atleta_confirmar_remocao.html
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── project/
│   ├── settings.py
│   └── urls.py
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

---

## Decisões de projeto

**Camada de service isolada** — toda comunicação HTTP com a API externa fica em
`app/service/cartola.py`. As views não conhecem detalhes de rede, JSON ou timeout:
elas pedem atletas e recebem objetos Python prontos.

**Credenciais em variáveis de ambiente** — as configurações do banco ficam no
`.env`, lidas com `python-decouple`. Além de manter senhas fora do repositório,
isso permitiu trocar o banco de dados sem alterar o código da aplicação.

**Dados do atleta copiados para o banco** — ao escalar, os dados vindos da API
são gravados localmente. Isso faz a home carregar sem depender da API e mantém
o time visível mesmo se o Cartola FC estiver fora do ar.

**Operações destrutivas apenas por POST** — exclusões nunca acontecem em GET.
As telas de confirmação usam formulário com CSRF token.

**Filtro por dono em todas as consultas** — views usam
`get_object_or_404(..., usuario=request.user)`, impedindo que um usuário acesse
ou modifique o time de outro alterando o ID na URL.

---

## Autor

**Matheus Romão**

[LinkedIn](https://www.linkedin.com/in/matheushromao)