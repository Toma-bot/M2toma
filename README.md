# 🗂️ Carte interactive des coworkings à Paris

Cette application Streamlit permet de visualiser les espaces de coworking à Paris (Île-de-France) extraits automatiquement depuis le site [leportagesalarial.com](https://www.leportagesalarial.com/coworking/).

## 🚀 Fonctionnalités

- 📄 Scraping des informations de contact (adresse, téléphone, mail, site)
- 🌍 Géocodage automatique des adresses avec OpenStreetMap
- 🗺️ Carte interactive avec Folium
- 🔍 Filtres par nom ou arrondissement
- 📥 Export des résultats filtrés en CSV

## ▶️ Lancer l'application localement

```bash
# Cloner le dépôt
git clone https://github.com/<TON_UTILISATEUR>/coworking-paris-app.git
cd coworking-paris-app

# (Optionnel) Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # sous Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
