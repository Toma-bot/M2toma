import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
import folium
from streamlit_folium import folium_static

# ----------- Scraping et géocodage -----------

BASE_URL = "https://www.leportagesalarial.com/coworking/"

@st.cache_data
def get_coworking_links():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        st.error("Erreur lors du chargement des liens.")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    paris_section = soup.find('h3', string="Coworking Paris – Île de France :")
    if not paris_section:
        st.warning("Section Paris – Île de France non trouvée.")
        return []
    links = paris_section.find_next('ul').find_all('a', href=True)
    return [(link.text.strip(), link['href']) for link in links]

def clean_info(text, prefix):
    pattern = re.compile(rf'{prefix}\s*:\s*', flags=re.IGNORECASE)
    return pattern.sub('', text).strip()

def get_coordinates(address, max_retries=2, timeout=10):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': 'CoworkingScraper - Python app'}
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            return None, None
        except requests.exceptions.RequestException:
            sleep(1)
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
    except Exception:
        return None

@st.cache_data
def load_data():
    links = get_coworking_links()
    results = []
    progress_bar = st.progress(0)
    total = len(links)

    for i, (name, url) in enumerate(links):
        info = get_contact_info(name, url)
        if info:
            adresse = info.get('Adresse')
            if adresse:
                lat, lon = get_coordinates(adresse)
                sleep(1)
                info['Latitude'] = lat
                info['Longitude'] = lon
            else:
                info['Latitude'], info['Longitude'] = None, None
            results.append(info)
        progress_bar.progress((i + 1) / total)

    progress_bar.empty()
    st.success("✅ Chargement des données terminé.")
    return pd.DataFrame(results)

# ----------- Interface utilisateur -----------

st.set_page_config(page_title="Carte des Coworkings Parisiens", layout="wide")
st.title("🗂️ Coworkings Paris – Île-de-France")
st.write("Données extraites automatiquement du site *leportagesalarial.com* avec coordonnées géographiques.")

df = load_data()

# Filtres
nom = st.text_input("🔍 Rechercher un coworking par nom :")
arrondissement = st.selectbox(
    "🏙️ Filtrer par arrondissement (extrait de l'adresse) :",
    options=["Tous"] + sorted(set(df["Adresse"].dropna().apply(lambda x: x.split(',')[-1].strip())))
)

filtered_df = df.copy()
if nom:
    filtered_df = filtered_df[filtered_df["Nom du Coworking"].str.contains(nom, case=False, na=False)]

if arrondissement != "Tous":
    filtered_df = filtered_df[filtered_df["Adresse"].str.contains(arrondissement)]

st.subheader(f"📋 Résultats ({len(filtered_df)} coworkings trouvés)")
st.dataframe(filtered_df, use_container_width=True)

# Téléchargement CSV
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger les résultats filtrés en CSV",
    data=csv_data,
    file_name='coworkings_paris_filtrés.csv',
    mime='text/csv'
)

# Carte interactive
st.subheader("📍 Carte des Coworkings")
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

for _, row in filtered_df.dropna(subset=["Latitude", "Longitude"]).iterrows():
    popup_text = f"<b>{row['Nom du Coworking']}</b><br>{row['Adresse']}<br>{row.get('Téléphone', '')}"
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=popup_text,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

folium_static(m)
