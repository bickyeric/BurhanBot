import json
import logging
# from logging.handlers import RotatingFileHandler

import requests
from flask import Flask, request

app = Flask(__name__)

sender_id = 0
params = {
		"access_token": "EAAEsAwadNEgBAKmrV5LxCBP1UCVQluvbcZBVfjB94qQjmO42FHgM9JVj5xKD3UGVtHqkbE7opgxNGK0fkkCYo9v42ZCitR5SDXlT0YGRc8G4Dodl6HGNWhnIDZBL3ZAZBNbMT1n2Yryb5gscxfFZArUrAo09LUagbZBoI5PLqx3kKJDZA8ivCpDM"
}
headers = {
	"Content-Type": "application/json"
}

@app.route('/', methods=['GET'])
def verify():
	app.logger.info("root page")
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == 'teuapaldjfn':
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200

	return "Hello world", 200

def cari(keyword):
	app.logger.info("scraping \"%s\" from wikipedia", keyword)
	response = requests.get("https://id.wikipedia.org/w/api.php?action=query&prop=extracts&titles="+keyword+"&exsentences=2&format=json&explaintext=true")

	obj = response.json()

	app.logger.debug("response from wikipedia : %s", obj)

	text = obj['query']['pages'].values()[0].get('extract')

	if text == None or text == '':
		return ''

	return text

def postbackHandler(postback):
	app.logger.info("handling postback!!!")
	app.logger.debug("postback data : %s", postback)

	global sender_id
	payload = postback['payload']

	if 'mulai' in payload:
		app.logger.info("user interacting with bot for first time!!")

		sendGreetingMessage(sender_id)
	elif 'CREATE_CLASS' in payload:
		app.logger.info("user create new class!!")

		data = json.dumps({
			"id_user":"{}".format(sender_id)
		})

		response = requests.post("http://vmaliqornan.southeastasia.cloudapp.azure.com:1904/vanaheim/class/create", headers=headers, data=data)

		app.logger.info("response from server : %s",response)

		obj = response.json()

		app.logger.debug("data from server : %s",obj)

		if obj['status'] == 200:
			sendCreateClassResponseMessage(sender_id,obj['data']['token_gabung_kelas'])
		else:
			send_message(sender_id, "gagal")
	elif "LEAVE_CLASS" in payload:
		app.logger.info("user leave class!!")

		data = json.dumps({
			"id_user":"{}".format(sender_id)
		})

		response = requests.post("http://vmaliqornan.southeastasia.cloudapp.azure.com:1904/vanaheim/class/leave", headers=headers, data=data)

		app.logger.info("response from server : %s",response)

		obj = response.json()

		app.logger.debug("data from server : %s",obj)

		if obj['status'] == 200:
			send_message(sender_id, "anda telah keluar dari kelas, anda tidak akan mendapat notifikasi lagi")
		else:
			send_message(sender_id, "gagal")
	elif "HELP" in payload:
		app.logger.info("user opening bantuan button!!")

		with open("pesan_bantuan.txt") as f:
			send_message(sender_id, f.read())

	elif "CHECK_CLASS" in payload:
		app.logger.info("user checking class token")

		data = json.dumps({
			"id_user":"{}".format(sender_id)
		})
		r = requests.post("http://vmaliqornan.southeastasia.cloudapp.azure.com:1904/vanaheim/class/view_token", headers=headers, data=data)

		app.logger.info("response from server : %s",r)

		obj = r.json()

		app.logger.debug("data from server : %s",obj)

		if obj['status'] == 200:
			send_message(sender_id, "token kelas anda {}".format(obj['data']['token_gabung_kelas']))
		else:
			send_message(sender_id, "gagal")
	elif "TEST_CARI" in payload:
		text = cari("array")
		send_message(sender_id, "perintah tersebut memungkinkan anda untuk menemukan definisi dari suatu istilah contohnya array dalam pemrograman, contoh responnya adalah \n{}".format(text))

	else:
		app.logger.info("unknown payload detected")


