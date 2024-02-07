# JustEats

JustEats é uma plataforma de delivery de comida comprometida com justiça, transparência e apoio à comunidade de
restaurantes, entregadores e clientes. Construída sobre os princípios do software livre, JustEats visa criar um
ecossistema equitativo para todos os stakeholders envolvidos.

### Pré requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [pyenv](https://realpython.com/lessons/installing-pyenv/)

### TL/DR

Esse comando vai executar a aplicação localmente em um container Docker juntamente com todas suas dependências.

```
make dev/run
```

### Makefile

Nós usamos um Makefile prático que sabe como compilar, construir, testar e publicar a aplicação em uma imagem docker. A
ideia completa de usar make visa a premissa de fornecer um requisito de configuração quase zero para executar tarefas
cotidianas ao desenvolver e implantar uma aplicação.

#### Tasks

- `make dev/setup`: configura o ambiente de desenvolvimento, configurando o pyenv e instalando as dependências do
  projeto
- `make test`: executa os testes da aplicação subindo todas as dependencias em containers docker
- `dev/run`: executa a aplicação localmente em um container docker, acessível em http://localhost:5000
