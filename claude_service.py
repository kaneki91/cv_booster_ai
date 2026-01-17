"""
Service d'interaction avec l'API Claude d'Anthropic
"""

import anthropic
import json
import os
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import prompts

# Chargement des variables d'environnement
load_dotenv()


def parse_checklist_markdown(text: str) -> Dict[str, Any]:
    """Parse le format Markdown de la checklist"""
    result = {
        "score_actuel": 0,
        "score_potentiel": 0,
        "temps_total_estime": "N/A",
        "actions": []
    }
    
    # Parse les scores en haut
    for ligne in text.split('\n')[:10]:
        if '**SCORE_ACTUEL:**' in ligne:
            result['score_actuel'] = int(re.search(r'\d+', ligne).group())
        elif '**SCORE_POTENTIEL:**' in ligne:
            result['score_potentiel'] = int(re.search(r'\d+', ligne).group())
        elif '**TEMPS_TOTAL:**' in ligne:
            result['temps_total_estime'] = ligne.split('**TEMPS_TOTAL:**')[1].strip()
    
    # Parse les actions
    blocs = text.split('## ACTION ')[1:]
    for bloc in blocs:
        try:
            action = {}
            lignes = bloc.strip().split('\n')
            
            for ligne in lignes[:10]:
                if '**Priorite:**' in ligne:
                    action['priorite'] = ligne.split('**Priorite:**')[1].strip()
                elif '**Titre:**' in ligne:
                    action['titre'] = ligne.split('**Titre:**')[1].strip()
                elif '**Impact:**' in ligne:
                    action['impact_points'] = int(re.search(r'\d+', ligne).group())
                elif '**Temps:**' in ligne:
                    action['temps_estime'] = ligne.split('**Temps:**')[1].strip()
            
            texte_complet = '\n'.join(lignes)
            
            if '### DESCRIPTION' in texte_complet:
                desc_section = texte_complet.split('### DESCRIPTION')[1].split('###')[0].strip()
                action['description'] = desc_section
            
            if '### ACTION_CONCRETE' in texte_complet:
                action_section = texte_complet.split('### ACTION_CONCRETE')[1].split('---')[0].strip()
                action['action_concrete'] = action_section
            
            if action.get('titre'):
                result['actions'].append(action)
        except:
            continue
    
    return result


def parse_ats_markdown(text: str) -> Dict[str, Any]:
    """Parse le format Markdown de l'analyse ATS"""
    result = {
        "score_ats": 0,
        "taux_couverture": "0%",
        "mots_cles_offre": [],
        "recommandations": [],
        "mots_cles_cv_positifs": []
    }
    
    # Parse les scores
    for ligne in text.split('\n')[:10]:
        if '**SCORE_ATS:**' in ligne:
            result['score_ats'] = int(re.search(r'\d+', ligne).group())
        elif '**TAUX_COUVERTURE:**' in ligne:
            result['taux_couverture'] = ligne.split('**TAUX_COUVERTURE:**')[1].strip()
    
    # Parse mots-clés manquants
    if '## MOTS_CLES_MANQUANTS' in text:
        section = text.split('## MOTS_CLES_MANQUANTS')[1].split('##')[0]
        for ligne in section.split('\n'):
            if ligne.strip().startswith('-'):
                parts = ligne.strip('- ').split('|')
                if len(parts) >= 3:
                    result['mots_cles_offre'].append({
                        "mot": parts[0].strip(),
                        "priorite": parts[1].strip(),
                        "present": False,
                        "occurrences": int(re.search(r'\d+', parts[2]).group()) if re.search(r'\d+', parts[2]) else 0
                    })
    
    # Parse mots-clés présents
    if '## MOTS_CLES_PRESENTS' in text:
        section = text.split('## MOTS_CLES_PRESENTS')[1].split('##')[0]
        for ligne in section.split('\n'):
            if ligne.strip().startswith('-'):
                parts = ligne.strip('- ').split('|')
                if len(parts) >= 3:
                    result['mots_cles_offre'].append({
                        "mot": parts[0].strip(),
                        "priorite": parts[1].strip(),
                        "present": True,
                        "occurrences": int(re.search(r'\d+', parts[2]).group()) if re.search(r'\d+', parts[2]) else 0
                    })
    
    # Parse recommandations
    if '## RECOMMANDATIONS' in text:
        section = text.split('## RECOMMANDATIONS')[1].split('##')[0]
        for ligne in section.split('\n'):
            if ligne.strip().startswith('-'):
                result['recommandations'].append(ligne.strip('- ').strip())
    
    # Parse points forts
    if '## POINTS_FORTS' in text:
        section = text.split('## POINTS_FORTS')[1].split('##')[0]
        for ligne in section.split('\n'):
            if ligne.strip().startswith('-'):
                result['mots_cles_cv_positifs'].append(ligne.strip('- ').strip())
    
    return result


