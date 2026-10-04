# 🏋️ Gym Project — Sistema de Gestão de Academia

Sistema full-stack para gestão de academias: cadastro e autenticação de alunos, contratação de planos com pagamento integrado via Mercado Pago, controle de acesso administrativo e expiração automática de planos.

Projeto pessoal construído do zero como estudo aprofundado de backend com Django REST Framework, com foco em autenticação segura, integração de pagamento real, boas práticas de arquitetura e entrega em produção (Docker, Nginx, CI e monitoramento de erros).

---

## 📌 Sobre o projeto

A maioria dos projetos de portfólio para de existir no "cadastro de usuário com CRUD". Este vai além: implementa um fluxo de pagamento real (sandbox do Mercado Pago), com verificação de status **sempre validada no servidor** — nunca confiando em dados vindos do navegador —, um sistema de expiração de planos rodando em segundo plano via Celery, pipeline de CI e uma stack completa containerizada, servida por Nginx.

## ✨ Funcionalidades

- **Autenticação JWT** (access + refresh token) com claims customizados (`is_staff`)
- **Renovação automática de token** no frontend: ao receber `401`, o cliente tenta o refresh e refaz a requisição; se falhar, faz logout
- **RBAC** (Role-Based Access Control) — separação clara entre rotas de aluno e rotas administrativas
- **Contratação de planos** integrada ao **Mercado Pago** (Checkout Pro):

  | Plano | Duração | Valor |
  |---|---|---|
  | Mensal | 1 mês | R$ 50,00 |
  | Trimestral | 3 meses | R$ 120,00 |
  | Anual | 12 meses | R$ 550,00 |

- **Confirmação de pagamento validada no backend** — o servidor consulta o pagamento diretamente na API do Mercado Pago, confere que ele pertence ao usuário autenticado e que está `approved` antes de ativar qualquer plano. A operação é idempotente por `payment_id`
- **Expiração automática de planos** via tarefa agendada com Celery Beat (execução diária à meia-noite UTC)
- **Painel administrativo**: estatísticas de planos, listagem paginada com busca (username, e-mail e telefone) e ativação/desativação do plano do aluno
- **Monitoramento de erros** com Sentry e handler de exceções customizado (erros não tratados são logados e retornam um `500` genérico, sem vazar detalhes internos)
- **Frontend em React** com dashboard do aluno (perfil, pagamentos) e painel admin separados por permissão

## 🛠️ Stack técnica

**Backend**
- Python 3.13 / Django 5.2 / Django REST Framework
- `djangorestframework-simplejwt` — autenticação JWT
- Celery + Redis — tarefas assíncronas e agendadas
- PostgreSQL 16 — banco de dados
- Gunicorn — servidor de aplicação em produção
- `python-decouple` — variáveis de ambiente
- `django-cors-headers`, `django-filter`
- Mercado Pago SDK (Python)
- `sentry-sdk` — monitoramento de erros
- pytest / pytest-django / pytest-cov — testes automatizados
- flake8, black, isort — lint e formatação

**Frontend**
- React 19 + Vite
- Tailwind CSS 4
- `jwt-decode`

**Infraestrutura**
- Docker e Docker Compose (stack completa: PostgreSQL, Redis, API, Celery worker, Celery Beat, Nginx e build do frontend)
- Nginx como proxy reverso da API e servidor dos arquivos estáticos do frontend
- GitHub Actions (CI)

## 🏗️ Arquitetura

O repositório é dividido em backend e frontend:

```
Gym_Project/
├── .github/workflows/ci.yml   # Pipeline de CI
├── web-site-gym/              # Backend (Django + DRF)
│   ├── config/                # Settings (base / development / production) e Celery
│   ├── core/                  # Handler de exceções customizado
│   ├── users/                 # Usuários, autenticação e painel admin
│   ├── plans/                 # Planos, pagamento e expiração
│   ├── nginx/default.conf     # Configuração do Nginx
│   ├── Dockerfile
│   └── docker-compose.yml
└── gym-frontend/              # Frontend (React + Vite)
    └── src/
        ├── pages/             # Login, Register, Perfil, Pagamentos, AdminUsuarios
        └── services/api.js    # Camada de acesso à API (com refresh automático de token)
```

