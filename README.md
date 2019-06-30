# anti_nude_bot
Este bot bloqueia o envio de imagens pornográficas no grupo. Este precisa de acesso administrativo do grupo, para banir os mal intencionados. É necessário, também, criar um canal para adicionar ao REG_GROUP, para registrar os banidos.

## nudepy
A biblioteca usada não é tão eficaz, mas pega até hentai explicito.

## Configuração Heroku
Estas são as chaves necessárias da configuração de variávels para que o bot funcione de maneira eficaz:

| KEY       | VALUE     |
| :-------- | :-------- |
| HEROKU_APP_NAME | Nome do app escolhido |
| MODO      | prod |
| REGISTER  | Link do grupo para registro |
| TOKEN     | Token do bot, feito pelo @botfather |

Onde configurar: https://dashboard.heroku.com/apps/NOME_DO_APP/settings