def parse_analyse_markdown(text: str) -> Dict[str, Any]:
    """Parse le format Markdown de l'analyse principale"""
    result = {
        "score_global": 0,
        "criteres": [],
        "adequation_offre": "",
        "recommandations_generales": []
    }
    
    # Parse le score global
    for ligne in text.split('\n')[:5]:
        if '**SCORE_GLOBAL:**' in ligne:
            match = re.search(r'\d+', ligne)
            if match:
                result['score_global'] = int(match.group())
    
    # Parse les critères
    blocs_criteres = text.split('## CRITERE:')[1:]
    for bloc in blocs_criteres:
        try:
            critere = {}
            lignes = bloc.strip().split('\n')
            
            # Nom du critère (première ligne)
            critere['nom'] = lignes[0].strip().split('**Score:**')[0].strip()
            
            # Score
            for ligne in lignes[:5]:
                if '**Score:**' in ligne:
                    match = re.search(r'\d+', ligne)
                    if match:
                        critere['score'] = int(match.group())
            
            texte_complet = '\n'.join(lignes)
            
            # Points forts
            if '### POINTS_FORTS' in texte_complet:
                section = texte_complet.split('### POINTS_FORTS')[1].split('###')[0]
                critere['points_forts'] = [l.strip('- ').strip() for l in section.split('\n') if l.strip().startswith('-')]
            
            # Améliorations
            if '### AMELIORATIONS' in texte_complet:
                section = texte_complet.split('### AMELIORATIONS')[1].split('---')[0]
                critere['ameliorations'] = [l.strip('- ').strip() for l in section.split('\n') if l.strip().startswith('-')]
            
            if critere.get('nom'):
                result['criteres'].append(critere)
        except:
            continue
    
    # Adéquation offre
    if '## ADEQUATION_OFFRE' in text:
        section = text.split('## ADEQUATION_OFFRE')[1].split('##')[0].strip()
        result['adequation_offre'] = section
    
    # Recommandations générales
    if '## RECOMMANDATIONS_GENERALES' in text:
        section = text.split('## RECOMMANDATIONS_GENERALES')[1]
        result['recommandations_generales'] = [l.strip('- ').strip() for l in section.split('\n') if l.strip().startswith('-')]
    
    return result


