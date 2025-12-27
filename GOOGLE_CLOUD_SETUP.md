# Configuração Google Drive + Kestra

Para que o Kestra consiga ler e baixar arquivos do seu Google Drive, precisamos criar um "robô" (Service Account) no Google Cloud.

## Passo 1: Criar Projeto no Google Cloud
1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um **Novo Projeto** (ex: "Automacao-Boletos").

## Passo 2: Ativar a API do Drive
1.  No menu lateral, vá em **APIs e Serviços** -> **Biblioteca**.
2.  Pesquise por **"Google Drive API"**.
3.  Clique em **Ativar**.

## Passo 3: Criar a Conta de Serviço (O "Robô")
1.  Vá em **APIs e Serviços** -> **Credenciais**.
2.  Clique em **+ CRIAR CREDENCIAIS** -> **Conta de serviço**.
3.  Dê um nome (ex: `kestra-bot`).
4.  Clique em **Criar e Continuar** (pode pular as permissões opcionais).
5.  Clique em **Concluir**.

## Passo 4: Baixar a Chave (JSON)
1.  Na lista de Contas de Serviço, clique no e-mail do robô que você acabou de criar (ex: `kestra-bot@automacao-boletos.iam.gserviceaccount.com`).
2.  Vá na aba **Chaves**.
3.  Clique em **Adicionar Chave** -> **Criar nova chave**.
4.  Escolha **JSON** e clique em **Criar**.
5.  **Guarde esse arquivo!** Ele é a "identidade" do seu robô.
    *   No Kestra, você vai colar o *conteúdo* desse arquivo em um Secret (ex: `GCP_CREDS`).

## Passo 5: Compartilhar a Pasta (O "Pulo do Gato") 🐈
O robô não tem acesso ao seu Drive pessoal automaticamente. Você precisa convidá-lo.

1.  Vá no seu Google Drive pessoal.
2.  Crie uma pasta chamada **"Input_Boletos"**.
3.  Clique com o botão direito -> **Compartilhar**.
4.  **Copie o e-mail do robô** (aquele `...iam.gserviceaccount.com`) e cole aí.
5.  Dê permissão de **Editor** e envie.
6.  Faça o mesmo para uma pasta **"Processed_Boletos"** (se quiser mover depois).

**Pronto!** Agora o Kestra consegue acessar essa pasta como se fosse um usuário compartilhado.
