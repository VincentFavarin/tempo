import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Utiliser les secrets GitHub pour Discord Webhook
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Vérification si les secrets sont bien récupérés
print(f"Webhook Discord: {'configuré' if DISCORD_WEBHOOK_URL else 'non configuré'}")

# Fonction pour envoyer des notifications à Discord
def send_discord_notification(message):
    print(f"Envoi de la notification : {message}")
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification envoyée à Discord avec succès")
    else:
        print(f"Erreur lors de l'envoi de la notification Discord : {response.text}")

# Envoyer une notification au début du script (après la définition de la fonction)
send_discord_notification("Début de l'exécution du script de scraping sur la page EDF Tempo.")

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

# Accéder à l'URL de la page EDF Tempo
print("Accès à la page EDF Tempo...")
send_discord_notification("Accès à la page EDF Tempo.")
driver.get('https://particulier.edf.fr/fr/accueil/gestion-contrat/options/tempo.html#/')

# Attendre que les éléments "Aujourd'hui" et "Demain" soient présents
wait = WebDriverWait(driver, 30)  # Attendre jusqu'à 30 secondes pour que les éléments apparaissent

# Initialisation des variables pour les informations d'aujourd'hui et de demain
today_status, tomorrow_status = None, None

try:
    print("Récupération des informations d'aujourd'hui et de demain sur Tempo...")
    send_discord_notification("Récupération des informations d'aujourd'hui et de demain sur Tempo...")

    # Utiliser les attentes explicites pour attendre que les éléments contenant les informations apparaissent
    today_info = wait.until(EC.presence_of_element_located((By.ID, 'a11y-today')))
    tomorrow_info = wait.until(EC.presence_of_element_located((By.ID, 'a11y-tomorrow')))

    # Extraire et afficher les informations pour aujourd'hui
    today_date = today_info.find_element(By.TAG_NAME, 'strong').text
    today_status = today_info.find_element(By.TAG_NAME, 'span').text
    print(f"Aujourd'hui ({today_date}): {today_status}")

    # Extraire et afficher les informations pour demain
    tomorrow_date = tomorrow_info.find_element(By.TAG_NAME, 'strong').text
    tomorrow_status = tomorrow_info.find_element(By.TAG_NAME, 'span').text
    print(f"Demain ({tomorrow_date}): {tomorrow_status}")

    # Notification après récupération des informations
    send_discord_notification(f"Aujourd'hui ({today_date}): {today_status} - Demain ({tomorrow_date}): {tomorrow_status}")
    
except Exception as e:
    print(f"Erreur lors de la récupération des données : {str(e)}")
    send_discord_notification(f"Erreur lors de la récupération des données : {str(e)}")

# Fermer le navigateur
driver.quit()

# Notification de fin de script
send_discord_notification("Script terminé.")
print("Script terminé.")