def parse_ameliorations_markdown(text: str) -> Dict[str, Any]:
    """Parse le format Markdown des améliorations et retourne un dict"""
    ameliorations = []
    
    # Divise par les blocs AMELIORATION
    blocs = text.split('## AMELIORATION ')[1:]  # Ignore la partie avant le premier bloc
    
    for bloc in blocs:
        try:
            lignes = bloc.strip().split('\n')
            amelioration = {}
            
            # Parse les métadonnées
            for ligne in lignes[:10]:  # Les 10 premières lignes contiennent les métadonnées
                if ligne.startswith('**Section:**'):
                    amelioration['section'] = ligne.replace('**Section:**', '').strip()
                elif ligne.startswith('**Titre:**'):
                    amelioration['titre'] = ligne.replace('**Titre:**', '').strip()
                elif ligne.startswith('**Impact:**'):
                    amelioration['impact_score'] = int(ligne.replace('**Impact:**', '').strip())
            
            # Parse AVANT, APRES, POURQUOI
            texte_complet = '\n'.join(lignes)
            
            if '### AVANT' in texte_complet and '### APRES' in texte_complet:
                avant_section = texte_complet.split('### AVANT')[1].split('### APRES')[0].strip()
                amelioration['avant'] = avant_section
            
            if '### APRES' in texte_complet and '### POURQUOI' in texte_complet:
                apres_section = texte_complet.split('### APRES')[1].split('### POURQUOI')[0].strip()
                amelioration['apres'] = apres_section
            
            if '### POURQUOI' in texte_complet:
                pourquoi_section = texte_complet.split('### POURQUOI')[1].split('---')[0].strip()
                pourquoi_lignes = [l.strip('- ').strip() for l in pourquoi_section.split('\n') if l.strip().startswith('-')]
                amelioration['pourquoi'] = pourquoi_lignes
            
            if amelioration.get('section'):  # Si on a au moins une section, on ajoute
                ameliorations.append(amelioration)
        except Exception as e:
            # Skip les blocs mal formés
            continue
    
    return {"ameliorations": ameliorations}


def clean_json_string(text: str) -> str:
    """Nettoie une chaîne JSON de manière agressive pour éviter les erreurs de parsing"""
    # Enlève les blocs de code markdown
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    # Supprime TOUS les caractères de contrôle (y compris \n, \r, \t dans les valeurs)
    # Garde uniquement les retours à la ligne de structure JSON
    import codecs
    
    # Decode les séquences d'échappement
    try:
        # Remplace les caractères de contrôle échappés par des espaces
        text = text.replace('\\n', ' ')
        text = text.replace('\\r', ' ')
        text = text.replace('\\t', ' ')
        text = text.replace('\\b', ' ')
        text = text.replace('\\f', ' ')
    except:
        pass
    
    # Supprime les caractères de contrôle bruts
    text = ''.join(char if ord(char) >= 32 or char in '\n\r\t' else ' ' for char in text)
    
    # Nettoie les espaces multiples mais garde la structure
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Garde la structure JSON mais nettoie les espaces dans les valeurs
        if line.strip():
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


