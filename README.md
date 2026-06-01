# Google Workspace Automation SDK

SDK interno para automações corporativas utilizando APIs do Google Workspace.

Atualmente o projeto possui integrações com:

* Google Sheets
* Google Drive
* Google Docs
* Gmail
* Google Admin SDK

A arquitetura foi construída para permitir a adição incremental de novos serviços Google mantendo o mesmo padrão de autenticação, tipagem, logging, retry e tratamento de erros.

---

# Objetivo do Projeto

Construir um SDK corporativo interno simples, tipado, reutilizável e escalável para automações empresariais baseadas em Google Workspace, permitindo que novas integrações sejam adicionadas de forma consistente e previsível.

---

# Principais Características

* OAuth centralizado
* Cache de autenticação e serviços
* Integração unificada através do `GoogleClient`
* Logging centralizado
* Retry automático para erros transitórios
* Models tipados com `dataclasses`
* Protocols tipados para IntelliSense
* Tratamento de erros com exceções customizadas
* Arquitetura modular e extensível
* Automações desacopladas da infraestrutura

---

# Estrutura do Projeto

```text
project/
│
├── core/
├── credentials/
├── models/
├── services/
├── automations/
├── automations_config/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Requisitos

* Python 3.12+
* Conta Google Workspace autorizada
* Arquivo OAuth Client JSON

---

# Instalação

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd project
```

Crie um ambiente virtual:

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv

source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# Configuração

Copie o arquivo de exemplo:

```bash
cp example.env .env
```

ou no Windows:

```cmd
copy example.env .env
```

Preencha as variáveis necessárias.


## Configuração OAuth

A pasta `credentials/oauth/` deve conter o arquivo `google_oauth_client.json`, o qual deve ser obtido através do Google Cloud Console. Todavia, o arquivo `token_google.json` não deve ser criado manualmente, pois ele será gerado automaticamente após a primeira autenticação OAuth.


## Primeira Execução

Após adicionar o arquivo OAuth:

Execute um dos scripts de teste:

```bash
python -m automations.tests.test_drive
```

ou qualquer outro script de teste disponível.

Na primeira execução:

1. Uma janela do navegador será aberta.
2. Faça login com a conta autorizada.
3. Conceda as permissões solicitadas.
4. O arquivo `token_google.json` será criado automaticamente.

## Atualização de Scopes

Sempre que um novo scope for adicionado em `core/google_scopes.py` é necessário remover `credentials/oauth/token_google.json` e autenticar novamente executando o programa.

---

# Utilização Básica

Todos os serviços são acessados através do `GoogleClient`.

```python
from services.google.client import GoogleClient

google = GoogleClient()
```

Exemplos:

```python
google.drive
google.docs
google.sheets
google.gmail
google.admin
```

---

# Executando Testes

Os testes manuais ficam em: `automations/tests/`

Exemplos:

- `test_admin.py`
- `test_docs.py`
- `test_gmail.py`
- `test_sheets.py`

Execução:

```bash
python -m automations.tests.test_admin
```

---

# Adicionando Novos Serviços Google

Ao integrar uma nova API Google:

1. Adicionar o scope.
2. Criar a exception específica.
3. Criar os models tipados.
4. Criar os Protocols.
5. Implementar o serviço herdando `GoogleService`.
6. Integrar ao `GoogleClient`.
7. Criar testes.

A estrutura do novo serviço deve seguir exatamente o mesmo padrão utilizado pelos serviços existentes.

---

# Convenções do Projeto

## Models

Utilizar:

```python
@dataclass
```

para representar entidades retornadas pelas APIs.

## Tratamento de Erros

Utilizar exceções customizadas localizadas em: `core/exceptions.py`

## Retry

Métodos que fazem chamadas para APIs Google devem utilizar:

```python
@retry_google_api
```

## Logging

Utilizar exclusivamente o logger configurado pela infraestrutura do projeto.

# Segurança

