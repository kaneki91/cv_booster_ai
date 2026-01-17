# CV Optimizer - MVP Streamlit

Application Streamlit pour optimiser des CV avec l'API Claude d'Anthropic.

## 🚀 Fonctionnalités

- 📄 Upload de CV au format PDF
- 🎯 Sélection de niche (Alternance, Tech, Data, etc.)
- 💼 Analyse de l'offre d'emploi (optionnel)
- 🤖 Analyse intelligente par Claude
- ✍️ Réécriture optimisée du CV
- 📊 Score et recommandations détaillées
- 📥 Export PDF du CV optimisé

## 📦 Installation

```bash
# Cloner le projet
cd cv_optim

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la clé API
cp .env.example .env
# Éditer .env et ajouter votre clé API Anthropic
```

## 🔑 Configuration

Créez un fichier `.env` à la racine du projet :

```
ANTHROPIC_API_KEY=votre_clé_api_anthropic
```

## 🎯 Utilisation

```bash
streamlit run streamlit_app.py
```

Puis ouvrez votre navigateur à l'adresse affichée (généralement http://localhost:8501)

## 📁 Structure du projet

```
cv_optim/
├── streamlit_app.py      # Interface Streamlit principale
├── claude_service.py     # Service d'interaction avec l'API Claude
├── pdf_utils.py          # Utilitaires PDF (lecture/export)
├── prompts.py            # Prompts système pour Claude
├── requirements.txt      # Dépendances Python
├── .env.example          # Template de configuration
└── README.md             # Documentation
```

## 🛠️ Stack Technique

- **Streamlit** : Interface web
- **Anthropic Claude** : Analyse et réécriture IA
- **pdfplumber** : Extraction de texte PDF
- **ReportLab** : Génération de PDF

## 📝 Licence

MIT
