import streamlit as st
import re
import easyocr
import os
from mylib_montant import functions
import json
from PIL import Image
from io import BytesIO  # Pour gérer les fichiers en mémoire
import tempfile  # Pour créer un fichier temporaire
import time

# Interface Streamlit
st.title("Détection d'informations dans les documents")

# Diviser l'écran en deux colonnes
col1, col2 = st.columns(2)

# Colonne gauche : Télécharger le fichier
with col1:
    uploaded_file = st.file_uploader("Choisissez un fichier (PDF ou image)", type=['pdf', 'jpg', 'jpeg', 'png'])

    if uploaded_file:
        # Réinitialiser l'état si un nouveau fichier est téléchargé
        if 'last_uploaded_file' not in st.session_state or st.session_state['last_uploaded_file'] != uploaded_file.name:
            st.session_state['ocr_text'] = None
            st.session_state['images'] = None
            st.session_state['last_uploaded_file'] = uploaded_file.name  # Mettre à jour avec le nouveau fichier

        # Sauvegarder le fichier dans l'état de session pour éviter qu'il soit relu à chaque interaction
        if st.session_state['ocr_text'] is None:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()  # Obtenir l'extension du fichier

            # Afficher une barre de chargement
            progress_bar = st.progress(0)  # Initialise la barre de progression
            status_text = st.empty()

            # Simuler une progression lors du traitement (ajouter des étapes réalistes ici)
            for percent_complete in range(0, 100, 10):
                status_text.text(f"Analyse en cours : {percent_complete}%")
                progress_bar.progress(percent_complete)
                # Simuler un délai pour chaque étape (ici, une petite pause)
                time.sleep(0.5)  # Vous pouvez ajuster le délai selon le besoin

            # Traitement du fichier pour afficher l'image si nécessaire
            images, ocr_text = functions.process_file(uploaded_file, file_extension)
            
            # Sauvegarder le texte OCR et les images dans l'état de session
            st.session_state['ocr_text'] = ocr_text
            st.session_state['images'] = images

            # Compléter la barre de progression à 100%
            progress_bar.progress(100)
            status_text.text("Analyse terminée")

        # Afficher les images (pour PDF, toutes les pages converties en images)
        for img in st.session_state['images']:
            st.image(img, caption='Page du document', use_column_width=True)

# Colonne droite : Cases à cocher pour les critères
with col2:
    st.write("### Sélectionnez les éléments à afficher")
    display_dates = st.checkbox('Dates')
    display_siren = st.checkbox('SIREN')
    display_siret = st.checkbox('SIRET')
    display_postal_codes = st.checkbox('Codes postaux')
    display_percentages = st.checkbox('Pourcentages')
    display_montants = st.checkbox('Montants')

# Effectuer le traitement pour tous les critères (même si les cases ne sont pas cochées)
if uploaded_file:
    # Utiliser le texte OCR déjà stocké
    final_text = st.session_state['ocr_text']

    # Variables pour stocker les résultats
    dates = []
    siren_siret = []
    postal_codes = []
    percentages = []
    montants = []
    somme_montants = 0

    # Détection et suppression des éléments dans le texte extrait
    dates, final_text = functions.extract_dates(final_text)
    siren, final_text = functions.extract_siren(final_text)
    siret, final_text = functions.extract_siret(final_text)
    postal_codes, final_text = functions.extract_postal_codes(final_text)
    percentages, final_text = functions.extract_percentages(final_text)
    montants,somme_montants, final_text = functions.extract_montants(final_text)

    # Résultats complets (utilisé pour JSON final)
    results = {
        "dates": ["/".join(date) for date in dates],  # Reformater les dates pour être lisibles
        "siren": [s[0] for s in siren],  # Prendre seulement les numéros Siren
        "siret": [s[0] for s in siret],  # Prendre seulement les numéros Siret
        "postal_codes": postal_codes,
        "percentages": percentages,
        "montants": montants,
        "somme_montants": somme_montants
    }

    # Afficher uniquement les résultats correspondant aux cases cochées
    st.write("### Résultats")
    if display_dates:
        st.write("#### Dates")
        st.write(results["dates"])

    if display_siren:
        st.write("#### SIREN")
        st.write(results["siren"])

    if display_siret:
        st.write("#### SIRET")
        st.write(results["siret"])

    if display_postal_codes:
        st.write("#### Codes postaux")
        st.write(results["postal_codes"])

    if display_percentages:
        st.write("#### Pourcentages")
        st.write(results["percentages"])

    if display_montants:
        st.write("#### Montants")
        st.write(results["montants"])
        st.write(f"Somme des montants: {results['somme_montants']} €")
