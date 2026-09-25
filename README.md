# DevShowcase API

Primeira etapa do back-end: perfis, projetos, tecnologias e opiniões, com persistência em SQLite. As relações são Profile 1:N Project, Project N:N Technology e Project 1:N Feedback. A entidade Feedback está modelada; a atividade pede rotas apenas para as outras três entidades.

## Rodar

É necessário Python 3.10 ou superior. No terminal, dentro desta pasta:

```bash
python -m venv .venv
```

Ative o ambiente no Windows com `.venv\Scripts\activate` ou no Linux/macOS com `source .venv/bin/activate`. Depois:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Acesse http://127.0.0.1:8000/docs para testar a API pelo navegador. O arquivo `devshowcase.db` surge automaticamente na primeira execução.

## Ordem para testar as seis rotas

1. `POST /api/profiles` com `{"name":"Seu nome","bio":"Sobre você","github_url":"https://github.com/seunome"}`. Anote o `id` retornado.
2. `GET /api/profiles/1` (use o ID que recebeu).
3. `POST /api/technologies` com `{"name":"Python"}`. Anote o `id`.
4. `GET /api/technologies`.
5. `POST /api/projects` com `{"title":"Meu portfólio","description":"Site pessoal","repository_url":"https://github.com/ana/portfolio","profile_id":1,"technology_ids":[1]}`. Troque os IDs pelos que recebeu.
6. `GET /api/projects`.

Em `/docs`, clique na rota, em **Try it out**, preencha o JSON e clique em **Execute**. Para demonstrar validação, envie um perfil com `github_url` inválida: a API retorna erro 422. Um perfil inexistente retorna 404.

