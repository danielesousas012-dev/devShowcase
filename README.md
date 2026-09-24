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

1. `POST /api/profiles` com `{"name":"Ana","bio":"Desenvolvedora","github_url":"https://github.com/ana"}`. Anote o `id` retornado.
2. `GET /api/profiles/1` (use o ID que recebeu).
3. `POST /api/technologies` com `{"name":"Python"}`. Anote o `id`.
4. `GET /api/technologies`.
5. `POST /api/projects` com `{"title":"Meu portfólio","description":"Site pessoal","repository_url":"https://github.com/ana/portfolio","profile_id":1,"technology_ids":[1]}`. Troque os IDs pelos que recebeu.
6. `GET /api/projects`.

Em `/docs`, clique na rota, em **Try it out**, preencha o JSON e clique em **Execute**. Para demonstrar validação, envie um perfil com `github_url` inválida: a API retorna erro 422. Um perfil inexistente retorna 404.

## Entrega e vídeo

Crie um repositório **público** no GitHub e envie `main.py`, `requirements.txt`, `.gitignore` e este README. Não envie `.venv` nem o banco `.db`. Grave vídeo de 5 a 8 minutos, publique como **não listado** no YouTube e envie um PDF com os dois links. No vídeo: apresente-se com a câmera ligada, mostre rapidamente as quatro entidades e as três relações no código; rode `uvicorn main:app --reload`; teste as seis rotas em `/docs`, mostrando requisição e resposta na tela; mostre o repositório público. Compartilhe a tela inteira e confira o áudio.
