import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Utiliser les secrets GitHub pour Discord Webhook et Home Assistant Token
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
HA_TOKEN = os.getenv('HA_TOKEN')

# Vérification si les secrets sont bien récupérés
print(f"Webhook Discord: {'configuré' if DISCORD_WEBHOOK_URL else 'non configuré'}")
print(f"Token Home Assistant: {'configuré' if HA_TOKEN else 'non configuré'}")

# Envoyer une notification au début du script
send_discord_notification("Début de l'exécution du script.")

# URL de Home Assistant
HA_URL = 'http://homeassistant.local:8123/api/states/'

# Fonction pour envoyer des notifications à Discord
def send_discord_notification(message):
    print(f"Envoi de la notification : {message}")
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification envoyée à Discord avec succès")
    else:
        print(f"Erreur lors de l'envoi de la notification Discord : {response.text}")

# Notification après la création de la fonction
send_discord_notification("Fonction send_discord_notification créée.")

# Fonction pour envoyer des données à Home Assistant avec des tentatives répétées jusqu'à succès
def update_sensor(entity_id, state, attributes={}):
    print(f"Mise à jour du capteur : {entity_id} avec l'état {state}")
    url = HA_URL + entity_id
    headers = {
        'Authorization': f'Bearer {HA_TOKEN}',
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

# Notification après la création de la fonction update_sensor
send_discord_notification("Fonction update_sensor créée.")

# Configuration de Selenium pour utiliser ChromeDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Envoyer une notification après la configuration de Selenium
send_discord_notification("Selenium configuré avec ChromeDriver.")

service = Service(ChromeDriverManager().install())
service.log_path = "chromedriver.log"
service.verbose = True
driver = webdriver.Chrome(service=service, options=chrome_options)

# Accéder à l'URL
print("Accès à la page EDF Tempo...")
send_discord_notification("Accès à la page EDF Tempo.")
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
        print("Récupération des informations Tempo d'EDF...")
        send_discord_notification("Récupération des informations Tempo d'EDF...")
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

        # Notification après récupération des informations
        send_discord_notification(f"Aujourd'hui ({today_date}): {today_status} - Demain ({tomorrow_date}): {tomorrow_status}")
        break  # Sortir de la boucle si les éléments sont trouvés
    except Exception as e:
        attempt_count += 1  # Incrémenter le compteur de tentatives
        print(f"Tentative {attempt_count} : Échec lors de la récupération des données : {str(e)}")
        send_discord_notification(f"Tentative {attempt_count} : Échec lors de la récupération des données : {str(e)}")
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

# Notification de fin de script
send_discord_notification("Script terminé.")
print("Script terminé.")