Dentro de cada app Django, o backend segue separação em camadas:

```
app/
├── models.py        # Estrutura de dados
├── views.py         # Camada HTTP (request/response)
├── services.py      # Regras de negócio
├── serializers.py   # Validação e (de)serialização
└── tasks.py         # Tarefas assíncronas (Celery)
```

Essa separação mantém as views enxutas — recebem a requisição, delegam a lógica de negócio para `services.py`, e devolvem a resposta. Facilita testes unitários isolados por camada.

## 🔌 Principais endpoints

| Método | Rota | Descrição | Acesso |
|---|---|---|---|
| `POST` | `/gym/create-user/` | Cadastro de novo usuário | Público |
| `POST` | `/gym/login/` | Login (retorna par de tokens JWT) | Público |
| `POST` | `/gym/refresh/` | Renovação do access token | Público |
| `GET` / `PATCH` | `/gym/user/` | Consulta/edição do próprio perfil | Autenticado |
| `POST` | `/gym/plan-payment/` | Cria preferência de pagamento no Mercado Pago | Autenticado |
| `POST` | `/gym/payments/confirm/` | Confirma pagamento (valida contra a API do Mercado Pago) | Autenticado |
| `GET` | `/gym/payments/status/` | Consulta status do plano atual | Autenticado |
| `POST` | `/gym/plan/cancel/` | Cancela o plano ativo | Autenticado |
| `GET` | `/gym/admin/stats/` | Estatísticas de planos (total, ativos e inativos) | Admin |
| `GET` | `/gym/admin/users/` | Lista paginada (10 por página) dos alunos com plano, com busca por `?search=` | Admin |
| `PATCH` | `/gym/admin/users/<id>/` | Ativa/desativa o plano do aluno (`{"is_active": true/false}`) | Admin |

## 🔐 Segurança

- Nenhuma credencial em código — tudo via variáveis de ambiente (`.env`, nunca commitado); no CI, segredos ficam em GitHub Secrets
- Settings separados por ambiente (`development.py` / `production.py`): `DEBUG`, CORS e hosts permitidos configurados individualmente
- Confirmação de pagamento **nunca** confia em status enviado pelo cliente — sempre revalida direto na API do Mercado Pago e verifica se o pagamento pertence ao usuário autenticado
- Rotas administrativas protegidas por `IsAdminUser` no backend (não apenas ocultas na interface)
- Throttling configurado: 100 requisições/dia para anônimos e 1000/dia para usuários autenticados
- Container da aplicação executa com usuário não-root
- Erros inesperados são capturados pelo handler customizado e enviados ao Sentry, sem expor detalhes na resposta

### Limitação conhecida

A confirmação de pagamento hoje é **iniciada pelo cliente** (`/gym/payments/confirm/`), chamada pelo frontend após o redirecionamento do checkout — e validada de forma segura no servidor contra a API do Mercado Pago. Um **webhook assíncrono** (que receberia a notificação diretamente do Mercado Pago, independente do navegador do usuário permanecer aberto) ainda não foi implementado nesta versão. Na prática, isso significa que, se o usuário fechar o navegador antes dessa confirmação disparar, o plano pode não ser ativado automaticamente. É uma limitação de escopo conhecida, não uma falha de segurança — o dado que chega ao servidor já é sempre verificado, independente da origem.

## 🚀 Rodando o projeto

### Pré-requisitos
- Docker e Docker Compose
- Python 3.13 (apenas para desenvolvimento local do backend)
- Node.js 20+ (apenas para desenvolvimento local do frontend)

### Variáveis de ambiente

Copie o exemplo e preencha com seus valores:

```bash
cd web-site-gym
cp .env.exemple .env
```

