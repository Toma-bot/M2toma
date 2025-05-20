import requests
from bs4 import BeautifulSoup
import csv

# URL du site à scraper
url = "https://www.leportagesalarial.com/coworking/"

# Fonction pour récupérer les liens
def get_coworking_links():
    # Envoie une requête HTTP pour obtenir le contenu de la page
    response = requests.get(url)
    
    # Vérifie si la requête a réussi
    if response.status_code != 200:
        print(f"Erreur")
        return []

    # Parse le contenu de la page avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Trouve toutes les listes <ul> pour Paris Île-de-France (section spécifique)
    paris_section = soup.find('h3', string="Coworking Paris – Île de France :")
    if not paris_section:
        print("Section 'Coworking Paris – Île de France' non trouvée.")
        return []

    # Trouve tous les liens dans la section
    links = paris_section.find_next('ul').find_all('a', href=True)
    
    # Extrait les URLs des liens
    coworking_links = [link['href'] for link in links]

    return coworking_links

# Fonction pour sauvegarder les liens dans un fichier CSV
def save_links_to_csv(links, filename):
    # Ouvre (ou crée) le fichier CSV et écrit les liens
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # En-tête du fichier CSV
        writer.writerow(['Coworking Name', 'URL'])
        
        # Écriture de chaque lien dans le fichier
        for link in links:
            writer.writerow([link.split("/")[-2], link])  # Nom et URL

    print(f"Les liens ont été sauvegardés dans {filename}")

# Récupérer les liens
coworking_links = get_coworking_links()

# Si des liens ont été récupérés, les sauvegarder dans un fichier CSV
if coworking_links:
    save_links_to_csv(coworking_links, r"C:\Users\desgr\Documents\Progra\py\coworking_paris_idf.csv")
else:
    print("Aucun lien trouvé.")