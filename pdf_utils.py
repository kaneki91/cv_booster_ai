"""
Utilitaires pour la manipulation de PDF (extraction et génération)
"""

import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.pdfgen import canvas
from io import BytesIO
from typing import Optional
import re
import markdown


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrait le texte d'un fichier PDF uploadé
    
    Args:
        pdf_file: Fichier PDF uploadé via Streamlit
        
    Returns:
        str: Texte extrait du PDF
    """
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("Le PDF ne contient pas de texte extractible")
            
            return text.strip()
    
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction du PDF : {str(e)}")


def clean_text(text: str) -> str:
    """
    Nettoie le texte extrait (suppression des espaces multiples, etc.)
    
    Args:
        text: Texte brut extrait
        
    Returns:
        str: Texte nettoyé
    """
    # Supprime les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    # Supprime les lignes vides multiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def markdown_to_pdf(markdown_content: str, output_filename: str = "cv_optimise.pdf") -> bytes:
    """
    Convertit du contenu Markdown en PDF avec un style professionnel
    
    Args:
        markdown_content: Contenu Markdown du CV réécrit
        output_filename: Nom du fichier de sortie
        
    Returns:
        bytes: Contenu du PDF généré
    """
    try:
        # Buffer pour stocker le PDF
        buffer = BytesIO()
        
        # Création du document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles personnalisés
        styles = getSampleStyleSheet()
        
        # Style pour le titre principal (H1)
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2c3e50'),
            spaceAfter=6,
            spaceBefore=0,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            borderWidth=2,
            borderColor=HexColor('#3498db'),
            borderPadding=5,
        )
        
        # Style pour le sous-titre (H2)
        subtitle_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=3,
            fontName='Helvetica',
        )
        
        # Style pour les sections (H3)
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=HexColor('#2c3e50'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            leftIndent=0,
            borderWidth=0,
            borderPadding=3,
            borderColor=HexColor('#3498db'),
        )
        
        # Style pour les sous-sections (H4)
        subsection_style = ParagraphStyle(
            'CustomSubSection',
            parent=styles['Heading4'],
            fontSize=11,
            textColor=HexColor('#2c3e50'),
            spaceAfter=3,
            spaceBefore=9,
            fontName='Helvetica-Bold',
        )
        
        # Style pour le texte normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#333333'),
            spaceAfter=6,
            leading=14,
            fontName='Helvetica',
        )
        
        # Style pour les listes
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#333333'),
            leftIndent=20,
            spaceAfter=3,
            leading=13,
            fontName='Helvetica',
        )
        
        # Contenu du PDF
        story = []
        
        # Parse le markdown ligne par ligne
        lines = markdown_content.split('\n')
        i = 0
        in_list = False
        list_items = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Ignore les lignes vides
            if not line:
                if in_list:
                    # Termine la liste
                    story.append(create_list(list_items, bullet_style))
                    list_items = []
                    in_list = False
                i += 1
                continue
            
            # Titre H1
            if line.startswith('# '):
                if in_list:
                    story.append(create_list(list_items, bullet_style))
                    list_items = []
                    in_list = False
                text = clean_markdown(line[2:])
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 0.2*cm))
            
            # Titre H2
            elif line.startswith('## '):
                if in_list:
                    story.append(create_list(list_items, bullet_style))
                    list_items = []
                    in_list = False
                text = clean_markdown(line[3:])
                story.append(Paragraph(text, subtitle_style))
            
            # Titre H3
            elif line.startswith('### '):
                if in_list:
                    story.append(create_list(list_items, bullet_style))
                    list_items = []
                    in_list = False
                text = clean_markdown(line[4:])
                # Ajouter un emoji si présent
                story.append(Paragraph(text, section_style))
            
            # Titre H4
            elif line.startswith('#### '):
                if in_list:
                    story.append(create_list(list_items, bullet_style))
                    list_items = []
                    in_list = False
                text = clean_markdown(line[5:])
                story.append(Paragraph(text, subsection_style))
            
            # Liste
            elif line.startswith('- ') or line.startswith('* '):
                in_list = True
                text = clean_markdown(line[2:])
                list_items.append(text)
            
            # Texte normal
            else:
                if in_list:
                    story.append(create_list(list_items, bullet_style))
                    list_items = []
                    in_list = False
                text = clean_markdown(line)
                if text:  # Ignore les lignes vides
                    story.append(Paragraph(text, normal_style))
            
            i += 1
        
        # Termine une éventuelle liste en cours
        if in_list and list_items:
            story.append(create_list(list_items, bullet_style))
        
        # Génération du PDF
        doc.build(story)
        
        # Récupération des bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    except Exception as e:
        raise Exception(f"Erreur lors de la génération du PDF : {str(e)}")


def create_list(items, style):
    """Crée une liste formatée pour ReportLab"""
    bullet_items = [ListItem(Paragraph(item, style), leftIndent=15) for item in items]
    return ListFlowable(
        bullet_items,
        bulletType='bullet',
        start='•',
    )


def clean_markdown(text: str) -> str:
    """
    Nettoie le texte Markdown pour ReportLab (gras, italique, etc.)
    
    Args:
        text: Texte avec syntaxe Markdown
        
    Returns:
        str: Texte avec balises HTML pour ReportLab
    """
    # Enlève les émojis s'ils posent problème (optionnel)
    # text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Gras : **texte** ou __texte__ -> <b>texte</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Italique : *texte* ou _texte_ -> <i>texte</i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    
    # Échapper les caractères spéciaux XML
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Restaurer les balises HTML qu'on a ajoutées
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    
    return text




def validate_pdf(pdf_file) -> tuple[bool, Optional[str]]:
    """
    Valide qu'un fichier est bien un PDF lisible
    
    Args:
        pdf_file: Fichier uploadé
        
    Returns:
        tuple: (est_valide, message_erreur)
    """
    try:
        # Vérifie que c'est bien un PDF
        if not pdf_file.name.lower().endswith('.pdf'):
            return False, "Le fichier doit être au format PDF"
        
        # Essaye d'ouvrir le PDF
        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) == 0:
                return False, "Le PDF ne contient aucune page"
            
            # Vérifie qu'au moins une page contient du texte
            has_text = False
            for page in pdf.pages:
                if page.extract_text():
                    has_text = True
                    break
            
            if not has_text:
                return False, "Le PDF ne contient pas de texte extractible (peut-être une image?)"
        
        return True, None
    
    except Exception as e:
        return False, f"Erreur lors de la validation du PDF : {str(e)}"
