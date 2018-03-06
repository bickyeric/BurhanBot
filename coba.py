import json
import requests

sender_id = 1778216532196834
params = {
		"access_token": "EAAEsAwadNEgBAJp1YUcVfB73oBO5gm7KfoUa8VIs30ibzXO8kHB3nGmQ1t05bbD829BMHtLFVZBKiuB3eLDRs3yvtIQUPuuUvBEZBNj2VZBO4VoeojlZCJ6RlRmJEzcqdN3RqgQjCAwloVamWpZAsl7Gkfkicpa2NBKipEhLrUK5Dp45eLzdT"
}
headers = {
	"Content-Type": "application/json"
}
def send_message(recipient_id, message_text):

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
							"title":"ALERT",
							"image_url":"https://backend-bot.000webhostapp.com/100.jpg",
							"subtitle":"there's someone you don't know in front of your door"
						}
					]
				}
			}
		}
	})
	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	print r.text

if __name__ == '__main__':
	send_message(1778216532196834, "fakyu")
