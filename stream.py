import streamlit as st
import os
import time
from mylib_montant import functions

# Interface Streamlit
st.title("Détection d'informations dans les documents")

# Créer des onglets
tab1, tab2 = st.tabs(["Traitement Normal", "Traitement par Page"])

# Onglet 1 : Traitement Normal
with tab1:
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

                # Simuler une progression lors du traitement
                for percent_complete in range(0, 100, 10):
                    status_text.text(f"Analyse en cours : {percent_complete}%")
                    progress_bar.progress(percent_complete)
                    time.sleep(0.5)  # Simuler un délai

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
        display_adeli = st.checkbox('Num. Adeli')
        display_rpps = st.checkbox('Num. RPPS')
        display_postal_codes = st.checkbox('Codes postaux')
        display_percentages = st.checkbox('Pourcentages')
        display_num_tel = st.checkbox('Numéro téléphone')
        display_montants = st.checkbox('Montants')

    # Effectuer le traitement pour tous les critères (même si les cases ne sont pas cochées)
    if uploaded_file:
        # Utiliser le texte OCR déjà stocké
        final_text = st.session_state['ocr_text']

        # Variables pour stocker les résultats
        dates = []
        siren = None
        siret = None
        postal_codes = []
        percentages = []
        num_tels = []
        montants = []
        num_adelis = []
        num_rpps = []
        somme_montants = 0

        # Détection et suppression des éléments dans le texte extrait
        dates, final_text = functions.extract_dates(final_text)
        siret, final_text = functions.extract_siret(final_text)
        siren = functions.extract_siren_from_siret(siret)
        num_adelis, final_text = functions.extract_adeli(final_text)
        num_rpps, final_text = functions.extract_rpps(final_text)
        postal_codes, final_text = functions.extract_postal_codes(final_text)
        percentages, final_text = functions.extract_percentages(final_text)
        num_tels, final_text = functions.extract_telephone(final_text)
        montants, somme_montants, final_text = functions.extract_montants(final_text)

        # Résultats complets (utilisé pour JSON final)
        results = {
            "dates": ["/".join(date) for date in dates],  # Reformater les dates pour être lisibles
            "siren": siren,  # Prendre seulement les numéros Siren
            "siret": siret,  # Prendre seulement les numéros Siret
            "num_Adeli": num_adelis,
            "num_RPPS": num_rpps,
            "postal_codes": postal_codes,
            "percentages": percentages,
            "numero_telephone": num_tels,
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

        if display_adeli:
            st.write("#### ADELI")
            st.write(results["num_Adeli"])

        if display_rpps:
            st.write("#### RPPS")
            st.write(results["num_RPPS"])

        if display_postal_codes:
            st.write("#### Codes postaux")
            st.write(results["postal_codes"])

        if display_percentages:
            st.write("#### Pourcentages")
            st.write(results["percentages"])

        if display_num_tel:
            st.write("#### Numéro téléphone")
            st.write(results["numero_telephone"])

        if display_montants:
            st.write("#### Montants")
            st.write(results["montants"])
            # st.write(f"Somme des montants: {results['somme_montants']} €")

# Onglet 2 : Traitement par Page
with tab2:
    uploaded_file_page = st.file_uploader("Choisissez un fichier (PDF ou image)", type=['pdf', 'jpg', 'jpeg', 'png'], key='page_uploader')

    if uploaded_file_page:
        # Réinitialiser l'état si un nouveau fichier est téléchargé
        if 'last_uploaded_file_page' not in st.session_state or st.session_state['last_uploaded_file_page'] != uploaded_file_page.name:
            st.session_state['ocr_text_page'] = None
            st.session_state['images_page'] = None
            st.session_state['last_uploaded_file_page'] = uploaded_file_page.name  # Mettre à jour avec le nouveau fichier

        # Sauvegarder le fichier dans l'état de session pour éviter qu'il soit relu à chaque interaction
        if st.session_state['ocr_text_page'] is None:
            file_extension_page = os.path.splitext(uploaded_file_page.name)[1].lower()  # Obtenir l'extension du fichier

            # Afficher une barre de chargement
            progress_bar_page = st.progress(0)  # Initialise la barre de progression
            status_text_page = st.empty()

            # Simuler une progression lors du traitement
            for percent_complete in range(0, 100, 10):
                status_text_page.text(f"Analyse en cours : {percent_complete}%")
                progress_bar_page.progress(percent_complete)
                time.sleep(0.5)

            # Traitement du fichier pour afficher l'image si nécessaire
            images_page, ocr_text_page = functions.process_file_page_per_page(uploaded_file_page, file_extension_page)

            # Sauvegarder le texte OCR et les images dans l'état de session
            st.session_state['ocr_text_page'] = ocr_text_page
            st.session_state['images_page'] = images_page

            # Compléter la barre de progression à 100%
            progress_bar_page.progress(100)
            status_text_page.text("Analyse terminée")

        # Dictionnaire pour stocker les résultats JSON
        results_json = {}

        # Cases à cocher pour les critères
        st.write("### Sélectionnez les éléments à afficher par page")
        display_dates_page = st.checkbox('Dates', value=True)
        display_siren_page = st.checkbox('SIREN', value=True)
        display_siret_page = st.checkbox('SIRET', value=True)
        display_adeli_page = st.checkbox('Num. Adeli', value=True)
        display_rpps_page = st.checkbox('Num. RPPS', value=True)
        display_postal_codes_page = st.checkbox('Codes postaux', value=True)
        display_percentages_page = st.checkbox('Pourcentages', value=True)
        display_num_tel_page = st.checkbox('Numéro téléphone', value=True)
        display_montants_page = st.checkbox('Montants', value=True)

        # Afficher les images et extraire les données pour chaque page
        for index, img in enumerate(st.session_state['images_page']):
            st.image(img, caption=f'Page {index + 1} du document', use_column_width=True)
            
            # Récupérer le texte pour la page actuelle
            final_text_page = st.session_state['ocr_text_page'][index]  # Utiliser le texte OCR spécifique à la page

            # Variables pour stocker les résultats de la page actuelle
            dates_page = []
            siren_page = None
            siret_page = None
            postal_codes_page = []
            percentages_page = []
            num_tels_page = []
            montants_page = []
            num_adelis_page = []
            num_rpps_page = []
            somme_montants_page = 0

            # Extraction des informations pour la page actuelle
            dates_page, final_text_page = functions.extract_dates(final_text_page)
            siret_page, final_text_page = functions.extract_siret(final_text_page)
            siren_page = functions.extract_siren_from_siret(siret_page)
            num_adelis_page, final_text_page = functions.extract_adeli(final_text_page)
            num_rpps_page, final_text_page = functions.extract_rpps(final_text_page)
            postal_codes_page, final_text_page = functions.extract_postal_codes(final_text_page)
            percentages_page, final_text_page = functions.extract_percentages(final_text_page)
            num_tels_page, final_text_page = functions.extract_telephone(final_text_page)
            montants_page, somme_montants_page, final_text_page = functions.extract_montants(final_text_page)

            # Résultats pour la page actuelle
            results_page = {
                "dates": ["/".join(date) for date in dates_page],  # Reformater les dates pour être lisibles
                "siren": siren_page,
                "siret": siret_page,
                "num_adeli": num_adelis_page,
                "num_rpps": num_rpps_page,
                "postal_codes": postal_codes_page,
                "percentages": percentages_page,
                "numero_telephone": num_tels_page,
                "montants": montants_page,
                "somme_montants": somme_montants_page
            }

            # Afficher uniquement les résultats correspondant aux cases cochées
            st.write("### Résultats pour la Page", index + 1)
            if display_dates_page:
                st.write("#### Dates")
                st.write(results_page["dates"])

            if display_siren_page:
                st.write("#### SIREN")
                st.write(results_page["siren"])

            if display_siret_page:
                st.write("#### SIRET")
                st.write(results_page["siret"])

            if display_adeli_page:
                st.write("#### ADELI")
                st.write(results_page["num_adeli"])

            if display_rpps_page:
                st.write("#### RPPS")
                st.write(results_page["num_rpps"])

            if display_postal_codes_page:
                st.write("#### Codes postaux")
                st.write(results_page["postal_codes"])

            if display_percentages_page:
                st.write("#### Pourcentages")
                st.write(results_page["percentages"])

            if display_num_tel_page:
                st.write("#### Numéro téléphone")
                st.write(results_page["numero_telephone"])

            if display_montants_page:
                st.write("#### Montants")
                st.write(results_page["montants"])
                # st.write(f"Somme des montants: {results_page['somme_montants']} €")
