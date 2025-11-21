# Book Catalog MS

Backend em FastAPI para gerenciar um catálogo de livros, permitindo operações de CRUD, importação/exportação em múltiplos formatos e suporte a desfazer ações. Projeto criado para demonstrar padrões de projeto em um contexto acadêmico.

## Visão Geral

A aplicação cataloga livros (título, autor, ISBN, editora, páginas), possibilita listar e editar registros, importar/exportar o catálogo em JSON ou XML e desfazer operações recentes para recuperar estados anteriores.

O foco é evidenciar boas práticas de arquitetura e uso de padrões clássicos.
Arquitetura do Projeto

app/domain: entidades e lógica de domínio (Book, Catalog), comandos e serviços de catálogo, controle de histórico para undo.

app/infrastructure: infra e estratégias de formato (factory + strategies JSON/XML).

app/api: DTOs e rotas FastAPI que expõem o catálogo.

app/main.py: ponto de entrada da aplicação FastAPI e health check.

Árvore resumida:

```
app/
├─ api/
│  ├─ dto.py
│  └─ routes.py
├─ domain/
│  ├─ book.py
│  ├─ catalog.py
│  ├─ commands/
│  ├─ services.py
│  └─ undo_manager.py
└─ infrastructure/
   ├─ factories/
   └─ formats/

```

## Padrões de Projeto Utilizados

### Command

Operações de mutação do catálogo são encapsuladas em comandos como AddBookCommand, UpdateBookCommand, RemoveBookCommand e ImportCatalogCommand, permitindo executar e desfazer ações de forma uniforme.
O CatalogService orquestra esses comandos antes de cada alteração, o que facilita rastrear histórico e acionar undo.

### Memento

O catálogo cria instantâneos (CatalogMemento) para preservar estados anteriores, enquanto o UndoManager mantém uma pilha limitada desses snapshots e restaura o catálogo quando solicitado.

Isso habilita a funcionalidade de “desfazer” múltiplos passos.
### Strategy

Importação e exportação suportam múltiplos formatos via estratégias JsonFormatStrategy e XmlFormatStrategy, selecionadas pela FormatFactory conforme o formato solicitado.

Esse desenho permite adicionar novos formatos sem alterar o código cliente do serviço ou das rotas.
Como Executar o Projeto

**Pré-requisitos:** Python 3.13 e Poetry instalados.

**Execute a partir da raiz do projeto:**

```
poetry config virtualenvs.in-project true
poetry install

poetry run uvicorn app.main:app --reload
```

Após o último comando, a API ficará disponível em **http://127.0.0.1:8000**.

## Documentação da API (Swagger / OpenAPI)

Com o servidor rodando, acesse http://127.0.0.1:8000/docs para visualizar a documentação interativa (Swagger UI).

### Endpoints Principais

| Método | Caminho                   | Descrição                                                             |
|--------|---------------------------|----------------------------------------------------------------------|
| GET    | /catalog/books            | Lista todos os livros.                                               |
| GET    | /catalog/books/{isbn}     | Retorna um livro pelo ISBN.                                          |
| POST   | /catalog/books            | Cria um novo livro.                                                  |
| PUT    | /catalog/books/{isbn}     | Atualiza os dados de um livro existente.                             |
| DELETE | /catalog/books/{isbn}     | Remove um livro pelo ISBN.                                           |
| POST   | /catalog/import           | Importa livros a partir de conteúdo serializado (JSON/XML).          |
| POST   | /catalog/export           | Exporta o catálogo no formato escolhido.                             |
| POST   | /catalog/undo             | Desfaz a última operação e retorna o estado atual e os undos restantes. |