class ClaudeService:
    """Service pour interagir avec l'API Claude"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le service Claude
        
        Args:
            api_key: Clé API Anthropic (optionnel, utilise .env par défaut)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Clé API Anthropic non trouvée. Vérifiez votre fichier .env")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-haiku-20240307"  # Claude 3 Haiku - Rapide et économique
    
    def analyser_cv(
        self, 
        cv_text: str, 
        niche: str, 
        offre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyse un CV et retourne un score + recommandations
        
        Args:
            cv_text: Texte du CV extrait
            niche: Clé de la niche cible (ex: 'tech_dev')
            offre: Texte de l'offre d'emploi (optionnel)
            
        Returns:
            Dict contenant le score et l'analyse détaillée
        """
        try:
            # Contexte de la niche
            niche_context = prompts.get_niche_context(niche)
            
            # Construction du message utilisateur
            user_message = f"{niche_context}\n\n"
            user_message += f"CV à analyser :\n\n{cv_text}\n\n"
            
            if offre:
                user_message += f"Offre d'emploi cible :\n\n{offre}\n\n"
            
            user_message += "Fournis ton analyse au format JSON spécifié dans les instructions."
            
            # Appel à l'API Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # Température basse pour cohérence
                system=prompts.ANALYSE_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extraction de la réponse
            response_text = message.content[0].text
            
            # Parse le Markdown au lieu du JSON
            analysis = parse_analyse_markdown(response_text)
            
            return {
                "success": True,
                "analysis": analysis,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Erreur de parsing JSON : {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'analyse : {str(e)}"
            }
    
    def reecrire_cv(
        self, 
        cv_text: str, 
        niche: str, 
        offre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Réécrit un CV de manière optimisée
        
        Args:
            cv_text: Texte du CV extrait
            niche: Clé de la niche cible
            offre: Texte de l'offre d'emploi (optionnel)
            
        Returns:
            Dict contenant le CV réécrit en Markdown
        """
        try:
            # Contexte de la niche
            niche_context = prompts.get_niche_context(niche)
            
            # Construction du message utilisateur
            user_message = f"{niche_context}\n\n"
            user_message += f"CV à réécrire :\n\n{cv_text}\n\n"
            
            if offre:
                user_message += f"Offre d'emploi cible :\n\n{offre}\n\n"
            
            user_message += "Réécris ce CV au format Markdown spécifié dans les instructions."
            
            # Appel à l'API Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,  # Température plus élevée pour créativité
                system=prompts.REECRITURE_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extraction de la réponse
            cv_markdown = message.content[0].text.strip()
            
            # Nettoie les balises markdown si présentes
            if cv_markdown.startswith("```markdown"):
                cv_markdown = cv_markdown[11:]
            if cv_markdown.startswith("```"):
                cv_markdown = cv_markdown[3:]
            if cv_markdown.endswith("```"):
                cv_markdown = cv_markdown[:-3]
            
            return {
                "success": True,
                "cv_markdown": cv_markdown.strip(),
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la réécriture : {str(e)}"
            }
    
    def generer_suggestions(
        self, 
        cv_text: str, 
        niche: str, 
        offre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère des suggestions d'amélioration pour un CV
        
        Args:
            cv_text: Texte du CV extrait
            niche: Clé de la niche cible
            offre: Texte de l'offre d'emploi (optionnel)
            
        Returns:
            Dict contenant les suggestions en Markdown
        """
        try:
            # Contexte de la niche
            niche_context = prompts.get_niche_context(niche)
            
            # Construction du message utilisateur
            user_message = f"{niche_context}\n\n"
            user_message += f"CV à améliorer :\n\n{cv_text}\n\n"
            
            if offre:
                user_message += f"Offre d'emploi cible :\n\n{offre}\n\n"
            
            user_message += "Fournis des suggestions concrètes et actionnables au format Markdown."
            
            # Appel à l'API Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3072,
                temperature=0.5,
                system=prompts.SUGGESTIONS_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extraction de la réponse
            suggestions_markdown = message.content[0].text.strip()
            
            return {
                "success": True,
                "suggestions": suggestions_markdown,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la génération de suggestions : {str(e)}"
            }
    
    def generer_ameliorations_sections(
        self,
        cv_text: str,
        niche: str,
        offre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère des améliorations section par section avec format avant/après
        
        Args:
            cv_text: Texte du CV extrait
            niche: Clé de la niche cible
            offre: Texte de l'offre d'emploi (optionnel)
            
        Returns:
            Dict contenant les améliorations par section
        """
        try:
            niche_context = prompts.get_niche_context(niche)
            
            user_message = f"{niche_context}\n\n"
            user_message += f"CV à analyser :\n\n{cv_text}\n\n"
            
            if offre:
                user_message += f"Offre d'emploi cible :\n\n{offre}\n\n"
            
            user_message += "Fournis les améliorations section par section au format JSON spécifié."
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.1,  # Très bas pour JSON strict
                system=prompts.AMELIORATIONS_SECTION_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            
            response_text = message.content[0].text
            
            # Parse le Markdown au lieu du JSON
            ameliorations = parse_ameliorations_markdown(response_text)
            
            return {
                "success": True,
                "ameliorations": ameliorations,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Erreur de parsing JSON : {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la génération des améliorations : {str(e)}"
            }
    
    def generer_checklist_actions(
        self,
        cv_text: str,
        niche: str,
        offre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une checklist d'actions priorisées
        
        Args:
            cv_text: Texte du CV extrait
            niche: Clé de la niche cible
            offre: Texte de l'offre d'emploi (optionnel)
            
        Returns:
            Dict contenant la checklist d'actions
        """
        try:
            niche_context = prompts.get_niche_context(niche)
            
            user_message = f"{niche_context}\n\n"
            user_message += f"CV à analyser :\n\n{cv_text}\n\n"
            
            if offre:
                user_message += f"Offre d'emploi cible :\n\n{offre}\n\n"
            
            user_message += "Génère une checklist d'actions concrètes au format JSON."
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3072,
                temperature=0.1,  # Très bas pour JSON strict
                system=prompts.CHECKLIST_ACTIONS_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            
            response_text = message.content[0].text
            
            # Parse le Markdown au lieu du JSON
            checklist = parse_checklist_markdown(response_text)
            
            return {
                "success": True,
                "checklist": checklist,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Erreur de parsing JSON : {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la génération de la checklist : {str(e)}"
            }
    
    def analyser_ats(
        self,
        cv_text: str,
        niche: str,
        offre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyse l'optimisation ATS du CV
        
        Args:
            cv_text: Texte du CV extrait
            niche: Clé de la niche cible
            offre: Texte de l'offre d'emploi (optionnel)
            
        Returns:
            Dict contenant l'analyse ATS
        """
        try:
            niche_context = prompts.get_niche_context(niche)
            
            user_message = f"{niche_context}\n\n"
            user_message += f"CV à analyser :\n\n{cv_text}\n\n"
            
            if offre:
                user_message += f"Offre d'emploi cible :\n\n{offre}\n\n"
            
            user_message += "Analyse l'optimisation ATS au format JSON."
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.1,  # Très bas pour JSON strict
                system=prompts.ANALYSE_ATS_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            
            response_text = message.content[0].text
            
            # Parse le Markdown au lieu du JSON
            analyse_ats = parse_ats_markdown(response_text)
            
            return {
                "success": True,
                "analyse_ats": analyse_ats,
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }
        
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Erreur de parsing JSON : {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'analyse ATS : {str(e)}"
            }
    
    def optimiser_cv_complet(
        self, 
        cv_text: str, 
        niche: str, 
        offre: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Effectue l'optimisation complète : analyse + améliorations + checklist + ATS
        
        Args:
            cv_text: Texte du CV extrait
            niche: Clé de la niche cible
            offre: Texte de l'offre d'emploi (optionnel)
            
        Returns:
            Dict contenant toutes les informations
        """
        results = {}
        
        # 1. Analyse globale
        analysis_result = self.analyser_cv(cv_text, niche, offre)
        if not analysis_result["success"]:
            return analysis_result
        results["analysis"] = analysis_result["analysis"]
        
        # 2. Améliorations section par section
        ameliorations_result = self.generer_ameliorations_sections(cv_text, niche, offre)
        if not ameliorations_result["success"]:
            return ameliorations_result
        results["ameliorations"] = ameliorations_result["ameliorations"]
        
        # 3. Checklist d'actions
        checklist_result = self.generer_checklist_actions(cv_text, niche, offre)
        if not checklist_result["success"]:
            return checklist_result
        results["checklist"] = checklist_result["checklist"]
        
        # 4. Analyse ATS
        ats_result = self.analyser_ats(cv_text, niche, offre)
        if not ats_result["success"]:
            return ats_result
        results["analyse_ats"] = ats_result["analyse_ats"]
        
        # Calcul des tokens totaux
        total_tokens = (
            analysis_result.get("tokens_used", 0) +
            ameliorations_result.get("tokens_used", 0) +
            checklist_result.get("tokens_used", 0) +
            ats_result.get("tokens_used", 0)
        )
        
        return {
            "success": True,
            "results": results,
            "total_tokens": total_tokens
        }
