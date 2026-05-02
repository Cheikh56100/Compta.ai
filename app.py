import streamlit as st
import anthropic
import json
import re
import pandas as pd
from datetime import date, datetime
import io

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ComptaIA — Comptabilisation automatique",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS PERSONNALISÉ
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1923;
    border-right: 1px solid #1e2d3d;
}
[data-testid="stSidebar"] * { color: #c8d6e5 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextArea label {
    color: #8fa8c0 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Main area */
.main .block-container { padding-top: 1.5rem; max-width: 1100px; }

/* Logo / titre header */
.app-header {
    background: linear-gradient(135deg, #0f1923 0%, #1a2e42 100%);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.app-header .logo {
    width: 52px; height: 52px;
    background: #1e6ef5;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; font-weight: 700; color: white;
    flex-shrink: 0;
}
.app-header h1 { color: white; margin: 0; font-size: 1.5rem; font-weight: 600; }
.app-header p { color: #8fa8c0; margin: 0; font-size: 0.875rem; }

/* Cards */
.card {
    background: white;
    border: 1px solid #e8edf3;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.card-blue { border-left: 4px solid #1e6ef5; }
.card-green { border-left: 4px solid #10b981; }
.card-amber { border-left: 4px solid #f59e0b; }
.card-red { border-left: 4px solid #ef4444; }

/* Section labels */
.sec-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6b7280;
    margin-bottom: 0.5rem;
    margin-top: 0.25rem;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-green { background: #d1fae5; color: #065f46; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-red   { background: #fee2e2; color: #991b1b; }
.badge-blue  { background: #dbeafe; color: #1e40af; }
.badge-gray  { background: #f3f4f6; color: #374151; }

/* Compte lines */
.compte-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #f3f4f6;
}
.compte-row:last-child { border-bottom: none; }
.compte-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    color: #1e6ef5;
    background: #eff6ff;
    padding: 4px 8px;
    border-radius: 6px;
    min-width: 80px;
    text-align: center;
}
.compte-lib { flex: 1; font-size: 0.85rem; color: #374151; }
.compte-just { font-size: 0.75rem; color: #6b7280; margin-top: 2px; }
.compte-montant { font-weight: 600; font-size: 0.9rem; color: #111827; text-align: right; }

/* Ecriture table */
.ecr-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.ecr-table thead th {
    background: #f8fafc;
    padding: 8px 12px;
    text-align: left;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6b7280;
    border-bottom: 2px solid #e5e7eb;
}
.ecr-table tbody td {
    padding: 8px 12px;
    border-bottom: 1px solid #f3f4f6;
    color: #374151;
}
.ecr-table tbody tr:last-child td { border-bottom: none; }
.ecr-table .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #1e6ef5; }
.ecr-table .num  { text-align: right; font-variant-numeric: tabular-nums; font-weight: 500; }
.ecr-table .total-row td { background: #f8fafc; font-weight: 600; border-top: 2px solid #e5e7eb; }

/* Metric cards */
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 1.25rem; }
.metric-card {
    background: white;
    border: 1px solid #e8edf3;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-card .val { font-size: 1.4rem; font-weight: 700; color: #111827; }
.metric-card .lbl { font-size: 0.72rem; color: #6b7280; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.05em; }

/* Alert boxes */
.alert {
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 12px;
    font-size: 0.85rem;
    display: flex;
    gap: 10px;
    align-items: flex-start;
}
.alert-warn { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }
.alert-info  { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; }
.alert-succ  { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }

/* Confidence bar */
.conf-bar-bg { background: #e5e7eb; height: 4px; border-radius: 2px; margin-top: 5px; overflow: hidden; }
.conf-bar-fill { height: 100%; border-radius: 2px; }

/* History card */
.hist-card {
    background: white;
    border: 1px solid #e8edf3;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.hist-card:hover { border-color: #1e6ef5; box-shadow: 0 2px 8px rgba(30,110,245,0.1); }

/* Steps nav */
.step-nav {
    display: flex;
    gap: 0;
    background: #f8fafc;
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 1.5rem;
}
.step-btn {
    flex: 1;
    padding: 8px 12px;
    border-radius: 8px;
    text-align: center;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    color: #6b7280;
    background: transparent;
}
.step-btn.active { background: white; color: #1e6ef5; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

/* Streamlit overrides */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.45rem 1.1rem !important;
}
.stButton > button[kind="primary"] {
    background: #1e6ef5 !important;
    border-color: #1e6ef5 !important;
}
div[data-testid="stExpander"] { border-radius: 10px !important; }
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    border-radius: 8px !important;
    border-color: #d1d5db !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #1e6ef5 !important;
    box-shadow: 0 0 0 3px rgba(30,110,245,0.15) !important;
}
hr { border-color: #f3f4f6; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "profil" not in st.session_state:
    st.session_state.profil = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "page" not in st.session_state:
    st.session_state.page = "profil"
if "regles" not in st.session_state:
    st.session_state.regles = [
        {"fourn": "Metro / Transgourmet / Rungis / Grossistes alimentaires", "compte": "601 ou 607 selon contenu (matières premières ou marchandises)"},
        {"fourn": "Loyer / Bail commercial / SCI", "compte": "613100 — Loyers"},
        {"fourn": "EDF / Engie / GRDF / électricité gaz", "compte": "606100 — Énergie"},
        {"fourn": "Orange / SFR / Bouygues / Free Pro", "compte": "626000 — Frais télécom"},
        {"fourn": "Matériel et équipements (> 500 €)", "compte": "Immobilisation 2154 ou 2183 si > seuil d'immobilisation"},
        {"fourn": "Emballages / consommables cuisine", "compte": "606400 — Emballages"},
        {"fourn": "Assurance (tous types)", "compte": "616000 — Primes d'assurance"},
        {"fourn": "Expert-comptable / avocat / conseil", "compte": "622000 — Honoraires"},
    ]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
SECTEURS = {
    "restauration": "Restauration / Hôtellerie / Traiteur",
    "commerce": "Commerce de détail / Grande distribution",
    "btp": "BTP / Construction / Artisanat",
    "industrie": "Industrie / Fabrication / Production",
    "service": "Services / Conseil / Prestation intellectuelle",
    "sante": "Santé / Médical / Paramédical",
    "immobilier": "Immobilier / Agence / Promotion",
    "transport": "Transport / Logistique / Livraison",
    "autre": "Autre activité",
}

def badge_html(text, color="blue"):
    return f'<span class="badge badge-{color}">{text}</span>'

def conf_bar(certitude: str) -> str:
    mapping = {"Élevé": ("#10b981", 95), "Moyen": ("#f59e0b", 60), "À vérifier": ("#ef4444", 30)}
    color, pct = mapping.get(certitude, ("#6b7280", 50))
    return f'<div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{pct}%;background:{color};"></div></div>'

def build_system_prompt(profil: dict, regles: list) -> str:
    regles_str = "\n".join([f'- "{r["fourn"]}" → {r["compte"]}' for r in regles])
    return f"""Tu es un expert-comptable français maîtrisant parfaitement le Plan Comptable Général (PCG 2025).
Tu aides un comptable à déterminer les comptes PCG exacts pour comptabiliser des factures fournisseurs.

## PROFIL DE LA SOCIÉTÉ
- Nom : {profil.get('nom','Non renseigné')}
- Forme juridique : {profil.get('forme','SARL')}
- Secteur : {profil.get('secteur_label','Non précisé')}
- Description activité : {profil.get('desc','Non précisée')}
- Régime TVA : {profil.get('tva','Réel normal')}
- Taux TVA principal : {profil.get('taux_tva','20%')}

## RÈGLES PERSONNALISÉES DU COMPTABLE
{regles_str if regles_str else 'Aucune règle spécifique'}

## INSTRUCTIONS
1. Analyse le contenu détaillé de la facture
2. Ventile par nature de charge si la facture est mixte
3. Pour chaque ligne : numéro de compte PCG exact + libellé + montant HT estimé + justification courte + certitude
4. Génère l'écriture journal achats complète (charges + TVA déductible 44566x + 401xxx fournisseur)
5. Signale tout point d'attention : immobilisation possible, TVA non déductible, nature mixte, etc.

## FORMAT DE RÉPONSE
Réponds UNIQUEMENT en JSON valide, sans markdown, sans backticks, structure exacte :
{{
  "fournisseur_detecte": "...",
  "resume_analyse": "...",
  "nature_principale": "...",
  "ventilation": [
    {{"categorie": "...", "compte": "601000", "libelle_compte": "Achats de matières premières", "montant_ht": 0.00, "cote": "Débit", "justification": "...", "certitude": "Élevé"}}
  ],
  "ecriture_comptable": [
    {{"compte": "601000", "libelle": "...", "debit": 0.00, "credit": 0.00}}
  ],
  "tva_deductible": true,
  "compte_tva": "445660",
  "montant_tva": 0.00,
  "montant_ht_total": 0.00,
  "montant_ttc_total": 0.00,
  "points_attention": ["..."],
  "conseil_comptable": "..."
}}"""

def appeler_ia(system_prompt: str, facture_info: dict) -> dict:
    user_msg = f"""Analyse cette facture et détermine les comptes PCG :

FOURNISSEUR : {facture_info['fournisseur']}
NUMÉRO DE FACTURE : {facture_info['numero']}
DATE : {facture_info['date']}
MONTANT HT DÉCLARÉ : {facture_info['montant_ht']} €
TAUX TVA : {facture_info['taux_tva']}%
MONTANT TVA : {facture_info['montant_tva']:.2f} €
MONTANT TTC : {facture_info['montant_ttc']:.2f} €

CONTENU / LIGNES DE LA FACTURE :
{facture_info['contenu']}"""

    client = anthropic.Anthropic(api_key=st.session_state.get("api_key", ""))
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

def export_csv(result: dict, facture_info: dict) -> bytes:
    rows = []
    for e in result.get("ecriture_comptable", []):
        rows.append({
            "Date": facture_info.get("date", ""),
            "Journal": "AC",
            "Fournisseur": facture_info.get("fournisseur", ""),
            "N° Facture": facture_info.get("numero", ""),
            "Compte": e["compte"],
            "Libellé": e["libelle"],
            "Débit": e.get("debit", 0) or "",
            "Crédit": e.get("credit", 0) or "",
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 0.5rem;">
      <div style="font-size:1.1rem;font-weight:700;color:white;letter-spacing:-0.01em;">ComptaIA</div>
      <div style="font-size:0.72rem;color:#5a7a99;margin-top:2px;">Comptabilisation intelligente</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="sec-label" style="color:#5a7a99!important;">Navigation</div>', unsafe_allow_html=True)

    pages = {
        "profil": "🏢  Profil société",
        "facture": "📄  Analyser une facture",
        "resultat": "✅  Résultat",
        "historique": "🗂  Historique",
    }
    for key, label in pages.items():
        is_active = st.session_state.page == key
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = key
            st.rerun()

    st.divider()
    st.markdown('<div class="sec-label" style="color:#5a7a99!important;">Configuration API</div>', unsafe_allow_html=True)
    api_key = st.text_input("Clé Anthropic API", type="password",
                            value=st.session_state.get("api_key", ""),
                            placeholder="sk-ant-api03-...",
                            help="Votre clé API Anthropic Claude")
    if api_key:
        st.session_state.api_key = api_key
        st.markdown('<div style="color:#10b981;font-size:0.75rem;">● API configurée</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#ef4444;font-size:0.75rem;">● API non configurée</div>', unsafe_allow_html=True)

    st.divider()
    if st.session_state.history:
        st.markdown(f'<div style="font-size:0.72rem;color:#5a7a99;">{len(st.session_state.history)} facture(s) analysée(s)</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
nom_soc = st.session_state.profil.get("nom", "")
sous_titre = f"— {nom_soc}" if nom_soc else "— Configurez votre profil"
st.markdown(f"""
<div class="app-header">
  <div class="logo">📊</div>
  <div>
    <h1>ComptaIA {sous_titre}</h1>
    <p>Analyse intelligente de factures · Plan Comptable Général français · Powered by Claude AI</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE : PROFIL
# ─────────────────────────────────────────────
if st.session_state.page == "profil":
    st.markdown('<div class="sec-label">Informations générales</div>', unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de la société *", value=st.session_state.profil.get("nom", ""),
                                placeholder="Ex : Le Bistrot du Marché SARL")
        with col2:
            forme = st.selectbox("Forme juridique", ["SARL","SAS","EURL","SA","SNC","EI","Association","Autre"],
                                 index=["SARL","SAS","EURL","SA","SNC","EI","Association","Autre"].index(
                                     st.session_state.profil.get("forme","SARL")))

        col3, col4 = st.columns(2)
        with col3:
            secteur_keys = list(SECTEURS.keys())
            secteur_labels = list(SECTEURS.values())
            cur_secteur = st.session_state.profil.get("secteur", "restauration")
            cur_idx = secteur_keys.index(cur_secteur) if cur_secteur in secteur_keys else 0
            secteur = st.selectbox("Secteur d'activité *", secteur_labels, index=cur_idx)
            secteur_key = secteur_keys[secteur_labels.index(secteur)]
        with col4:
            siret = st.text_input("SIRET (optionnel)", value=st.session_state.profil.get("siret",""),
                                  placeholder="12345678900012")

        desc = st.text_area("Description de l'activité *",
                            value=st.session_state.profil.get("desc",""),
                            height=110,
                            placeholder="Décrivez votre activité en détail. Ex : Restaurant gastronomique 60 couverts. Principaux achats : denrées alimentaires (Metro, Rungis), boissons, emballages, produits d'entretien. Location de local commercial. Personnel CDI et extras...")
        st.caption("💡 Plus la description est précise, meilleure sera la suggestion de comptes par l'IA.")

    st.divider()
    st.markdown('<div class="sec-label">Paramètres fiscaux et comptables</div>', unsafe_allow_html=True)

    col5, col6, col7 = st.columns(3)
    with col5:
        tva = st.selectbox("Régime TVA", ["Réel normal","Réel simplifié","Franchise en base","Régime de la marge"],
                           index=["Réel normal","Réel simplifié","Franchise en base","Régime de la marge"].index(
                               st.session_state.profil.get("tva","Réel normal")))
    with col6:
        taux_tva = st.selectbox("Taux TVA principal", ["20%","10%","5,5%","Mixte (plusieurs taux)"],
                                index=["20%","10%","5,5%","Mixte (plusieurs taux)"].index(
                                    st.session_state.profil.get("taux_tva","20%")))
    with col7:
        seuil_immo = st.number_input("Seuil d'immobilisation (€ HT)", min_value=0, value=int(st.session_state.profil.get("seuil_immo",500)), step=100)

    st.divider()
    st.markdown('<div class="sec-label">Règles de comptabilisation personnalisées</div>', unsafe_allow_html=True)
    st.markdown("""<div class="alert alert-info">🔵 Ces règles sont transmises à l'IA pour adapter ses suggestions à votre pratique. Elles ne sont pas limitatives : l'IA analyse aussi le contenu de la facture.</div>""", unsafe_allow_html=True)

    regles_a_suppr = []
    for i, regle in enumerate(st.session_state.regles):
        col_a, col_b, col_c = st.columns([2, 2.5, 0.4])
        with col_a:
            st.session_state.regles[i]["fourn"] = st.text_input(
                f"Fournisseur / catégorie {i+1}", value=regle["fourn"],
                key=f"regle_fourn_{i}", label_visibility="collapsed",
                placeholder="Fournisseur ou catégorie")
        with col_b:
            st.session_state.regles[i]["compte"] = st.text_input(
                f"Compte {i+1}", value=regle["compte"],
                key=f"regle_compte_{i}", label_visibility="collapsed",
                placeholder="Compte PCG suggéré")
        with col_c:
            if st.button("✕", key=f"del_regle_{i}", help="Supprimer"):
                regles_a_suppr.append(i)

    for i in sorted(regles_a_suppr, reverse=True):
        st.session_state.regles.pop(i)

    if st.button("+ Ajouter une règle"):
        st.session_state.regles.append({"fourn": "", "compte": ""})
        st.rerun()

    st.divider()
    col_sv1, col_sv2 = st.columns([1, 3])
    with col_sv1:
        if st.button("💾  Enregistrer le profil", type="primary", use_container_width=True):
            if not nom:
                st.error("Le nom de la société est obligatoire.")
            elif not desc:
                st.error("La description de l'activité est obligatoire.")
            else:
                st.session_state.profil = {
                    "nom": nom, "forme": forme, "secteur": secteur_key,
                    "secteur_label": secteur, "siret": siret, "desc": desc,
                    "tva": tva, "taux_tva": taux_tva, "seuil_immo": seuil_immo,
                }
                st.success("✅ Profil enregistré ! Vous pouvez maintenant analyser des factures.")
                st.balloons()

# ─────────────────────────────────────────────
# PAGE : FACTURE
# ─────────────────────────────────────────────
elif st.session_state.page == "facture":
    if not st.session_state.profil:
        st.markdown("""<div class="alert alert-warn">⚠️ Configurez d'abord le profil de votre société dans l'onglet "Profil société".</div>""", unsafe_allow_html=True)
        if st.button("→ Aller au profil"):
            st.session_state.page = "profil"
            st.rerun()
        st.stop()

    if not st.session_state.get("api_key"):
        st.markdown("""<div class="alert alert-warn">⚠️ Renseignez votre clé API Anthropic dans la barre latérale gauche.</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Informations de la facture</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        fourn = st.text_input("Fournisseur *", placeholder="Ex : Metro Cash & Carry")
    with col2:
        num_fac = st.text_input("N° de facture", placeholder="FAC-2025-001")
    with col3:
        date_fac = st.date_input("Date de facture", value=date.today())

    col4, col5, col6 = st.columns(3)
    with col4:
        montant_ht = st.number_input("Montant HT (€) *", min_value=0.0, value=0.0, step=0.01, format="%.2f")
    with col5:
        taux_tva_fac = st.selectbox("Taux TVA", ["20", "10", "5.5", "0", "Mixte"],
                                    help="Taux TVA appliqué sur la facture")
    with col6:
        if taux_tva_fac != "Mixte":
            taux = float(taux_tva_fac)
            montant_tva = montant_ht * taux / 100
            montant_ttc = montant_ht + montant_tva
            st.metric("TVA", f"{montant_tva:.2f} €")
        else:
            montant_tva = st.number_input("Montant TVA (€)", min_value=0.0, step=0.01, format="%.2f")
            montant_ttc = montant_ht + montant_tva
            taux = 0

    if montant_ht > 0:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Montant HT", f"{montant_ht:.2f} €")
        col_m2.metric("TVA", f"{montant_tva:.2f} €")
        col_m3.metric("Montant TTC", f"{montant_ttc:.2f} €")
        col_m4.metric("Taux TVA", f"{taux_tva_fac} %")

    st.divider()
    st.markdown('<div class="sec-label">Contenu de la facture</div>', unsafe_allow_html=True)

    tab_saisie, tab_fichier, tab_exemples = st.tabs(["✏️ Saisie manuelle", "📎 Import fichier", "💡 Exemples"])

    with tab_saisie:
        contenu = st.text_area(
            "Copiez-collez les lignes de détail de la facture",
            height=160,
            placeholder="Ex :\n- Viandes et volailles fraîches : 380,00 €\n- Légumes et fruits : 195,00 €\n- Produits d'entretien (Javel, dégraissant) : 58,30 €\n- Emballages (barquettes, film plastique) : 40,00 €\n\nPlus le détail est complet, plus la ventilation sera précise.",
            key="contenu_manual"
        )

    with tab_fichier:
        uploaded = st.file_uploader("Importez un fichier texte ou CSV de la facture",
                                    type=["txt","csv"],
                                    help="Les PDF ne sont pas encore supportés directement. Extrayez le texte d'abord.")
        if uploaded:
            contenu = uploaded.read().decode("utf-8", errors="ignore")[:3000]
            st.text_area("Contenu extrait", value=contenu, height=120, disabled=True)
        else:
            contenu = st.session_state.get("contenu_manual", "")

    with tab_exemples:
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        with col_ex1:
            if st.button("🛒 Facture Metro alimentaire", use_container_width=True):
                st.session_state.ex_fourn = "Metro Cash & Carry"
                st.session_state.ex_num = "MET-2025-08741"
                st.session_state.ex_ht = 1254.80
                st.session_state.ex_contenu = """Viandes et volailles fraîches : 380,00 €
Poissons et fruits de mer : 210,00 €
Légumes et fruits frais (salade, tomates, carottes) : 195,00 €
Produits laitiers (crème, beurre, fromage AOP) : 145,00 €
Épicerie sèche (pâtes, riz, farine T55, huile) : 128,00 €
Boissons sans alcool (eau minérale, sodas, jus) : 98,50 €
Produits d'entretien (Javel, dégraissant four, éponges) : 58,30 €
Emballages et consommables (barquettes, film, gants) : 40,00 €"""
        with col_ex2:
            if st.button("🏢 Loyer commercial", use_container_width=True):
                st.session_state.ex_fourn = "SCI Les Arcades"
                st.session_state.ex_num = "LOYER-NOV-2025"
                st.session_state.ex_ht = 3200.00
                st.session_state.ex_contenu = """Loyer commercial novembre 2025 : 3 000,00 €
Charges récupérables (eau, entretien parties communes, gardiennage) : 200,00 €
Bail commercial 9 ans - Local commercial 120 m² - 15 rue du Commerce 75011 Paris"""
        with col_ex3:
            if st.button("🔧 Matériel équipement", use_container_width=True):
                st.session_state.ex_fourn = "CHR Equipements Pro"
                st.session_state.ex_num = "CHR-2025-4521"
                st.session_state.ex_ht = 8900.00
                st.session_state.ex_contenu = """Four combiné vapeur Rational SCC 62 (6 niveaux) : 7 200,00 €
Batterie de cuisine inox (casseroles, poêles, plaques) : 950,00 €
Ustensiles divers (spatules, fouets, thermomètres) : 320,00 €
Frais de livraison et mise en service : 430,00 €"""

        if st.session_state.get("ex_fourn"):
            st.info(f"Exemple chargé : {st.session_state.ex_fourn} — Rechargez la page si vous voulez saisir manuellement.")
            fourn = st.session_state.get("ex_fourn", fourn)
            num_fac = st.session_state.get("ex_num", num_fac)
            montant_ht_ex = st.session_state.get("ex_ht", montant_ht)
            contenu = st.session_state.get("ex_contenu", "")
            montant_tva = montant_ht_ex * 0.20
            montant_ttc = montant_ht_ex + montant_tva

    if "contenu_manual" in st.session_state and not contenu:
        contenu = st.session_state.contenu_manual

    st.divider()
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        lancer = st.button("🔍  Analyser avec l'IA", type="primary", use_container_width=True,
                           disabled=not st.session_state.get("api_key"))

    if lancer:
        if not fourn:
            st.error("Renseignez le nom du fournisseur.")
        elif montant_ht <= 0:
            st.error("Renseignez un montant HT valide.")
        elif not contenu or len(contenu.strip()) < 10:
            st.error("Décrivez le contenu de la facture (minimum 10 caractères).")
        else:
            ht_final = st.session_state.get("ex_ht", montant_ht) if st.session_state.get("ex_fourn") == fourn else montant_ht
            tva_val = float(taux_tva_fac) if taux_tva_fac != "Mixte" else 20.0
            tva_mnt = ht_final * tva_val / 100
            ttc_mnt = ht_final + tva_mnt

            facture_info = {
                "fournisseur": fourn, "numero": num_fac,
                "date": date_fac.strftime("%d/%m/%Y"),
                "montant_ht": ht_final, "taux_tva": tva_val,
                "montant_tva": tva_mnt, "montant_ttc": ttc_mnt,
                "contenu": contenu,
            }
            st.session_state.facture_en_cours = facture_info

            system_prompt = build_system_prompt(st.session_state.profil, st.session_state.regles)
            with st.spinner("L'IA analyse votre facture…"):
                try:
                    result = appeler_ia(system_prompt, facture_info)
                    st.session_state.last_result = result
                    st.session_state.last_facture = facture_info
                    st.session_state.history.insert(0, {
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "fourn": fourn, "num": num_fac,
                        "montant_ht": ht_final, "result": result,
                        "facture_info": facture_info,
                    })
                    st.session_state.page = "resultat"
                    st.rerun()
                except anthropic.AuthenticationError:
                    st.error("❌ Clé API invalide. Vérifiez votre clé Anthropic dans la barre latérale.")
                except json.JSONDecodeError as e:
                    st.error(f"❌ L'IA a renvoyé une réponse non parseable. Réessayez. ({e})")
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

# ─────────────────────────────────────────────
# PAGE : RÉSULTAT
# ─────────────────────────────────────────────
elif st.session_state.page == "resultat":
    if not st.session_state.last_result:
        st.info("Aucun résultat disponible. Analysez d'abord une facture.")
        if st.button("→ Analyser une facture"):
            st.session_state.page = "facture"
            st.rerun()
        st.stop()

    result = st.session_state.last_result
    fac = st.session_state.get("last_facture", {})

    # Header résultat
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        st.markdown(f"""
        <div class="card card-blue">
          <div style="font-size:1.1rem;font-weight:600;color:#111827;">{result.get('fournisseur_detecte', fac.get('fournisseur',''))}</div>
          <div style="font-size:0.85rem;color:#6b7280;margin-top:4px;">{result.get('resume_analyse','')}</div>
          <div style="margin-top:8px;">{badge_html(result.get('nature_principale','—'), 'blue')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r2:
        ht = result.get("montant_ht_total", fac.get("montant_ht", 0))
        tva = result.get("montant_tva", fac.get("montant_tva", 0))
        ttc = result.get("montant_ttc_total", fac.get("montant_ttc", 0))
        st.metric("Montant HT", f"{ht:.2f} €")
        st.metric("TVA déductible", f"{tva:.2f} €")
        st.metric("Total TTC", f"{ttc:.2f} €")

    # Ventilation
    ventilation = result.get("ventilation", [])
    if ventilation:
        st.divider()
        st.markdown('<div class="sec-label">Ventilation par nature de charges</div>', unsafe_allow_html=True)

        html_vent = '<div class="card">'
        for v in ventilation:
            cert = v.get("certitude", "Moyen")
            badge_color = "green" if cert == "Élevé" else ("amber" if cert == "Moyen" else "red")
            html_vent += f"""
            <div class="compte-row">
              <div>
                <div class="compte-num">{v.get('compte','')}</div>
              </div>
              <div class="compte-lib">
                <div><strong>{v.get('libelle_compte','')}</strong> — <span style="color:#6b7280;">{v.get('categorie','')}</span></div>
                <div class="compte-just">{v.get('justification','')}</div>
                {conf_bar(cert)}
              </div>
              <div style="text-align:right;min-width:130px;">
                <div class="compte-montant">{v.get('montant_ht',0):.2f} €</div>
                <div style="margin-top:4px;">{badge_html(cert, badge_color)}</div>
              </div>
            </div>"""
        html_vent += "</div>"
        st.markdown(html_vent, unsafe_allow_html=True)

    # Écriture comptable
    ecriture = result.get("ecriture_comptable", [])
    if ecriture:
        st.markdown('<div class="sec-label">Écriture comptable — Journal des achats</div>', unsafe_allow_html=True)

        total_d = sum(e.get("debit", 0) or 0 for e in ecriture)
        total_c = sum(e.get("credit", 0) or 0 for e in ecriture)
        rows_html = ""
        for e in ecriture:
            d = e.get("debit", 0) or 0
            c = e.get("credit", 0) or 0
            rows_html += f"""
            <tr>
              <td class="mono">{e.get('compte','')}</td>
              <td>{e.get('libelle','')}</td>
              <td class="num">{f"{d:.2f} €" if d else ""}</td>
              <td class="num">{f"{c:.2f} €" if c else ""}</td>
            </tr>"""

        st.markdown(f"""
        <div class="card">
          <table class="ecr-table">
            <thead>
              <tr><th>Compte</th><th>Libellé</th><th style="text-align:right;">Débit</th><th style="text-align:right;">Crédit</th></tr>
            </thead>
            <tbody>
              {rows_html}
              <tr class="total-row">
                <td colspan="2">Total</td>
                <td class="num">{total_d:.2f} €</td>
                <td class="num">{total_c:.2f} €</td>
              </tr>
            </tbody>
          </table>
        </div>""", unsafe_allow_html=True)

        if abs(total_d - total_c) < 0.02:
            st.markdown("""<div class="alert alert-succ">✅ Écriture équilibrée — Débit = Crédit</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="alert alert-warn">⚠️ Déséquilibre détecté : Débit {total_d:.2f} € ≠ Crédit {total_c:.2f} € — Vérifiez les montants.</div>""", unsafe_allow_html=True)

    # Points d'attention
    points = result.get("points_attention", [])
    if points:
        st.markdown('<div class="sec-label">Points d'attention</div>', unsafe_allow_html=True)
        warn_html = '<div class="alert alert-warn"><div><strong>⚠️ À vérifier :</strong><ul style="margin-top:6px;padding-left:18px;">'
        for p in points:
            warn_html += f"<li style='margin-bottom:4px;'>{p}</li>"
        warn_html += "</ul></div></div>"
        st.markdown(warn_html, unsafe_allow_html=True)

    # Conseil
    conseil = result.get("conseil_comptable", "")
    if conseil:
        st.markdown(f"""<div class="alert alert-info">💡 <strong>Conseil :</strong> {conseil}</div>""", unsafe_allow_html=True)

    # Export
    st.divider()
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        csv_data = export_csv(result, fac)
        st.download_button(
            "⬇️  Exporter en CSV",
            data=csv_data,
            file_name=f"ecriture_{fac.get('fournisseur','facture').replace(' ','_')}_{fac.get('date','').replace('/','')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_e2:
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️  Exporter en JSON",
            data=json_data.encode("utf-8"),
            file_name="resultat_analyse.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_e3:
        if st.button("📄  Analyser une autre facture", use_container_width=True):
            if "ex_fourn" in st.session_state:
                del st.session_state["ex_fourn"]
            st.session_state.page = "facture"
            st.rerun()

# ─────────────────────────────────────────────
# PAGE : HISTORIQUE
# ─────────────────────────────────────────────
elif st.session_state.page == "historique":
    st.markdown('<div class="sec-label">Factures analysées</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("Aucune facture analysée pour le moment. Commencez par analyser une facture.")
    else:
        total_ttc = sum(h.get("result", {}).get("montant_ttc_total", h.get("montant_ht", 0)) for h in st.session_state.history)
        col_h1, col_h2 = st.columns(2)
        col_h1.metric("Factures analysées", len(st.session_state.history))
        col_h2.metric("Total TTC cumulé", f"{total_ttc:.2f} €")
        st.divider()

        for i, h in enumerate(st.session_state.history):
            r = h.get("result", {})
            comptes = ", ".join([v.get("compte","") for v in r.get("ventilation",[])][:3])
            with st.expander(f"📄 {h['fourn']} — {h.get('num','—')} — {h['date']} — {h['montant_ht']:.2f} € HT"):
                col_hd1, col_hd2 = st.columns([2,1])
                with col_hd1:
                    st.markdown(f"**Fournisseur :** {h['fourn']}")
                    st.markdown(f"**Résumé :** {r.get('resume_analyse','—')}")
                    st.markdown(f"**Comptes utilisés :** `{comptes}`")
                with col_hd2:
                    if st.button("Recharger ce résultat", key=f"reload_{i}"):
                        st.session_state.last_result = h["result"]
                        st.session_state.last_facture = h.get("facture_info", {})
                        st.session_state.page = "resultat"
                        st.rerun()

        if st.button("🗑  Effacer l'historique"):
            st.session_state.history = []
            st.rerun()
