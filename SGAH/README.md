# SGAH - Sistema de Gestão e Logística de Ajuda Humanitária

Projeto final de SPOLBP1 (Laboratório de Programação 1) - aplicação web MPA feita com
Python, Flask, Jinja2 e SQLite3 (sem ORM).

O sistema ajuda a organizar a logística em situações de emergência: cada usuário cadastra
seus **abrigos**, controla o **estoque de suprimentos** (que pode ser ligado a um abrigo) e
registra **ocorrências** em campo com prioridade.

## Como executar

```bash
python -m venv .venv
.venv\Scripts\activate          # no Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python iniciar_bd.py            # cria as tabelas e o usuário de teste
python run.py
```

Depois é só abrir http://127.0.0.1:5000

## Usuário de teste

| usuário | senha |
|---------|-------|
| admin   | 1234  |

Também dá para criar uma conta nova pela tela de cadastro.

## Funcionalidades

- Cadastro, login e logout (senha salva com `generate_password_hash`)
- Painel com os números do usuário logado
- **Suprimentos**: cadastrar, listar, editar, excluir, buscar por nome/categoria e filtrar por categoria e abrigo
- **Abrigos**: cadastrar, listar, editar, excluir e buscar; mostra o estoque de cada abrigo
- **Operações**: cadastrar, listar, editar, excluir, buscar e filtrar por prioridade
- Relacionamento: suprimento pertence (opcionalmente) a um abrigo
- Cada usuário só enxerga e altera os próprios registros (`WHERE usuario_id = ?`)
- Painel com resumo do dia, indicadores (estoque, abrigos, ocorrências), gráficos feitos só com CSS (ocorrências por prioridade e estoque por categoria) e área "precisa de atenção" com estoque baixo e ocorrências urgentes
- Cadastros abrem em janela (`<dialog>`); se a validação falhar, a janela reabre com os dados digitados
- Selo de "estoque baixo" nos suprimentos com 30 unidades ou menos
- Tema claro/escuro guardado em cookie
- Cookie com o último usuário que fez login
- Flash messages por categoria (sucesso, erro, aviso)
- Página de erro personalizada para 404 e 500
- Logs com `app.logger` (login, falhas de login, criação/edição/exclusão)

## Estrutura

```
sgah/
|-- iniciar_bd.py           # CREATE TABLE + usuário de teste
|-- run.py                  # inicia o servidor
|-- requirements.txt
|-- README.md
`-- app/
    |-- __init__.py         # cria o Flask, secret_key, blueprints e error handlers
    |-- db.py               # classe DatabaseConnection (__enter__ / __exit__)
    |-- models/             # Usuario, Abrigo, Suprimento, Operacao (todo o SQL fica aqui)
    |-- controllers/        # blueprints com as rotas (sem SQL)
    |-- utils/              # auth_middleware.py (@login_required)
    |-- views/              # templates Jinja2 (base.html, páginas e formulários reaproveitados _form_*.html)
    `-- static/             # css e js
```

## Observações

- O banco `banco_sistema.db` é criado na raiz do projeto quando roda o `iniciar_bd.py`.
- A `secret_key` pode ser trocada pela variável de ambiente `SECRET_KEY`.