```
SECRET_KEY=
DEBUG=True
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost            # use "db" quando a API roda dentro do Docker Compose
DB_PORT=5432
DJANGO_SETTINGS_MODULE=config.settings.development   # ou config.settings.production
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
BACK_URL=http://localhost:5173   # URL do frontend para onde o Mercado Pago retorna após o checkout
MERCADOPAGO_ACCESS_TOKEN=
MERCADOPAGO_WEBHOOK_SECRET=      # reservado para o webhook (ainda não utilizado)
SENTRY_DSN=                      # obrigatório com config.settings.production
```

No frontend, crie `gym-frontend/.env` a partir de `.env.exemple`:

```
VITE_API_BASE=http://localhost:8000
```

### Opção 1 — Stack completa com Docker Compose

```bash
cd web-site-gym

# Build da imagem usada pelos serviços do backend
docker build -t web-site-gym:latest .

# Sobe tudo
docker compose up -d
```

Serviços iniciados: PostgreSQL, Redis, migrations, `collectstatic`, API (Gunicorn), Celery worker, Celery Beat, build do frontend e Nginx (porta 80).

> O Nginx responde apenas aos `server_name` definidos em `nginx/default.conf` (qualquer outro host recebe `444`). Para testar localmente, ajuste os domínios nesse arquivo.

### Opção 2 — Desenvolvimento local (backend e frontend separados)

**Backend**

```bash
cd web-site-gym

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Suba apenas o banco
docker compose up -d db

python manage.py migrate
python manage.py runserver
```

O broker do Celery está configurado como `redis://redis:6379/0` (hostname do serviço no Compose). Para executar o worker e o agendador, use o Compose:

```bash
docker compose up -d redis celery-work celery-beat
```

**Frontend**

```bash
cd gym-frontend
npm install
npm run dev
```

## 🧪 Testes

```bash
cd web-site-gym
pytest
```

Cobertura atual: **61 testes** distribuídos entre os apps `plans` e `users`.

| Arquivo | Escopo | Testes |
|---|---|---|
| `plans/tests/test_plan_models.py` | Model de plano | 1 |
| `plans/tests/test_plan_services.py` | Services de plano | 9 |
| `plans/tests/test_plan_tasks.py` | Task Celery de expiração | 4 |
| `plans/tests/test_plan_views.py` | Endpoints de plano e pagamento | 14 |
| `users/tests/test_user_models.py` | Model de usuário | 1 |
| `users/tests/test_user_services.py` | Services de usuário | 8 |
| `users/tests/test_user_views.py` | Endpoints de usuário e admin | 24 |

Cenários cobertos: criação e validação de usuários, autenticação JWT com claims customizados, fluxo completo de pagamento (com mock da API do Mercado Pago), status e cancelamento de planos, permissões por perfil (aluno vs admin), paginação, busca e expiração automática de planos via Celery.

## ⚙️ Integração contínua

O workflow em [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) roda a cada push em `main`/`develop` e em pull requests para `main`:

1. Instala as dependências (Python 3.13)
2. Sobe o PostgreSQL via Docker Compose e aguarda o `pg_isready`
3. Lint e formatação: `flake8`, `black --check` e `isort --check-only`
4. Verifica migrations pendentes (`makemigrations --check --dry-run`)
5. Executa os testes com relatório de cobertura (`pytest --cov`)

## 🗺️ Roadmap

- [x] Docker Compose completo (incluindo serviço web, Celery e Nginx)
- [x] Pipeline de CI
- [ ] Webhook assíncrono do Mercado Pago (validação de assinatura)
- [ ] HTTPS no Nginx (TLS) e ativação das flags de segurança de cookies/redirect em produção

## 📄 Licença

Este projeto está sob licença proprietária — todos os direitos reservados. Veja o arquivo [LICENSE](./LICENSE) para detalhes. O código está publicamente disponível para fins de avaliação técnica e portfólio, mas seu uso, cópia ou redistribuição não são permitidos sem autorização prévia do autor.

## 👤 Autor

**Pedro Duarte (Antonio)**
Estudante de Análise e Desenvolvimento de Sistemas
[GitHub](https://github.com/Pedrao01) · [LinkedIn](https://linkedin.com/in/pedroduarte-dev)