@app.route('/', methods=['POST'])
def webhook():

	data = request.get_json()
	app.logger.info("handling %s event!!!", len(data['entry']))
	app.logger.debug("event data : %s", data)


	if data["object"] == "page":

		eventCount=1
		for entry in data["entry"]:

			app.logger.info("handling event %s", eventCount)
			app.logger.debug("data event %s", data['entry'][eventCount-1])

			messageCount = 1
			for messaging_event in entry["messaging"]:

				app.logger.info("handling message %s", messageCount)
				app.logger.debug("message event %s",entry['messaging'][messageCount-1])

				global sender_id
				sender_id = messaging_event["sender"]["id"]		# the facebook ID of the person sending you the message
				recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

				if messaging_event.get("message"):  # someone sent us a message
					messageObject = messaging_event.get("message")

					if messageObject.get("text"):
						app.logger.info("handling text!!!")

						message_text = messaging_event["message"]["text"]  # the message's text

						app.logger.debug("message : %s ", message_text)

						if '/selesai' in message_text:
							send_message(sender_id, "kelas anda telah dibubarkan :D")
						elif '/keluar' in message_text:
							app.logger.info("user leave class!!")

							data = json.dumps({
								"id_user":"{}".format(sender_id)
							})

							response = requests.post("http://vmaliqornan.southeastasia.cloudapp.azure.com:1904/vanaheim/class/leave", headers=headers, data=data)

							app.logger.info("response from server : %s",response)

							obj = response.json()

							app.logger.debug("data from server : %s",obj)

							if obj['status'] == 200:
								send_message(sender_id, "anda telah keluar dari kelas, anda tidak akan mendapat notifikasi lagi")
							else:
								send_message(sender_id, "gagal")
						elif '/buat' in message_text:
							app.logger.info("user create new class!!")

							data = json.dumps({
								"id_user":"{}".format(sender_id)
							})

							response = requests.post("http://vmaliqornan.southeastasia.cloudapp.azure.com:1904/vanaheim/class/create", headers=headers, data=data)

							app.logger.info("response from server : %s",response)

							obj = response.json()

							app.logger.debug("data from server : %s",obj)

							if obj['status'] == 200:
								sendCreateClassResponseMessage(sender_id,obj['data']['token_gabung_kelas'])
							else:
								send_message(sender_id, "gagal")
						elif '/cari ' in message_text:
							app.logger.info("user asking to wikipedia!!!")

							keyword = message_text[6:]
							response =  cari(keyword)

							if response == '':
								app.logger.info("keyword not found")
								send_message(sender_id, "aku gak nemu apapun nih kak :(, coba deh cari keyword yang lain, contohnya micin :D")
							else:
								app.logger.info("keyword found")
								send_message(sender_id, response)
						elif '/tanya ' in message_text:
							app.logger.info("user asking to lecturer!!!")

							question = message_text[6:]

							r = requests.get("http://vmaliqornan.southeastasia.cloudapp.azure.com:1909/Latrevo/getDosenKelas/{}".format(sender_id))
							app.logger.info("response code %s", r)

							r = r.json()
							app.logger.debug(r)
							send_message(r['ID_USER'], "seseorang ingin bertanya:\n{}".format(question))
							send_message(sender_id, "pertanyaan kaka udah aku kirim ke dosen ya ka :D")
						elif '/gabung ' in message_text:
							app.logger.info("user want to join class")

							classId = message_text[8:]

							data = json.dumps({
								"id_user" : "{}".format(sender_id),
								"token_gabung_kelas" : "{}".format(classId)
							})

							r = requests.post("http://vmaliqornan.southeastasia.cloudapp.azure.com:1904/vanaheim/class/join", headers=headers, data=data)

							app.logger.info(r)

							send_message(sender_id, "anda bergabung ke kelas dengan id {}".format(classId))
						elif "/broadcast " in message_text:
							app.logger.info("user want to broadcast a message")

							messageText = message_text[10:]

							r = requests.get("http://vmaliqornan.southeastasia.cloudapp.azure.com:1909/Latrevo/getABroadcasts/{}".format(sender_id))
							app.logger.info("response code %s", r)

							r = r.json()

							app.logger.debug(r)
							for member in r:
								send_message(member['ID_USER'], "pesan broadcast:\n\n{}".format(messageText))

							send_message(sender_id, "pesan anda telah dikirim ke semua siswa di kelas :D")

						elif "/keyword " in message_text:
							app.logger.info("user want to save keyword")

							messageText = message_text[9:]
							messageTextArray = messageText.split(" ")

							data = json.dumps({
								"id_user" :"{}".format(sender_id),
								"konten_keyword":"{}".format(messageTextArray[0]),
								"deskripsi_keyword":"{}".format(messageText)
							})

							r = requests.post("http://vmaliqornan.southeastasia.cloudapp.azure.com:1515/gochan/keyword/create", headers=headers, data=data)
							app.logger.info(r)

							app.logger.debug(messageText)

						else:

							sendGreetingMessage(sender_id)
					else:
						app.logger.info("handling non-text!!!")
						app.logger.info("event ignored!!!")

				elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
					postbackHandler(messaging_event['postback'])

				messageCount += 1
			eventCount += 1

	app.logger.info("finish handling all event!!")
	return "ok", 200

