# anti_nude_bot
Este bot bloqueia o envio de imagens pornográficas no grupo. Este precisa de acesso administrativo do grupo, para banir os mal intencionados. É necessário, também, criar um canal para adicionar ao REG_GROUP, para registrar os banidos.

## nudity
A biblioteca usada tem uma eficácia de 90%. Ela pega, também, hentai explícito. Está sendo usada agora porque a antiga biblioteca (nudepy), além de descontinuada, era ineficaz (bania usuário que mandava fotos da takagi-san, fotos de casas e outras).

## Configuração Heroku
**Sugestão: o plano grátis do Heroku não permite o bom uso do bot, pois este excede a memória limite.**
Estas são as chaves necessárias da configuração de variávels para que o bot funcione de maneira eficaz:

| KEY       | VALUE     |
| :-------- | :-------- |
| HEROKU_APP_NAME | Nome do app escolhido |
| MODO      | prod |
| REGISTER  | Link do grupo para registro |
| TOKEN     | Token do bot, feito pelo @botfather |

Onde configurar: https://dashboard.heroku.com/apps/NOME_DO_APP/settings
