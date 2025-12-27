# Configurando Variáveis no Kestra (Alternativa sem Secrets)

Se a função de Secrets não estiver disponível para você, podemos usar variáveis de ambiente diretas.

## Opção: Texto Simples no YAML

No arquivo `kestra_flow.yaml`, você preenche os valores diretamente:

```yaml
env:
  DEEPSEEK_API_KEY: "sk-..." 
  MONGODB_URI: "mongodb://admin:admin@host.docker.internal:27017/"
  ...
```

**⚠️ Atenção**: Isso deixa suas senhas visíveis para quem tiver acesso ao arquivo de fluxo. Para um projeto pessoal rodando localmente, o risco é menor, mas evite isso em projetos compartilhados.

## Nota sobre Docker
Lembre-se: se o Kestra estiver rodando no Docker e o Mongo estiver rodando no seu Windows (ou outro container), o endereço `localhost` não funciona. Use `host.docker.internal` para o Kestra "enxergar" o seu computador.
