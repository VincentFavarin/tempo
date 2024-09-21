from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from selenium.webdriver.chrome.options import Options
import os
from datetime import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
service.log_path = "chromedriver.log"
service.verbose = True
driver = webdriver.Chrome(service=service, options=chrome_options)

HA_URL = 'http://homeassistant.local:8123/api/states/'
TOKEN = os.getenv('HA_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Fonction pour envoyer des notifications à Discord
def send_discord_notification(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification envoyée à Discord avec succès")
    else:
        print(f"Erreur lors de l'envoi de la notification Discord : {response.text}")

# Fonction pour envoyer des données à Home Assistant avec des tentatives répétées jusqu'à succès
def update_sensor(entity_id, state, attributes={}):
    url = HA_URL + entity_id
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'state': state,
        'attributes': attributes,
    }
    max_attempts = 5  # Limite le nombre de tentatives pour éviter une boucle infinie
    attempt_count = 0  # Compteur de tentatives actuel
    
    while attempt_count < max_attempts:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f'{entity_id} mis à jour avec succès : {state}')
            send_discord_notification(f"Mise à jour de {entity_id} réussie : {state}")
            break  # Sortir de la boucle si la mise à jour est réussie
        else:
            attempt_count += 1  # Incrémenter le compteur de tentatives
            print(f'Tentative {attempt_count} : Erreur lors de la mise à jour de {entity_id} : {response.text}')
            send_discord_notification(f"Tentative {attempt_count} : Erreur lors de la mise à jour de {entity_id} : {response.text}")
            time.sleep(5)  # Attendre un peu avant de réessayer, pour éviter de surcharger le serveur

    if attempt_count == max_attempts:
        print(f"Échec après {max_attempts} tentatives de mise à jour de {entity_id}")
        send_discord_notification(f"Échec après {max_attempts} tentatives de mise à jour de {entity_id}")

# Configuration de Selenium pour utiliser ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Accéder à l'URL
driver.get('https://particulier.edf.fr/fr/accueil/gestion-contrat/options/tempo.html#/')

# Attendre que la page soit chargée et que le contenu dynamique soit généré
time.sleep(2)

# Initialisation des variables pour les informations d'aujourd'hui et de demain
today_date, today_status, tomorrow_date, tomorrow_status = None, None, None, None

# Limite le nombre de tentatives pour éviter une boucle infinie
max_attempts = 5
attempt_count = 0

# Boucle jusqu'à ce que les éléments soient trouvés ou que le nombre maximal de tentatives soit atteint
while attempt_count < max_attempts:
    try:
        # Trouver les éléments contenant les informations pour aujourd'hui et demain
        today_info = driver.find_element(By.ID, 'a11y-today')
        tomorrow_info = driver.find_element(By.ID, 'a11y-tomorrow')

        # Extraire et afficher les informations
        today_date = today_info.find_element(By.TAG_NAME, 'strong').text
        today_status = today_info.find_element(By.TAG_NAME, 'span').text
        print(f"Aujourd'hui ({today_date}): {today_status}")

        tomorrow_date = tomorrow_info.find_element(By.TAG_NAME, 'strong').text
        tomorrow_status = tomorrow_info.find_element(By.TAG_NAME, 'span').text
        print(f"Demain ({tomorrow_date}): {tomorrow_status}")
        break  # Sortir de la boucle si les éléments sont trouvés
    except Exception as e:
        attempt_count += 1  # Incrémenter le compteur de tentatives
        print(f"Tentative {attempt_count} : Échec lors de la récupération des données")
        time.sleep(300)  # Attendre un peu avant de réessayer, pour éviter de surcharger le serveur

if attempt_count == max_attempts:
    print(f"Échec après {max_attempts} tentatives de récupération des données")
    send_discord_notification(f"Échec après {max_attempts} tentatives de récupération des informations sur la page")

# Fermer le navigateur
driver.quit()

# Mise à jour des entités Home Assistant
update_sensor('sensor.tempo_aujourdhui', today_status, {
    'friendly_name': 'Tempo Aujourd\'hui',
    'icon': 'mdi:calendar-today',
})

update_sensor('sensor.tempo_demain', tomorrow_status, {
    'friendly_name': 'Tempo Demain',
    'icon': 'mdi:calendar-tomorrow',
})

#15 12 * * * /usr/bin/xvfb-run --server-args="-screen 0, 1024x768x24" /usr/bin/python3 /home/ubuntu/Code/jour.py >> /home/ubuntu/Code/jour.log 2>&1
#scp /home/ubuntuwsl/tempo/jour.py ubuntu@192.168.0.151:~/Code/