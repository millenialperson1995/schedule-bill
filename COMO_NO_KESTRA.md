# Como "Subir" seus arquivos para o Kestra

O Kestra precisa ter acesso aos seus scripts (`process_boletos.py`, `.env`, etc.) para executá-los. Existem duas formas principais de fazer isso:

## Opção 1: Via Git (Recomendado - Profissional)

A forma mais correta é colocar seu código no **GitHub** (ou GitLab/Bitbucket).

1.  **Crie um repositório** no GitHub.
2.  **Suba seus arquivos** para lá (`git push`).
3.  **No Kestra**: O fluxo começa baixando esses arquivos automaticamente toda vez que roda.

Seu fluxo no Kestra ficaria assim (já atualizei o arquivo `kestra_flow.yaml`): de 10 em 10 minutos, ele baixa o código novo do GitHub, instala dependências e roda.

## Opção 2: Montagem de Volume (Local - Rápido)

Se você está rodando o Kestra na **sua máquina** usando Docker, você pode "conectar" sua pasta do Windows dentro do Kestra.

No comando de rodar o Kestra (`docker run`), você adiciona:
`-v "C:\Users\rafae\OneDrive\Área de Trabalho\python:/app/python"`

E no Kestra você diz para o script rodar na pasta `/app/python`.

---

### Resumo
Para produção real, use a **Opção 1 (Git)**. Assim você pode alterar o código no seu PC, dar `git push`, e o Kestra já pega a versão nova na próxima execução, sem você precisar "copiar e colar" nada manualmente.
