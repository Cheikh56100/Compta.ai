# ComptaIA — Comptabilisation automatique de factures

Application Streamlit intelligente pour la comptabilisation automatique de factures fournisseurs, alimentée par Claude AI (Anthropic).

## Fonctionnalités

- **Profil société** : Configurez votre activité, régime TVA, règles personnalisées
- **Analyse IA** : L'IA lit le contenu de la facture et détermine les comptes PCG exacts
- **Ventilation automatique** : Factures mixtes ventilées par nature (matières premières, marchandises, charges, etc.)
- **Écriture comptable complète** : Journal des achats avec charges + TVA déductible + 401 fournisseur
- **Points d'attention** : Immobilisations possibles, TVA non déductible, etc.
- **Export CSV / JSON** : Intégrable dans Sage, Cegid, MyUnisoft, etc.
- **Historique** : Toutes les factures analysées conservées en session

## Installation locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement sur Streamlit Cloud

1. Créez un compte sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez votre dépôt GitHub contenant ces fichiers
3. Déployez l'application
4. Dans les **Secrets** Streamlit, vous pouvez pré-configurer la clé API :
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-..."
   ```
   Puis dans `app.py`, ajoutez en haut :
   ```python
   import os
   if "api_key" not in st.session_state:
       st.session_state.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
   ```

## Structure des fichiers

```
comptabilisateur/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
└── README.md           # Ce fichier
```

## Utilisation

1. **Étape 1 — Profil** : Renseignez le nom, secteur, description de votre société et vos règles comptables
2. **Étape 2 — Facture** : Saisissez ou collez le contenu d'une facture
3. **Étape 3 — Résultat** : L'IA analyse et propose les comptes PCG avec justifications
4. **Export** : Téléchargez l'écriture en CSV pour votre logiciel comptable

## Clé API Anthropic

Obtenez votre clé sur [console.anthropic.com](https://console.anthropic.com). 
Le modèle utilisé est `claude-opus-4-5` (le plus précis pour la comptabilité).

## Points d'attention PCG

- Les achats alimentaires Metro sont ventilés : 601 (matières premières cuisine) vs 607 (marchandises revente)
- Les loyers vont en 613100, les charges récupérables en 614xxx
- Le matériel > seuil d'immobilisation (configurable) est signalé
- La TVA non déductible (cadeaux, véhicules de tourisme) est détectée et signalée
