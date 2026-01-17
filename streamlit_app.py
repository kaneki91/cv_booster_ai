"""
Application Streamlit pour l'optimisation de CV avec Claude API
"""

import streamlit as st
from claude_service import ClaudeService
from pdf_utils import extract_text_from_pdf, validate_pdf, markdown_to_pdf, clean_text
from prompts import NICHES
import traceback

# Configuration de la page
st.set_page_config(
    page_title="CV Optimizer - Claude AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé moderne
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        animation: fadeIn 0.8s ease-in;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        font-weight: 300;
        margin-bottom: 1rem;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        color: white;
        font-weight: 600;
        backdrop-filter: blur(10px);
        margin-top: 1rem;
    }
    
    /* Cards */
    .custom-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Score Box - Amélioré */
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .score-box::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 3s ease-in-out infinite;
    }
    
    .score-value {
        font-size: 5rem;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .score-label {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        font-weight: 600;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Criterion Box - Amélioré */
    .criterion-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #3498db;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .criterion-box:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .criterion-box h4 {
        color: #2c3e50;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
    }
    
    /* Buttons - Améliorés */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        padding: 1rem 2rem;
        border-radius: 12px;
        border: none;
        font-size: 1.2rem;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Progress Bar */
    .progress-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        margin: 0.8rem 0;
        padding: 0.8rem;
        border-radius: 8px;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    
    .progress-step.active {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
    }
    
    .progress-step.completed {
        background: linear-gradient(135deg, rgba(46, 213, 115, 0.1) 0%, rgba(72, 219, 251, 0.1) 100%);
        border-left: 4px solid #2ed573;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.1) rotate(180deg); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Tabs - Stylisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed #667eea;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        animation: slideIn 0.5s ease;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* Exemple Avant/Après */
    .example-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .example-box:hover {
        border-color: #667eea;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.15);
    }
    
    .example-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .before-badge {
        background: #ffebee;
        color: #c62828;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .after-badge {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Compteur freemium */
    .trial-counter {
        background: rgba(255,255,255,0.15);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    .trial-number {
        font-size: 2rem;
        font-weight: 800;
        color: white;
    }
    
    .premium-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.3);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialise les variables de session"""
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'cv_text' not in st.session_state:
        st.session_state.cv_text = None
    # Compteur d'essais gratuits
    if 'free_trials' not in st.session_state:
        st.session_state.free_trials = 3


def display_header():
    """Affiche l'en-tête moderne de l'application"""
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🚀 CV Optimizer AI</div>
        <div class="hero-subtitle">Transformez votre CV en un atout professionnel avec l'intelligence artificielle Claude</div>
        <div class="hero-badge">✨ Propulsé par Claude 3 Haiku</div>
    </div>
    """, unsafe_allow_html=True)


def display_score(score: int):
    """Affiche le score global dans un box stylisé moderne"""
    # Détermine la couleur en fonction du score
    if score >= 80:
        color_start, color_end = "#2ed573", "#7bed9f"
        emoji = "🎉"
        label = "Excellent"
    elif score >= 60:
        color_start, color_end = "#667eea", "#764ba2"
        emoji = "👍"
        label = "Bien"
    else:
        color_start, color_end = "#ff6b6b", "#ee5a6f"
        emoji = "💪"
        label = "À améliorer"
    
    st.markdown(f"""
    <div class="score-box" style="background: linear-gradient(135deg, {color_start} 0%, {color_end} 100%);">
        <div class="score-value">{emoji} {score}/100</div>
        <div class="score-label">{label} - Score Global de votre CV</div>
    </div>
    """, unsafe_allow_html=True)




def display_example_before_after():
    """Affiche un exemple Avant/Après pour inciter à tester"""
    with st.expander("💡 Exemple Réel (anonymisé) - Voir la transformation", expanded=False):
        st.markdown("### 🔄 Transformation d'une expérience professionnelle")
        
        col_before, col_after = st.columns(2)
        
        with col_before:
            st.markdown("""
            <div class="example-box">
                <div class="example-title">
                    <span class="before-badge">❌ AVANT (Score: 52/100)</span>
                </div>
                
                **Développeur Web** chez TechCorp  
                *Janvier 2022 - Décembre 2023*
                
                - Développement de sites web
                - Travail en équipe avec d'autres développeurs
                - Participation aux réunions projet
                - Maintenance du code existant
                - Résolution de bugs
                - Utilisation de technologies modernes
                
                **Compétences:** HTML, CSS, JavaScript, React
            </div>
            """, unsafe_allow_html=True)
        
        with col_after:
            st.markdown("""
            <div class="example-box">
                <div class="example-title">
                    <span class="after-badge">✅ APRÈS (Score: 89/100)</span>
                </div>
                
                **Développeur Full-Stack React** chez TechCorp  
                *Janvier 2022 - Décembre 2023*
                
                - 🚀 Conçu et déployé **5 applications web** générant **+150K€ de CA**
                - 💡 Optimisé les performances, réduisant le temps de chargement de **40%**
                - 👥 Encadré **2 développeurs juniors** et conduit **15+ code reviews/mois**
                - 🔧 Résolu **200+ tickets critiques** avec un taux de satisfaction de **98%**
                - 📊 Implémenté des **dashboards analytics** utilisés par **1000+ clients**
                - ⚡ Migré l'architecture legacy vers **React/Node.js**, améliorant la scalabilité
                
                **Stack maîtrisée:** React • Node.js • TypeScript • MongoDB • Docker • CI/CD
            </div>
            """, unsafe_allow_html=True)
        
        st.success("📈 **Résultat : Score passé de 52/100 à 89/100 en 20 secondes !**")
        st.info("💡 **Améliorations clés :** Quantification (+6 chiffres), Verbes d'action, Impact business, Stack détaillée")


def main():
    """Fonction principale de l'application"""
    init_session_state()
    display_header()
    
    # Exemple Avant/Après (incitation à tester)
    display_example_before_after()
    
    # Sidebar - Informations et configuration
    with st.sidebar:
        st.markdown("### ℹ️ À propos")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
        Cette application utilise <b>Claude AI</b> pour transformer votre CV en un document professionnel impactant.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✨ Fonctionnalités")
        st.markdown("""
        - 📊 **Analyse complète** avec scoring
        - ✍️ **Réécriture optimisée** par IA
        - 💡 **Suggestions personnalisées**
        - 📥 **Export PDF professionnel**
        - 🎯 **8 niches spécialisées**
        """)
        
        st.markdown("---")
        st.markdown("### 🎁 Essais Gratuits")
        
        # Compteur d'essais gratuits
        trials_remaining = st.session_state.free_trials
        
        if trials_remaining > 0:
            st.markdown(f"""
            <div class="trial-counter">
                <div class="trial-number">{trials_remaining}/3</div>
                <div style='font-size: 0.9rem; margin-top: 0.5rem;'>Analyses restantes</div>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"✨ {trials_remaining} analyse{'s' if trials_remaining > 1 else ''} gratuite{'s' if trials_remaining > 1 else ''} disponible{'s' if trials_remaining > 1 else ''}")
        else:
            st.markdown("""
            <div class="premium-box">
                <h3 style='margin: 0 0 0.5rem 0;'>🔓 Passez Premium</h3>
                <p style='margin: 0.5rem 0; font-size: 0.95rem;'>Analyses illimitées</p>
                <div style='font-size: 1.8rem; font-weight: 800; margin: 1rem 0;'>9,99€/mois</div>
                <small>✨ Bientôt disponible ✨</small>
            </div>
            """, unsafe_allow_html=True)
            st.warning("⚠️ Essais gratuits épuisés. Rechargez la page pour réinitialiser (démo).")
        
        st.markdown("---")
        st.markdown("### 🔑 Configuration")
        
        # Vérification de la clé API
        try:
            service = ClaudeService()
            st.markdown("""
            <div style='background: rgba(46, 213, 115, 0.2); padding: 0.8rem; border-radius: 8px; margin: 1rem 0;'>
            ✅ <b>Clé API active</b><br>
            <small>Prêt à analyser vos CV</small>
            </div>
            """, unsafe_allow_html=True)
        except ValueError as e:
            st.markdown("""
            <div style='background: rgba(255, 107, 107, 0.2); padding: 0.8rem; border-radius: 8px; margin: 1rem 0;'>
            ❌ <b>Clé API manquante</b><br>
            <small>Ajoutez votre clé dans .env</small>
            </div>
            """, unsafe_allow_html=True)
            st.code("ANTHROPIC_API_KEY=votre_clé", language="bash")
            return
        
        st.markdown("---")
        st.markdown("### 🛠️ Stack Technique")
        st.markdown("""
        <div style='font-size: 0.9rem;'>
        • <b>Claude 3 Haiku</b> - IA d'analyse<br>
        • <b>Streamlit</b> - Interface web<br>
        • <b>pdfplumber</b> - Extraction PDF<br>
        • <b>ReportLab</b> - Génération PDF
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; font-size: 0.85rem; opacity: 0.8; margin-top: 2rem;'>
        Made with ❤️ using Claude AI<br>
        <small>Version 1.0.0</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Zone principale
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="card-title">📤 Étape 1 : Import du CV</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Uploadez votre CV au format PDF",
            type=['pdf'],
            help="Le CV doit contenir du texte extractible (pas uniquement des images)"
        )
        
        if uploaded_file:
            # Validation du PDF
            is_valid, error_message = validate_pdf(uploaded_file)
            
            if not is_valid:
                st.error(f"❌ {error_message}")
                return
            
            st.success(f"✅ CV chargé : {uploaded_file.name}")
            
            # Extraction du texte
            try:
                cv_text = extract_text_from_pdf(uploaded_file)
                cv_text = clean_text(cv_text)
                st.session_state.cv_text = cv_text
                
                with st.expander("👁️ Aperçu du texte extrait"):
                    st.text_area("Texte du CV", cv_text, height=200, disabled=True)
            
            except Exception as e:
                st.error(f"❌ Erreur d'extraction : {str(e)}")
                return
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 Étape 2 : Configuration</div>', unsafe_allow_html=True)
        
        # Sélection de la niche
        niche_options = {key: value["nom"] for key, value in NICHES.items()}
        selected_niche_key = st.selectbox(
            "Choisissez votre niche cible",
            options=list(niche_options.keys()),
            format_func=lambda x: niche_options[x],
            help="Sélectionnez le secteur pour lequel vous optimisez votre CV"
        )
        
        # Affichage du focus de la niche
        niche_focus = NICHES[selected_niche_key]["focus"]
        st.info(f"**Focus :** {niche_focus}")
        
        # Offre d'emploi (optionnel)
        st.markdown("**Offre d'emploi** (optionnel)")
        job_offer = st.text_area(
            "Collez l'offre d'emploi pour une optimisation ciblée",
            height=150,
            placeholder="Intitulé du poste, missions, compétences requises...",
            help="Plus l'offre est détaillée, plus l'optimisation sera précise"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bouton d'analyse
        if uploaded_file and st.session_state.cv_text:
            st.markdown('<div class="card-title">🚀 Étape 3 : Analyse</div>', unsafe_allow_html=True)
            
            # Vérification des essais restants
            if st.session_state.free_trials <= 0:
                st.error("❌ Vous avez épuisé vos 3 essais gratuits")
                st.info("🔓 Passez Premium pour des analyses illimitées (9,99€/mois - Bientôt disponible)")
                if st.button("🔄 Recharger la page (démo)", type="secondary"):
                    st.session_state.free_trials = 3
                    st.rerun()
            else:
                if st.button("🚀 Analyser et Optimiser Mon CV", type="primary"):
                    # Décrémente le compteur
                    st.session_state.free_trials -= 1
                    
                    # Progress bar
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    try:
                        service = ClaudeService()
                        
                        # Étape 1 : Analyse
                        progress_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-step active">⏳ Analyse du CV en cours...</div>
                            <div class="progress-step">⏸️ Réécriture optimisée</div>
                            <div class="progress-step">⏸️ Génération des suggestions</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        analysis_result = service.analyser_cv(
                            cv_text=st.session_state.cv_text,
                            niche=selected_niche_key,
                            offre=job_offer if job_offer.strip() else None
                        )
                        
                        if not analysis_result["success"]:
                            st.error(f"❌ Erreur : {analysis_result.get('error', 'Erreur inconnue')}")
                            return
                        
                        # Étape 2 : Améliorations sections
                        progress_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-step completed">✅ Analyse terminée</div>
                            <div class="progress-step active">⏳ Améliorations section par section...</div>
                            <div class="progress-step">⏸️ Checklist d'actions</div>
                            <div class="progress-step">⏸️ Analyse ATS</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        ameliorations_result = service.generer_ameliorations_sections(
                            cv_text=st.session_state.cv_text,
                            niche=selected_niche_key,
                            offre=job_offer if job_offer.strip() else None
                        )
                        
                        if not ameliorations_result["success"]:
                            st.error(f"❌ Erreur : {ameliorations_result.get('error', 'Erreur inconnue')}")
                            if ameliorations_result.get('raw_response'):
                                with st.expander("🔍 Réponse brute (debug)"):
                                    st.code(ameliorations_result['raw_response'], language="text")
                            return
                        
                        # Étape 3 : Checklist
                        progress_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-step completed">✅ Analyse terminée</div>
                            <div class="progress-step completed">✅ Améliorations générées</div>
                            <div class="progress-step active">⏳ Checklist d'actions...</div>
                            <div class="progress-step">⏸️ Analyse ATS</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        checklist_result = service.generer_checklist_actions(
                            cv_text=st.session_state.cv_text,
                            niche=selected_niche_key,
                            offre=job_offer if job_offer.strip() else None
                        )
                        
                        if not checklist_result["success"]:
                            st.error(f"❌ Erreur : {checklist_result.get('error', 'Erreur inconnue')}")
                            if checklist_result.get('raw_response'):
                                with st.expander("🔍 Réponse brute (debug)"):
                                    st.code(checklist_result['raw_response'], language="text")
                            return
                        
                        # Étape 4 : Analyse ATS
                        progress_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-step completed">✅ Analyse terminée</div>
                            <div class="progress-step completed">✅ Améliorations générées</div>
                            <div class="progress-step completed">✅ Checklist créée</div>
                            <div class="progress-step active">⏳ Analyse ATS...</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        ats_result = service.analyser_ats(
                            cv_text=st.session_state.cv_text,
                            niche=selected_niche_key,
                            offre=job_offer if job_offer.strip() else None
                        )
                        
                        if not ats_result["success"]:
                            st.error(f"❌ Erreur : {ats_result.get('error', 'Erreur inconnue')}")
                            if ats_result.get('raw_response'):
                                with st.expander("🔍 Réponse brute (debug)"):
                                    st.code(ats_result['raw_response'], language="text")
                            return
                        
                        # Succès !
                        progress_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-step completed">✅ Analyse terminée</div>
                            <div class="progress-step completed">✅ Améliorations générées</div>
                            <div class="progress-step completed">✅ Checklist créée</div>
                            <div class="progress-step completed">✅ Analyse ATS terminée</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Stockage des résultats
                        total_tokens = (
                            analysis_result.get("tokens_used", 0) +
                            ameliorations_result.get("tokens_used", 0) +
                            checklist_result.get("tokens_used", 0) +
                            ats_result.get("tokens_used", 0)
                        )
                        
                        st.session_state.results = {
                            "analysis": analysis_result["analysis"],
                            "ameliorations": ameliorations_result["ameliorations"],
                            "checklist": checklist_result["checklist"],
                            "analyse_ats": ats_result["analyse_ats"]
                        }
                        st.session_state.analysis_done = True
                        
                        st.success("🎉 Analyse complète terminée avec succès !")
                        st.info(f"💬 Tokens utilisés : {total_tokens} (~{total_tokens/1000:.2f}k)")
                        
                        # Message essais restants
                        trials_left = st.session_state.free_trials
                        if trials_left > 0:
                            st.info(f"🎁 Il vous reste {trials_left} analyse{'s' if trials_left > 1 else ''} gratuite{'s' if trials_left > 1 else ''}")
                        else:
                            st.warning("⚠️ C'était votre dernier essai gratuit ! Passez Premium pour continuer.")
                        
                        st.balloons()
                        
                    except Exception as e:
                        # En cas d'erreur, on rembourse l'essai
                        st.session_state.free_trials += 1
                        st.error(f"❌ Erreur : {str(e)}")
                        st.info("ℹ️ Votre essai a été remboursé suite à l'erreur")
                        with st.expander("🔍 Détails de l'erreur"):
                            st.code(traceback.format_exc())
    
    with col2:
        st.markdown('<div class="card-title">📊 Résultats de l\'analyse</div>', unsafe_allow_html=True)
        
        if st.session_state.analysis_done and st.session_state.results:
            results = st.session_state.results
            analysis = results["analysis"]
            
            # Affichage du score
            display_score(analysis["score_global"])
            
            # Nouveaux onglets axés sur l'amélioration
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Score & Analyse", "✅ Plan d'Action", "📝 Améliorations Détaillées", "🤖 Optimisation ATS"])
            
            with tab1:
                st.markdown("### 📈 Vue d'ensemble")
                
                # Métriques en ligne
                metrics_cols = st.columns(len(analysis["criteres"]))
                for idx, criterion in enumerate(analysis["criteres"]):
                    with metrics_cols[idx]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{criterion['score']}</div>
                            <div class="metric-label">{criterion['nom'].split()[0]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🔍 Analyse détaillée par critère")
                
                # Critères avec accordéon visuel
                for idx, criterion in enumerate(analysis["criteres"]):
                    with st.expander(f"{'🟢' if criterion['score'] >= 16 else '🟡' if criterion['score'] >= 12 else '🔴'} {criterion['nom']} - {criterion['score']}/20", expanded=idx==0):
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if criterion.get('points_forts'):
                                st.markdown("**✅ Points forts**")
                                for point in criterion['points_forts']:
                                    st.markdown(f"- {point}")
                        
                        with col_b:
                            if criterion.get('ameliorations'):
                                st.markdown("**🔸 À améliorer**")
                                for point in criterion['ameliorations']:
                                    st.markdown(f"- {point}")
                
                # Adéquation avec l'offre
                if analysis.get("adequation_offre"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 🎯 Adéquation avec l'offre")
                    st.info(analysis["adequation_offre"])
                
                # Recommandations générales
                if analysis.get("recommandations_generales"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 💡 Recommandations clés")
                    for idx, reco in enumerate(analysis["recommandations_generales"], 1):
                        st.markdown(f"""
                        <div style='background: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #667eea;'>
                        <b>{idx}.</b> {reco}
                        </div>
                        """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("### ✅ Votre Plan d'Action Personnalisé")
                
                checklist = results.get("checklist", {})
                
                if checklist:
                    # Progression estimée
                    score_actuel = checklist.get("score_actuel", 0)
                    score_potentiel = checklist.get("score_potentiel", 0)
                    temps_total = checklist.get("temps_total_estime", "N/A")
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;'>
                        <h3 style='color: white; margin: 0;'>🎯 Votre Potentiel d'Amélioration</h3>
                        <div style='display: flex; justify-content: space-around; margin-top: 1.5rem;'>
                            <div style='text-align: center;'>
                                <div style='font-size: 2.5rem; font-weight: bold;'>{score_actuel}</div>
                                <div style='opacity: 0.9;'>Score actuel</div>
                            </div>
                            <div style='font-size: 3rem; opacity: 0.7;'>→</div>
                            <div style='text-align: center;'>
                                <div style='font-size: 2.5rem; font-weight: bold;'>{score_potentiel}</div>
                                <div style='opacity: 0.9;'>Score potentiel</div>
                            </div>
                        </div>
                        <div style='text-align: center; margin-top: 1rem; font-size: 1.1rem;'>
                            ⏱️ Temps estimé : <b>{temps_total}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Actions par priorité
                    actions = checklist.get("actions", [])
                    
                    for idx, action in enumerate(actions, 1):
                        priorite = action.get("priorite", "")
                        priorite_color = {
                            "URGENTE": "#ff6b6b",
                            "IMPORTANTE": "#ffa500",
                            "AMÉLIORATION": "#4CAF50"
                        }.get(priorite, "#888")
                        
                        priorite_emoji = {
                            "URGENTE": "🔴",
                            "IMPORTANTE": "🟡",
                            "AMÉLIORATION": "🟢"
                        }.get(priorite, "⚪")
                        
                        with st.expander(f"{priorite_emoji} Action {idx} : {action.get('titre', 'Action')} (+{action.get('impact_points', 0)} pts)", expanded=(idx==1)):
                            st.markdown(f"**Priorité :** <span style='color: {priorite_color}; font-weight: bold;'>{priorite}</span>", unsafe_allow_html=True)
                            st.markdown(f"**Impact estimé :** +{action.get('impact_points', 0)} points")
                            st.markdown(f"**Temps estimé :** {action.get('temps_estime', 'N/A')}")
                            
                            st.markdown("<br>**📝 Diagnostic :**", unsafe_allow_html=True)
                            st.info(action.get('description', ''))
                            
                            st.markdown("**🎯 Action concrète à réaliser :**", unsafe_allow_html=True)
                            action_text = action.get('action_concrete', '')
                            st.success(action_text)
                            
                            # Bouton copier
                            if st.button(f"📋 Copier cette action", key=f"copy_action_{idx}"):
                                st.code(action_text, language="text")
                                st.success("✅ Texte prêt à copier !")
                else:
                    st.warning("Aucune checklist disponible")
            
            with tab3:
                st.markdown("### 📝 Améliorations Section par Section")
                st.info("💡 **Mode d'emploi** : Pour chaque section, copiez la version améliorée et remplacez dans votre CV original.")
                
                ameliorations_data = results.get("ameliorations", {})
                ameliorations = ameliorations_data.get("ameliorations", [])
                
                if ameliorations:
                    for idx, amelioration in enumerate(ameliorations, 1):
                        section = amelioration.get("section", "Section")
                        titre = amelioration.get("titre", "")
                        impact = amelioration.get("impact_score", 0)
                        
                        with st.expander(f"📌 {section} : {titre} (Impact: +{impact} pts)", expanded=(idx==1)):
                            st.markdown("#### ❌ AVANT (votre version)")
                            avant = amelioration.get("avant", "")
                            st.markdown(f"""
                            <div style='background: #ffebee; padding: 1rem; border-radius: 8px; border-left: 4px solid #c62828;'>
                            {avant}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            st.markdown("#### ✅ APRÈS (version améliorée)")
                            apres = amelioration.get("apres", "")
                            st.markdown(f"""
                            <div style='background: #e8f5e9; padding: 1rem; border-radius: 8px; border-left: 4px solid #2e7d32;'>
                            {apres}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Bouton copier
                            if st.button(f"📋 Copier la version améliorée", key=f"copy_amelioration_{idx}", type="primary"):
                                st.code(apres, language="text")
                                st.success("✅ Texte prêt à copier et coller dans votre CV !")
                            
                            st.markdown("<br>**💡 Pourquoi c'est mieux :**", unsafe_allow_html=True)
                            pourquoi = amelioration.get("pourquoi", [])
                            for raison in pourquoi:
                                st.markdown(f"✓ {raison}")
                else:
                    st.warning("Aucune amélioration disponible")
            
            with tab4:
                st.markdown("### 🤖 Analyse d'Optimisation ATS")
                st.info("💡 **ATS (Applicant Tracking System)** : Les recruteurs utilisent des logiciels pour filtrer les CV. Cette analyse vous aide à passer ces filtres.")
                
                analyse_ats = results.get("analyse_ats", {})
                
                if analyse_ats:
                    # Score ATS
                    score_ats = analyse_ats.get("score_ats", 0)
                    taux_couverture = analyse_ats.get("taux_couverture", "0%")
                    
                    col_ats1, col_ats2 = st.columns(2)
                    
                    with col_ats1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{score_ats}</div>
                            <div class="metric-label">Score ATS</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_ats2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{taux_couverture}</div>
                            <div class="metric-label">Taux de couverture</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Mots-clés de l'offre
                    mots_cles = analyse_ats.get("mots_cles_offre", [])
                    
                    if mots_cles:
                        st.markdown("### 🔍 Mots-clés de l'offre")
                        
                        # Séparer présents et manquants
                        manquants = [mc for mc in mots_cles if not mc.get("present", False)]
                        presents = [mc for mc in mots_cles if mc.get("present", False)]
                        
                        if manquants:
                            st.markdown("#### ❌ Mots-clés MANQUANTS (à ajouter !)")
                            for mc in manquants:
                                priorite_emoji = {"HAUTE": "🔴", "MOYENNE": "🟡", "BASSE": "🟢"}.get(mc.get("priorite", ""), "⚪")
                                st.markdown(f"{priorite_emoji} **{mc.get('mot', '')}** - Priorité {mc.get('priorite', 'N/A')}")
                        
                        if presents:
                            with st.expander(f"✅ Mots-clés PRÉSENTS ({len(presents)})"):
                                for mc in presents:
                                    st.markdown(f"✓ **{mc.get('mot', '')}** ({mc.get('occurrences', 0)}x)")
                    
                    # Recommandations
                    recommandations = analyse_ats.get("recommandations", [])
                    
                    if recommandations:
                        st.markdown("### 💡 Recommandations ATS")
                        for idx, reco in enumerate(recommandations, 1):
                            st.markdown(f"{idx}. {reco}")
                    
                    # Mots-clés positifs
                    mots_positifs = analyse_ats.get("mots_cles_cv_positifs", [])
                    
                    if mots_positifs:
                        with st.expander(f"✨ Points forts de votre CV ({len(mots_positifs)} mots-clés pertinents)"):
                            st.markdown(", ".join([f"**{mot}**" for mot in mots_positifs]))
                else:
                    st.warning("Aucune analyse ATS disponible")
        
        else:
            st.markdown("""
            <div class="custom-card" style='text-align: center; padding: 3rem;'>
                <h2 style='color: #667eea; margin-bottom: 1rem;'>👈 Commencez l'analyse</h2>
                <p style='color: #7f8c8d; font-size: 1.1rem;'>
                Uploadez votre CV et cliquez sur le bouton d'analyse pour découvrir comment l'optimiser
                </p>
                <div style='margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 10px;'>
                    <p style='color: #2c3e50; margin: 0.5rem 0;'><b>⚡ Rapide</b> - Résultats en ~30 secondes</p>
                    <p style='color: #2c3e50; margin: 0.5rem 0;'><b>🎯 Précis</b> - Analyse par IA Claude</p>
                    <p style='color: #2c3e50; margin: 0.5rem 0;'><b>📊 Complet</b> - Score + Réécriture + Suggestions</p>
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