def send_message(recipient_id, message_text):

	app.logger.info("sending message to %s !!!", recipient_id)
	app.logger.debug("message text: %s", message_text)

	data = json.dumps({
		"recipient": {
			"id": recipient_id
		},
		"message": {
			"text": message_text
		}
	})
	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	app.logger.info("sending message success")
	app.logger.debug(r.text)

def sendCreateClassResponseMessage(recipient_id, kelas_id):

	app.logger.info("sending message to %s !!!", recipient_id)

	data = json.dumps({
		"recipient":{
			"id":recipient_id
		},
		"message":{
			"attachment":{
				"type":"template",
				"payload":{
					"template_type":"generic",
					"elements":[
						{
							"title":"Kelas telah dibuat!!!",
							"subtitle":"Untuk mengundang siswa bergabung gunakan id kelas berikut: {}".format(kelas_id),
							"image_url":"https://lh3.googleusercontent.com/8PoASwhbTsHJbzSxRJxSEkrQ8F2pe8IcqNn3LonFAHRxcYWlJLBdz5uUqpsv_tugVKDZcJ8-7sesy2fwFr3z=w1366-h657",
							"buttons": [
								{
									"type": "element_share",
									"share_contents": { 
										"attachment": {
											"type": "template",
											"payload": {
												"template_type": "generic",
												"elements": [
													{
														"title": "Kelas telah dibuat!!!",
														"subtitle": "berikut id kelas yang telah dibuat {}".format(kelas_id),
														"image_url":"https://lh3.googleusercontent.com/8PoASwhbTsHJbzSxRJxSEkrQ8F2pe8IcqNn3LonFAHRxcYWlJLBdz5uUqpsv_tugVKDZcJ8-7sesy2fwFr3z=w1366-h657",
														"default_action": {
															"type": "web_url",
															"url": "http://m.me/petershats?ref=invited_by_24601"
														},
														"buttons": [
															{
																"type": "web_url",
																"url": "http://m.me/petershats?ref=invited_by_24601", 
																"title": "Gabung kelas"
															}
														]
													}
												]
											}
										}
									}
								}
							]
						}
					]
				}
			}
		}
	})
	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	app.logger.info("sending message success")
	app.logger.debug(r.text)

def sendGreetingMessage(recipient_id):
	app.logger.info("sending greeting message to %s !!!", recipient_id)

	data = json.dumps({
		"recipient": {
			"id": recipient_id
		},
		"message":{
			"attachment":{
				"type":"template",
				"payload":{
					"template_type":"generic",
					"elements":[
						{
							"title":"Selamat datang di BurhanBot",
							"image_url":"https://lh3.googleusercontent.com/8PoASwhbTsHJbzSxRJxSEkrQ8F2pe8IcqNn3LonFAHRxcYWlJLBdz5uUqpsv_tugVKDZcJ8-7sesy2fwFr3z=w1366-h657",
							"subtitle":"Aku bakal bantuin kaka, biar tau banyak hal :D",
							"buttons":[
								{
									"type":"web_url",
									"url":"https://www.facebook.com/BurhanBot-594324680958723/",
									"title":"Lihat Halaman Bot"
								},
								{
									"type":"postback",
									"title":"Bantuan",
									"payload":"HELP"
								}              
							]      
						}
					]
				}
			}
		}
	})
	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	app.logger.info("sending message success")
	app.logger.debug(r.text)

if __name__ == '__main__':
	# handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
	# handler.setLevel(logging.INFO)
	app.logger.setLevel(logging.DEBUG)
	app.run(debug=True, port=8080)