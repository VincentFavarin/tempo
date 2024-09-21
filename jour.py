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

# Attendre 5 secondes pour laisser le temps à la page de se charger dynamiquement
time.sleep(5)

# Capturer le HTML complet de la page après le chargement
page_html = driver.page_source
with open("page_source.html", "w", encoding="utf-8") as f:
    f.write(page_html)

# Envoyer une notification pour indiquer que le HTML a été récupéré
send_discord_notification("Le HTML de la page Tempo a été capturé et enregistré dans 'page_source.html'.")

# Fermer le navigateur
driver.quit()

# Notification de fin de script
send_discord_notification("Script terminé.")
print("Script terminé.")
