#coding: utf-8
#!/usr/bin/python3.7

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.error import NetworkError, Unauthorized, BadRequest
import logging
import requests
import json
import sys
import os
import re
import datetime
from pytz import timezone
import nude
import shutil
from nude import Nude

API_TOKEN = os.getenv('TOKEN') #645361521:AAH3RJjl_XEI4sXITXU4FuJoKfTJpFjOVuY

REG_GROUP = os.getenv('REGISTER')

modo = os.getenv('MODO')

logging.basicConfig(level=logging.INFO)

if modo == 'dev':
	def rodar(updater):
		updater.start_polling()
		updater.idle()

elif modo == 'prod':
	def rodar(updater):
		PORTA = int(os.environ.get('PORT', '8443'))
		HEROKU_NOME = os.environ.get('HEROKU_APP_NAME')

		updater.start_webhook(listen='0.0.0.0',
			port=PORTA,
			url_path=API_TOKEN)
		updater.bot.set_webhook('https://{}.herokuapp.com/{}'.format(HEROKU_NOME, API_TOKEN))
else:
	logging.error('MODO NÃO ESPECIFICADO')
	sys.exit()

@run_async
def check_nude(bot, update):
	foto = bot.get_file(update.message.photo[-1].file_id)
	foto = str(foto) #transformando o tipo type para string
	foto = foto.replace("'", '"') #substituindo os ' por "

	js = json.loads(foto) #carregando o json
	foto = js['file_path'] #conseguindo a fonte da imagem

	r = requests.get(foto, stream=True) #fazendo a requisição para baixar a img
	foto = foto.split('/')[-1] #dividindo para pegar apenas o nome e a extensão

	with open(foto, 'wb') as fo:
		shutil.copyfileobj(r.raw, fo)
	del r

	if nude.is_nude(str(foto)) == True: #checando se tem nude ou n com nudepy
		alvo_id = update.message.from_user.id
		alvo_usuario = update.message.from_user.username
		alvo_nome = update.message.from_user.first_name

		if alvo_usuario == None:
			banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_nome, alvo_id)
		else:
			banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_usuario, alvo_id)

		banido_usuario = '''
#BANIDO_USUARIO
<b>Usuário: </b>{user_name} [{user_id}]
<b>Grupo: </b>{group_name} [{group_id}]
<b>Data: </b>{data}
<b>Motivo: </b>{motivo}
'''.format(user_name=alvo_usuario,
		user_id=alvo_id,
		group_name=update.message.chat.title,
		group_id=update.message.chat.id,
		data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
	  	motivo='Pornografia')

		bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=banido_usuario)
	else: pass

def main():
	updater = Updater(token=API_TOKEN)
	dispatcher = updater.dispatcher

	# saida
	dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, saida))
	
	# filtrar imagens
	dispatcher.add_handler(MessageHandler(Filters.photo, check_nude))

	rodar(updater)

if __name__ == '__main__':
	main()
