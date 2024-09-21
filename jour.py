import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Récupérer l'URL du webhook Discord et le token Home Assistant depuis les variables d'environnement
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
HA_TOKEN = os.getenv('HA_TOKEN')
HA_URL = 'http://homeassistant.local:8123/api/states/'

# Fonction pour envoyer un message via Discord
def send_to_discord(message):
    if DISCORD_WEBHOOK_URL:
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("Message envoyé avec succès.")
        else:
            print(f"Erreur lors de l'envoi du message : {response.status_code}")
    else:
        print("DISCORD_WEBHOOK_URL n'est pas défini.")

# Fonction pour mettre à jour l'état d'un capteur dans Home Assistant
def update_sensor(entity_id, state, attributes={}):
    url = HA_URL + entity_id
    headers = {
        'Authorization': f'Bearer {HA_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'state': state,
        'attributes': attributes,
    }
    max_attempts = 5
    attempt_count = 0
    
    while attempt_count < max_attempts:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f'{entity_id} mis à jour avec succès : {state}')
            break
        else:
            attempt_count += 1
            print(f'Tentative {attempt_count} : Erreur lors de la mise à jour de {entity_id} : {response.text}')
            time.sleep(5)

    if attempt_count == max_attempts:
        print(f"Échec après {max_attempts} tentatives de mise à jour de {entity_id}")

# Configuration de Selenium avec WebDriver Manager
chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL de la page que tu veux récupérer
url = "https://particulier.edf.fr/fr/accueil/gestion-contrat/options/tempo.html#/"
driver.get(url)

max_attempts = 5
attempt_count = 0

while attempt_count < max_attempts:
    try:
        time.sleep(5)

        # Récupérer la couleur du jour actuel
        aujourd_hui = driver.find_element(By.CSS_SELECTOR, ".jtp-tempodays__item--blue, .jtp-tempodays__item--red, .jtp-tempodays__item--white")
        couleur_aujourd_hui = aujourd_hui.text.split("\n")[2]
        jour_aujourd_hui = aujourd_hui.text.split("\n")[1]

        # Récupérer la couleur du jour suivant
        demain = driver.find_element(By.CSS_SELECTOR, ".jtp-tempodays__item--indet")
        jour_demain = demain.text.split("\n")[1]
        couleur_demain = "Couleur à venir"

        # Préparer le message formaté
        message = (
            f"Aujourd'hui ({jour_aujourd_hui}), on est en {couleur_aujourd_hui}.\n"
            f"Demain ({jour_demain}), on sera en {couleur_demain}.\n"
            f"Informations récupérées après {attempt_count + 1} tentative(s)."
        )

        # Envoyer le message à Discord
        send_to_discord(message)

        # Mise à jour des entités Home Assistant
        update_sensor('sensor.tempo_aujourdhui', couleur_aujourd_hui, {
            'friendly_name': 'Tempo Aujourd\'hui',
            'icon': 'mdi:calendar-today',
        })
        update_sensor('sensor.tempo_demain', couleur_demain, {
            'friendly_name': 'Tempo Demain',
            'icon': 'mdi:calendar-tomorrow',
        })

        break

    except Exception as e:
        attempt_count += 1
        print(f"Tentative {attempt_count} : Échec lors de la récupération des données")
        time.sleep(300)

if attempt_count == max_attempts:
    print(f"Échec après {max_attempts} tentatives de récupération des données")
    send_to_discord(f"Échec après {max_attempts} tentatives de récupération des informations sur la page")

# Fermer le navigateur
driver.quit()
