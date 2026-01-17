# 🚀 Déploiement sur Streamlit Cloud

## 📋 Étape 1 : Préparer l'application

Votre application est prête à être déployée ! Assurez-vous d'avoir :
- ✅ `requirements.txt` avec toutes les dépendances
- ✅ `streamlit_app.py` comme fichier principal
- ✅ Tous les fichiers `.py` nécessaires

## 🔑 Étape 2 : Configurer les Secrets (IMPORTANT)

Sur Streamlit Cloud, les variables d'environnement se configurent via les **Secrets**.

### **Accéder aux Secrets :**

1. Allez sur votre app déployée : https://cvboosterai-gq3tmlg58w4ejcstqouaed.streamlit.app/
2. Cliquez sur **⚙️ Settings** (en haut à droite)
3. Sélectionnez l'onglet **"Secrets"**

### **Ajouter votre clé API :**

Copiez-collez ce contenu dans les secrets :

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxx"
```

⚠️ **Remplacez** `sk-ant-api03-xxx...` par votre **vraie clé API** Anthropic.

4. Cliquez sur **"Save"**
5. L'application va **redémarrer automatiquement**

## ✅ Étape 3 : Vérifier que tout fonctionne

1. **Rafraîchissez** la page de votre app
2. Dans la sidebar, vous devriez voir : **"✅ Clé API active"**
3. Le bouton **"📤 Upload CV"** devrait maintenant être visible
4. Testez en uploadant un CV PDF

## 🔐 Obtenir une clé API Anthropic

Si vous n'avez pas encore de clé API :

1. Allez sur : https://console.anthropic.com/
2. Créez un compte (5$ de crédits gratuits)
3. Allez dans **Settings** → **API Keys**
4. Créez une nouvelle clé
5. **Copiez-la immédiatement** (vous ne pourrez plus la voir !)
6. Collez-la dans les Secrets de Streamlit Cloud

## 🐛 Dépannage

### **L'upload n'apparaît toujours pas ?**

- Vérifiez que les Secrets sont bien sauvegardés
- Attendez 30 secondes que l'app redémarre
- Rafraîchissez la page (F5)
- Vérifiez dans la sidebar si "✅ Clé API active" s'affiche

### **Erreur "Clé API manquante" ?**

- Le nom de la variable DOIT être exactement : `ANTHROPIC_API_KEY`
- Pas d'espaces avant/après le =
- La clé doit commencer par `sk-ant-api03-`
- Format exact : `ANTHROPIC_API_KEY = "sk-ant-api03-..."`

### **L'app crash au démarrage ?**

- Vérifiez que toutes les dépendances sont dans `requirements.txt`
- Regardez les logs dans Streamlit Cloud (Settings → Logs)

## 📊 Monitoring

Streamlit Cloud vous permet de voir :
- **Logs** : Settings → Logs
- **Usage** : Settings → Analytics
- **Secrets** : Settings → Secrets

## 🔄 Mise à jour de l'app

Pour mettre à jour votre app déployée :

1. Committez vos changements sur GitHub
2. Pushez sur la branche connectée à Streamlit
3. L'app se redéploie automatiquement !

## 💡 Conseils

- ✅ Ne commitez JAMAIS votre clé API dans le code
- ✅ Utilisez toujours les Secrets pour les clés
- ✅ Testez localement avant de déployer
- ✅ Surveillez votre usage de crédits Anthropic

## 🎉 Votre app est live !

URL de votre app : https://cvboosterai-gq3tmlg58w4ejcstqouaed.streamlit.app/

Partagez-la et profitez ! 🚀
