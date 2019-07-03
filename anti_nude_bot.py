#coding: utf-8
#!/usr/bin/python3.7
#Bot anti-nude do sam

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.error import NetworkError, Unauthorized, BadRequest
import logging
import requests
import json
import os
import sys
import datetime
from pytz import timezone
import shutil
from nudity import Nudity
from PIL import Image
import Algorithmia

#Biblioteca nudity
nudity = Nudity()

#BOT TOKEN
API_TOKEN = os.getenv('TOKEN')

#GRUPO_PERMITIDO (APENAS UM GRUPO)
OFC_G = os.getenv('ONE_GROUP_ONLY')

#REGISTRY_GROUP
REG_GROUP = os.getenv('REGISTER')

#MODO = DEV / PROD
modo = os.getenv('MODO')

#ALGORITHMIA NUDITY DETECTION
ALGORITHMIA_KEY = os.getenv('ALGO_KEY')
client = Algorithmia.client(ALGORITHMIA_KEY)
algo = client.algo('sfw/NudityDetection/1.1.6')
algo.set_options(timeout=300)

permitidos = ['-1001480767444']

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

def check_group(chat_id):
	if str(chat_id) == str(OFC_G):
		return True
	else:
		return False

@run_async
def check_nude_sticker(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		'''
		A função check_nude_sticker será a versão 1.0 (sem Algorithmia), pois
		não é possível fazer a verificação com a extensão .webp.
		'''
		try:
			ids_txt = open('ids.txt', 'r+')

			sticker = str(bot.get_file(update.message.sticker.file_id)).replace("'", '"')

			js = json.loads(sticker)
			sticker = js['file_path']

			r = requests.get(sticker, stream=True)
			sticker = sticker.split('/')[-1]

			with open(sticker, 'wb') as fo:
				shutil.copyfileobj(r.raw, fo)
			del r

			#transformando de webp para jpg
			im = Image.open(sticker).convert('RGB') 
			sticker = sticker.split('.')[0] + '.jpg'
			im.save(sticker, 'jpeg')

			if nudity.has(str(sticker)) == True: #checando se tem nude ou n com nudepy
				alvo_id = update.message.from_user.id
				alvo_usuario = update.message.from_user.username
				alvo_nome = update.message.from_user.first_name

				if str(alvo_id) not in ids_txt.readlines():
					if alvo_usuario == None:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_nome, alvo_id)
					else:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_usuario, alvo_id)

					banido_usuario = '''
#BANIDO_USUARIO
<b>Usuário: </b>{user_name} [<a href="{link}">{user_id}</a>]
<b>Grupo: </b>{group_name} [{group_id}]
<b>Data: </b>{data}
<b>Motivo: </b>{motivo}
'''.format(user_name=alvo_usuario,
					user_id=alvo_id,
					group_name=update.message.chat.title,
					group_id=update.message.chat.id,
					data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
					motivo='Pornografia',
					link='tg://user?id=' + str(alvo_id))

					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
					bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=banido_usuario)

					del banido_usuario
					del banido
					del alvo_id
					del alvo_usuario
					del alvo_nome
			else: pass

			os.remove(sticker) #remove os stickers salvos para n ocupar espaço
			os.remove(sticker.split('.')[0] + '.webp') #remove os stickers salvos para n ocupar espaço
		
			del sticker
		except BadRequest as e:
			try:
				os.remove(sticker)
				os.remove(sticker.split('.')[0] + '.webp')
			except: pass

			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>O usuário é administrador e não pode ser banido.</b>', reply_to_message_id=update.message.message_id)
			bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def check_nude_image(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		try:
			ids_txt = open('ids.txt', 'r+')

			foto = bot.get_file(update.message.photo[-1].file_id)

			foto = str(foto) #transformando o tipo type para string
			foto = foto.replace("'", '"') #substituindo os ' por "

			js = json.loads(foto) #carregando o json
			foto = js['file_path'] #conseguindo a fonte da imagem

			algo_js = algo.pipe(foto).result #passando a fonte na API do algorithmia

			if algo_js['nude'] == 'true': #checando se tem nude ou n
				alvo_id = update.message.from_user.id
				alvo_usuario = update.message.from_user.username
				alvo_nome = update.message.from_user.first_name

				if str(alvo_id) not in ids_txt.readlines():
					if alvo_usuario == None:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_nome, alvo_id)
					else:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_usuario, alvo_id)

					banido_usuario = '''
#BANIDO_USUARIO
<b>Usuário: </b>{user_name} [<a href="{link}">{user_id}</a>]
<b>Grupo: </b>{group_name} [{group_id}]
<b>Data: </b>{data}
<b>Motivo: </b>{motivo}
'''.format(user_name=alvo_usuario,
					user_id=alvo_id,
					group_name=update.message.chat.title,
					group_id=update.message.chat.id,
					data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
					motivo='Pornografia',
					link='tg://user?id=' + str(alvo_id))

					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
					bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=banido_usuario)

					del banido_usuario
					del banido
					del alvo_id
					del alvo_usuario
					del alvo_nome
			else: pass

			#tentando liberar memória pro bot n explodir
			del js
			del algo_js

		except BadRequest as e:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>O usuário é administrador e não pode ser banido.</b>', reply_to_message_id=update.message.message_id)
			bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

def main():
	updater = Updater(token=API_TOKEN)
	dispatcher = updater.dispatcher
	
	# filtrar imagens
	dispatcher.add_handler(MessageHandler(Filters.photo, check_nude_image))
	
	# filtrar stickers
	dispatcher.add_handler(MessageHandler(Filters.sticker, check_nude_sticker))

	rodar(updater)

if __name__ == '__main__':
	main()
