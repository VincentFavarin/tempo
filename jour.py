import requests
import os

# Récupérer l'URL du webhook depuis les secrets GitHub
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Message à envoyer
message = "Hello World!"

# Fonction pour envoyer des notifications à Discord
def send_discord_notification(message):
    if DISCORD_WEBHOOK_URL is None:
        print("Erreur : Le webhook Discord n'est pas configuré.")
        return
    
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification envoyée à Discord avec succès")
    else:
        print(f"Erreur lors de l'envoi de la notification Discord : {response.text}")

# Appel de la fonction pour envoyer le message "Hello World"
send_discord_notification(message)
