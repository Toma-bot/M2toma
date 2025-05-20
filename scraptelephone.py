import requests
from bs4 import BeautifulSoup
import pandas as pd

# Fonction pour récupérer les informations de contact depuis un site web
def get_contact_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Chercher la section "Contacter" (la balise <h2> contenant "Contacter")
        contact_section = soup.find('h2', string=lambda text: text and 'Contacter' in text)
        
        if contact_section:
            # Extraire le nom de l'entreprise qui suit "Contacter"
            company_name = contact_section.get_text(strip=True).replace('Contacter', '').strip()
            
            # Trouver le <ul> sous cette section pour extraire les informations
            contact_list = contact_section.find_next('ul')
            if contact_list:
                # Initialiser un dictionnaire pour stocker les informations
                contact_info = {
                    'Nom de l\'Entreprise': company_name,
                    'Adresse': None,
                    'Téléphone': None,
                    'Site': None,
                    'Mail': None
                }

                # Parcourir tous les <li> de cette liste
                for li in contact_list.find_all('li'):
                    # Récupérer le texte de chaque <li> et essayer de trouver les informations spécifiques
                    text = li.get_text(strip=True)

                    # Nettoyage pour l'adresse
                    if 'Adresse' in text:
                        # Enlever le préfixe "Adresse:" et garder la valeur
                        contact_info['Adresse'] = clean_info(text, "Adresse")
                    # Nettoyage pour le téléphone
                    elif 'Téléphone' in text:
                        # Enlever le préfixe "Téléphone:" et garder la valeur
                        contact_info['Téléphone'] = clean_info(text, "Téléphone")
                    # Nettoyage pour le site
                    elif 'Site' in text:
                        # Enlever le préfixe "Site:" et garder la valeur
                        contact_info['Site'] = clean_info(text, "Site")
                    # Récupérer l'email
                    elif 'Mail' in text:
                        contact_info['Mail'] = clean_info(text, "Mail")

                return contact_info
        return None  # Si la section "Contacter" n'est pas trouvée
    except Exception as e:
        print(f"Erreur pour {url}: {e}")
        return None

# Fonction pour nettoyer les informations
def clean_info(text, prefix):
    # Supprime le préfixe spécifique, comme "Adresse:", "Téléphone:", "Site:" et garde la valeur propre
    if prefix + ":" in text:
        return text.split(f"{prefix} :")[-1].strip()
    return text.strip()

# Chargement du fichier CSV contenant les URLs
csv_file_path = r'C:\Users\desgr\Documents\Progra\py\coworking_paris_idf.csv'  # Chemin du fichier CSV
df = pd.read_csv(csv_file_path)

# Liste pour stocker les résultats
results = []

# Parcourir chaque URL du fichier CSV et récupérer les informations de contact
for index, row in df.iterrows():
    name = row['Coworking Name']
    url = row['URL']
    contact_info = get_contact_info(url)
    
    if contact_info:
        # Ajouter l'URL et les informations de contact dans les résultats
        contact_info['URL'] = url  # Garder l'URL pour référence si nécessaire
        results.append(contact_info)

# Convertir la liste en DataFrame
results_df = pd.DataFrame(results)

# Supprimer les colonnes non désirées
results_df = results_df.drop(columns=['URL'])

# Sauvegarder les résultats dans un fichier Excel
output_file_path = r'C:\Users\desgr\Documents\Progra\py\coworking_contact_info.xlsx'
results_df.to_excel(output_file_path, index=False)

print(f"Les informations de contact ont été sauvegardées dans {output_file_path}")