Os seguintes arquivos nunca devem ser enviados ao repositório:

- ``.env``
- ``credentials/oauth/google_oauth_client.json``
- ``credentials/oauth/token_google.json``

Verifique o `.gitignore` antes de realizar commits.

---

# Arquitetura

A arquitetura do projeto foi construída com foco em:

* simplicidade
* reutilização
* baixo acoplamento
* forte tipagem
* escalabilidade incremental

Todos os serviços Google compartilham a mesma infraestrutura de autenticação, logging, retry e tratamento de erros.

O ponto central de acesso às APIs é a classe `GoogleClient`.

## Visão Geral

```text
              ┌───────────────────────┐
              │      Automações       │
              │  (regras de negócio)  │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │     GoogleClient      │
              └───────────┬───────────┘
                          │
    ┌───────┬────────┬────┴───┬────────┬────────┐
    ▼       ▼        ▼        ▼        ▼        ▼
  Drive    Docs    Sheets   Gmail    Admin     ... 
   API     API      API      API      API      API
    │       │        │        │        │        │
    └───────┴────────┴────┬───┴────────┴────────┘
                          │
                          ▼
               GoogleOAuthAuthenticator
                          │
                          ▼
                   Google OAuth 2.0
                          │
                          ▼
                     Google APIs
```

## Organização em Camadas

O projeto está dividido em três grandes responsabilidades.

### Infraestrutura

Responsável por autenticação, logging, retry, exceções e configurações compartilhadas.

- ``core/``
- ``services/google/``

Exemplos:

* OAuth
* criação dos clients Google
* cache de serviços
* logging
* retry automático
* tratamento de erros

---

### Serviços

Responsáveis por encapsular as chamadas para APIs Google.

`services/google/`

Exemplos:

```python
google.drive
google.docs
google.sheets
google.gmail
google.admin
```

Cada serviço:

* herda de `GoogleService`
* utiliza OAuth compartilhado
* possui logging padronizado
* possui retry automático
* retorna models tipados

### Models

Representam entidades do domínio da aplicação.

`models/`

Exemplos:

```python
DriveFile
GoogleUser
EmailAttachment
```

Objetivos:

* desacoplar a API bruta do restante do código
* melhorar IntelliSense
* melhorar legibilidade
* aumentar segurança de tipos

### Automações

Representam fluxos de negócio específicos.

``automations/``

Exemplos:

``account_creator/``
``certificates_generator/``
``interview_docs_generator/``

As automações nunca devem implementar autenticação ou comunicação direta com APIs Google.

Toda interação deve ocorrer através do `GoogleClient`.

## Fluxo de Execução

Exemplo simplificado:

```python
from services.google.client import GoogleClient

google = GoogleClient()

user = google.admin.create_user(...)
```

Fluxo interno:

```text
Automação
    ↓
GoogleClient
    ↓
GoogleAdminAPI
    ↓
GoogleOAuthAuthenticator
    ↓
Google Admin SDK
    ↓
Model Tipado
    ↓
Automação
```

---

## Compartilhamento de Infraestrutura

Todos os serviços reutilizam:

```text
✓ OAuth
✓ Token
✓ Cache de serviços
✓ Logging
✓ Retry
✓ Exceptions
✓ Configurações
```

Isso garante comportamento consistente entre todas as integrações Google.

---

# Adicionando Novas APIs

Novos serviços devem seguir exatamente o mesmo padrão arquitetural.

Exemplo:

```text
Google Calendar
Google Forms
Google Tasks
Google Chat
Google Classroom
```

O fluxo padrão é:

```text
     Adicionar Scope
           ↓
     Criar Exception
           ↓
      Criar Models
           ↓
    Criar Protocols
           ↓
  Implementar Serviço
           ↓
Integrar ao GoogleClient
           ↓
     Criar Testes
```

O objetivo é que qualquer novo serviço pareça visualmente idêntico aos serviços já existentes, mantendo previsibilidade e facilidade de manutenção.
