# 🏋️ Gym Project — Sistema de Gestão de Academia

Sistema full-stack para gestão de academias: cadastro e autenticação de alunos, contratação de planos com pagamento integrado via Mercado Pago, controle de acesso administrativo e expiração automática de planos.

Projeto pessoal construído do zero como estudo aprofundado de backend com Django REST Framework, com foco em autenticação segura, integração de pagamento real e boas práticas de arquitetura.

---

## 📌 Sobre o projeto

A maioria dos projetos de portfólio para de existir no "cadastro de usuário com CRUD". Este vai além: implementa um fluxo de pagamento real (sandbox do Mercado Pago), com verificação de status **sempre validada no servidor** — nunca confiando em dados vindos do navegador — e um sistema de expiração de planos rodando em segundo plano via Celery.

## ✨ Funcionalidades

- **Autenticação JWT** (access + refresh token) com claims customizados
- **RBAC** (Role-Based Access Control) — separação clara entre rotas de aluno e rotas administrativas
- **Contratação de planos** (mensal, trimestral, anual) integrada ao **Mercado Pago** (Checkout Pro)
- **Confirmação de pagamento validada no backend** — o servidor sempre confere o status real do pagamento diretamente na API do Mercado Pago antes de ativar qualquer plano, nunca aceitando esse dado vindo do cliente
- **Expiração automática de planos** via tarefa agendada com Celery Beat
- **Painel administrativo**: estatísticas de usuários, listagem, ativação/desativação de contas
- **Frontend em React** com dashboard do aluno e painel admin separados por permissão

## 🛠️ Stack técnica

**Backend**
- Python 3.10+ / Django 5.2 / Django REST Framework
- `djangorestframework-simplejwt` — autenticação JWT
- Celery + Redis — tarefas assíncronas e agendadas
- PostgreSQL — banco de dados
- `python-decouple` — variáveis de ambiente
- `django-cors-headers`, `django-filter`
- Mercado Pago SDK (Python)
- pytest / pytest-django — testes automatizados

**Frontend**
- React 19 + Vite
- Tailwind CSS
- `jwt-decode`

**Infraestrutura**
- Docker Compose (PostgreSQL + Redis)

## 🏗️ Arquitetura

O backend segue separação em camadas dentro de cada app Django:

```
app/
├── models.py        # Estrutura de dados
├── views.py          # Camada HTTP (request/response)
├── services.py        # Regras de negócio
├── serializers.py     # Validação e (de)serialização
└── tasks.py           # Tarefas assíncronas (Celery)
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
| `GET` | `/gym/admin/stats/` | Estatísticas gerais (total de usuários, planos ativos/inativos) | Admin |
| `GET` | `/gym/admin/users/` | Lista todos os usuários | Admin |
| `PATCH` | `/gym/admin/users/<id>/` | Ativa/desativa um usuário | Admin |

## 🔐 Segurança

- Nenhuma credencial em código — tudo via variáveis de ambiente (`.env`, nunca commitado)
- `DEBUG`, `CORS`, `SSL redirect` configurados separadamente por ambiente (`development.py` / `production.py`)
- Confirmação de pagamento **nunca** confia em status enviado pelo cliente — sempre revalida direto na API do Mercado Pago
- Rotas administrativas protegidas por `IsAdminUser` no backend (não apenas ocultas na interface)
- Throttling configurado (limite de requisições por usuário/anônimo)

### Limitação conhecida

A confirmação de pagamento hoje é **iniciada pelo cliente** (`/gym/payments/confirm/`), chamada pelo frontend após o redirecionamento do checkout — e validada de forma segura no servidor contra a API do Mercado Pago. Um **webhook assíncrono** (que receberia a notificação diretamente do Mercado Pago, independente do navegador do usuário permanecer aberto) ainda não foi implementado nesta versão. Na prática, isso significa que, se o usuário fechar o navegador antes dessa confirmação disparar, o plano pode não ser ativado automaticamente. É uma limitação de escopo conhecida, não uma falha de segurança — o dado que chega ao servidor já é sempre verificado, independente da origem.

## 🚀 Rodando localmente

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- Docker e Docker Compose

### Backend

```bash
cd web-site-gym

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Suba o banco e o Redis
docker compose up -d

# Copie o exemplo de variáveis de ambiente e preencha com seus valores
cp .env.example .env

python manage.py migrate
python manage.py runserver
```

Em outro terminal, suba o worker do Celery e o agendador:
```bash
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

### Frontend

```bash
cd gym-frontend
npm install
npm run dev
```

### Variáveis de ambiente necessárias

```
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5435
CORS_ALLOWED_ORIGINS=http://localhost:5173
MERCADOPAGO_ACCESS_TOKEN=
```

## 🧪 Testes

```bash
pytest
```

*(cobertura de testes em desenvolvimento)*

## 🗺️ Roadmap

- [ ] Webhook assíncrono do Mercado Pago (validação de assinatura)
- [ ] Suíte de testes automatizados (pytest)
- [ ] Docker Compose completo (incluindo serviço web e Celery)
- [ ] Pipeline de CI

## 📄 Licença

Este projeto está sob licença proprietária — todos os direitos reservados. Veja o arquivo [LICENSE](./LICENSE) para detalhes. O código está publicamente disponível para fins de avaliação técnica e portfólio, mas seu uso, cópia ou redistribuição não são permitidos sem autorização prévia do autor.

## 👤 Autor

**Pedro Duarte (Antonio)**
Estudante de Análise e Desenvolvimento de Sistemas
[GitHub](https://github.com/Pedrao01) · [LinkedIn](https://linkedin.com/in/pedroduarte-dev)
