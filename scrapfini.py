import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep

BASE_URL = "https://www.leportagesalarial.com/coworking/"
OUTPUT_FILE = r'C:\Users\desgr\Documents\Progra\py\coworking_paris_idf_info.xlsx'


def get_coworking_links():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print("Erreur de requête")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    paris_section = soup.find('h3', string="Coworking Paris – Île de France :")
    if not paris_section:
        print("Section Paris – Île de France non trouvée.")
        return []

    links = paris_section.find_next('ul').find_all('a', href=True)
    return [(link.text.strip(), link['href']) for link in links]


def clean_info(text, prefix):
    pattern = re.compile(rf'{prefix}\s*:\s*', flags=re.IGNORECASE)
    return pattern.sub('', text).strip()


def get_coordinates(address):
    """
    Utilise Nominatim (OpenStreetMap) pour géocoder une adresse et retourner latitude/longitude.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'CoworkingScraper - Python script'}
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return float(lat), float(lon)
        else:
            return None, None
    except Exception as e:
        print(f"Erreur de géocodage pour l'adresse {address}: {e}")
        return None, None


def get_contact_info(name, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        contact_section = soup.find('h2', string=lambda t: t and 'Contacter' in t)
        if not contact_section:
            return None

        company_name = contact_section.get_text(strip=True).replace('Contacter', '').strip()
        contact_list = contact_section.find_next('ul')
        if not contact_list:
            return None

        contact_info = {
            'Nom du Coworking': name,
            'Nom de l\'Entreprise': company_name,
            'Adresse': None,
            'Téléphone': None,
            'Mail': None,
            'Site': None
        }

        for li in contact_list.find_all('li'):
            text = li.get_text(strip=True)
            if 'Adresse' in text:
                contact_info['Adresse'] = clean_info(text, "Adresse")
            elif 'Téléphone' in text:
                contact_info['Téléphone'] = clean_info(text, "Téléphone")
            elif 'Site' in text:
                contact_info['Site'] = clean_info(text, "Site")
            elif 'Mail' in text or '@' in text:
                contact_info['Mail'] = clean_info(text, "Mail")

        return contact_info

    except Exception as e:
        print(f"Erreur pour {url}: {e}")
        return None


def main():
    links = get_coworking_links()
    print(f"{len(links)} liens récupérés.")

    results = []
    for name, url in links:
        info = get_contact_info(name, url)
        if info:
            adresse = info.get('Adresse')
            if adresse:
                lat, lon = get_coordinates(adresse)
                sleep(1)  # Pause d’1 seconde pour respecter le rate limit de Nominatim
                info['Latitude'] = lat
                info['Longitude'] = lon
            else:
                info['Latitude'] = None
                info['Longitude'] = None
            results.append(info)

    if results:
        df = pd.DataFrame(results)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"Fichier Excel généré avec succès : {OUTPUT_FILE}")
    else:
        print("Aucune donnée à sauvegarder.")


if __name__ == "__main__":
    main()
