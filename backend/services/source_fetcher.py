import requests
import io
import re
import os
from urllib.parse import urlparse

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


def fetch_source_text(source_url: str, allowed_domains_env: str = None, max_bytes_env: str = None):
    """Récupère et extrait le texte d'une URL donnée (HTML ou PDF).

    - Vérifie le domaine si `allowed_domains_env` fourni (liste CSV) ou via env `ALLOWED_SOURCE_DOMAINS`.
    - Limite la lecture à `max_bytes_env` (ou env `SOURCE_MAX_BYTES`, défaut 2MB).
    - Retourne le texte extrait ou `None` si échec / non autorisé / trop volumineux.
    """
    ALLOWED_DOMAINS = allowed_domains_env or os.environ.get('ALLOWED_SOURCE_DOMAINS')
    MAX_BYTES = int(max_bytes_env or os.environ.get('SOURCE_MAX_BYTES', str(2 * 1024 * 1024)))

    parsed = urlparse(source_url)
    domain = parsed.hostname or ''
    if ALLOWED_DOMAINS:
        allowed = [d.strip().lower() for d in ALLOWED_DOMAINS.split(',') if d.strip()]
        if domain.lower() not in allowed:
            print(f"⚠️ Domaine {domain} non autorisé pour la source.")
            return None

    resp = requests.get(source_url, timeout=10, stream=True)
    content_length = resp.headers.get('Content-Length')
    if content_length and int(content_length) > MAX_BYTES:
        print(f"⚠️ Fichier trop volumineux ({content_length} bytes) > limite {MAX_BYTES}")
        return None

    collected = io.BytesIO()
    total = 0
    for chunk in resp.iter_content(1024):
        if not chunk:
            break
        collected.write(chunk)
        total += len(chunk)
        if total > MAX_BYTES:
            print(f"⚠️ Fichier dépassant la taille maximale ({MAX_BYTES} bytes)")
            return None

    raw = collected.getvalue()
    extracted = None

    try:
        ctype = (resp.headers.get('Content-Type') or '').lower()
    except Exception:
        ctype = ''

    # Traiter PDF
    if 'pdf' in ctype or source_url.lower().endswith('.pdf'):
        if PdfReader is not None:
            try:
                pdf_reader = PdfReader(io.BytesIO(raw))
                texts = []
                for p in pdf_reader.pages:
                    try:
                        texts.append(p.extract_text() or '')
                    except Exception:
                        pass
                extracted = '\n'.join(texts)
            except Exception as e:
                print(f"⚠️ Erreur extraction PDF: {e}")
                extracted = None
        else:
            print("⚠️ PyPDF2 non disponible; impossible d'extraire le PDF")
            extracted = None
    else:
        # Traiter HTML/text
        try:
            encoding = resp.encoding or 'utf-8'
            html = raw.decode(encoding, errors='replace')
            if BeautifulSoup is not None:
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    for s in soup(['script', 'style', 'noscript']):
                        s.decompose()
                    text = soup.get_text(separator=' ')
                    extracted = ' '.join(text.split())
                except Exception as e:
                    print(f"⚠️ BeautifulSoup erreur: {e}")
                    extracted = None
            else:
                # Fallback basique
                text = re.sub('<script[^>]*>.*?</script>', '', html, flags=re.S | re.I)
                text = re.sub('<style[^>]*>.*?</style>', '', text, flags=re.S | re.I)
                text = re.sub('<[^>]+>', '', text)
                extracted = re.sub('\s+', ' ', text).strip()
        except Exception as e:
            print(f"⚠️ Erreur decoding HTML: {e}")
            extracted = None
    print(f"✅ Extraction source depuis {source_url} réussie.")
    print(extracted[:500])  # Debug: afficher un extrait

    return extracted

def topic_related_to_text(topic: str, text: str) -> bool:
    """Validation simple: vérifie si le sujet est lié au texte extrait.

    - Extrait des mots-clés significatifs du `topic` (longueur >=4, suppression d'un petit set de stopwords FR)
    - Vérifie la présence d'au moins un mot-clé dans le texte extrait.
    - Si aucun mot-clé détectable, retombe sur la recherche de la phrase complète.
    """
    if not topic or not text:
        return False

    text_low = text.lower()
    # Liste minimale de stopwords français
    stopwords = {
        'et','les','des','pour','avec','sans','dans','sur','par','entre','est','une','un','le','la','du','de'
    }

    words = re.findall(r"\w+", topic.lower())
    keywords = [w for w in words if len(w) >= 4 and w not in stopwords]

    if keywords:
        matches = sum(1 for k in keywords if k in text_low)
        return matches >= 1

    # Fallback: check if full topic string appears
    return topic.lower() in text_low
