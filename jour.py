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
send_discord_notification("Début de l'exécution du script de scraping sur Wikipédia.")

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

# Accéder à l'URL de la page d'accueil de Wikipédia
print("Accès à la page d'accueil de Wikipédia...")
send_discord_notification("Accès à la page d'accueil de Wikipédia.")
driver.get('https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal')

# Attendre que le titre de l'article principal soit présent
wait = WebDriverWait(driver, 30)  # Attendre jusqu'à 30 secondes pour que les éléments apparaissent

# Initialisation des variables pour le titre de l'article
article_title = None

try:
    print("Récupération du titre de l'article principal de Wikipédia...")
    send_discord_notification("Récupération du titre de l'article principal de Wikipédia...")

    # Utiliser les attentes explicites pour attendre que l'élément contenant le titre de l'article principal apparaisse
    article_title_element = wait.until(EC.presence_of_element_located((By.ID, 'mp-tfa-h2')))
    
    # Extraire et afficher le titre de l'article
    article_title = article_title_element.text
    print(f"Article principal : {article_title}")

    # Notification après récupération des informations
    send_discord_notification(f"Titre de l'article principal de Wikipédia : {article_title}")
    
except Exception as e:
    print(f"Erreur lors de la récupération des données : {str(e)}")
    send_discord_notification(f"Erreur lors de la récupération des données : {str(e)}")

# Fermer le navigateur
driver.quit()

# Notification de fin de script
send_discord_notification("Script terminé.")
print("Script terminé.")
