# 🎬 Clipp

Application intelligente pour créer facilement des clips vidéo au format vertical (9:16) pour **TikTok**, **YouTube Shorts** et **Instagram Reels** à partir de vidéos au format paysage ou portrait.

## ✨ Fonctionnalités

### Fonctionnalités de base
- 📁 Import de vidéos multiples formats (MP4, AVI, MOV, MKV, WEBM)
- ✂️ Découpage précis avec sélection des timestamps
- 📱 Conversion automatique au format 9:16 (1080x1920)
- 🔍 3 modes de zoom : Adapter, Remplir, Centrer
- 🎯 Génération automatique de plusieurs clips
- 💾 Export en MP4 haute qualité

### Fonctionnalités avancées
- 🎙️ **Sous-titres automatiques** avec Whisper (OpenAI)
  - Support de plusieurs langues (FR, EN, ES, DE, IT, PT)
  - Intégration directe dans les clips
- ✨ **Sous-titres animés** (NOUVEAU)
  - Fondu (fade in/out)
  - Glissement (slide up/down)
  - Zoom progressif
  - Machine à écrire (lettre par lettre)
  - Effet rebond
- 🔊 **Détection intelligente par audio**
  - Détecte les pics de volume pour trouver les moments les plus intéressants
  - Analyse du spectre audio pour identifier les moments clés
- 🎬 **Détection de changements de scène**
  - Analyse visuelle pour détecter les changements de plan
  - Création automatique de clips aux transitions
- 👁️ **Prévisualisation avant export** (NOUVEAU)
  - Rendu rapide en basse qualité (360p)
  - Vérification du cadrage et des sous-titres
  - Limite de 10 secondes pour la rapidité
- 🔗 **Assemblage avec transitions** (NOUVEAU)
  - Combine plusieurs clips en une seule vidéo
  - 6 types de transitions disponibles:
    - Fondu (fade)
    - Fondu enchaîné (crossfade)
    - Glissement gauche/droite/haut/bas
  - Durée de transition configurable

### Méthodes de génération automatique
1. **🔊 Pics audio** (recommandé) - Moments sonores intenses
2. **🎬 Changements de scène** - Coupures visuelles
3. **⚖️ Division égale** - Segments réguliers

## 🚀 Installation

### Prérequis
- Python 3.8+
- FFmpeg (installé automatiquement avec moviepy sur la plupart des systèmes)
- ~2GB d'espace disque pour les modèles Whisper

### Étapes d'installation

1. **Cloner ou créer le projet**
```bash
cd clipp
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

**Note**: La première installation téléchargera le modèle Whisper (~150MB) lors de la première utilisation.

## 🎮 Utilisation

### Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

### Guide d'utilisation

#### 1. Importer votre vidéo
- Allez dans l'onglet **"📁 Importer"**
- Chargez votre vidéo (MP4, AVI, MOV, MKV, WEBM)
- Les informations de la vidéo s'afficheront (durée, résolution, FPS)

#### 2. Configurer les options (sidebar)
- **Format de sortie** : Choisissez entre TikTok, YouTube Shorts ou Instagram Reels
- **Mode de zoom** :
  - *Adapter* : Montre toute la vidéo avec bands noires si nécessaire
  - *Remplir* : Remplit l'écran en coupant les bords si nécessaire
  - *Centrer* : Centre la vidéo sans redimensionnement
- **📝 Sous-titres** : Activez la génération automatique
- **Langue** : Sélectionnez la langue de la vidéo
- **Animation des sous-titres** : Choisissez l'effet d'animation

#### 3. Créer un clip avec prévisualisation
- Allez dans l'onglet **"✂️ Clip Manuel"**
- Utilisez les sliders pour définir le début et la fin
- Cliquez sur **"👁️ Prévisualiser"** pour voir le résultat (10s)
- Une fois satisfait, cliquez sur **"🚀 Créer le clip final"**
- Le clip est ajouté à la liste pour assemblage

#### 4. Générer automatiquement des clips
- Allez dans l'onglet **"🎯 Auto-Détection"**
- Choisissez votre méthode de détection
- Définissez le nombre de clips et leur durée
- Activez les sous-titres animés si souhaité
- Cliquez sur **"🎲 Générer automatiquement"**

#### 5. Assembler avec transitions (NOUVEAU)
- Allez dans l'onglet **"🔗 Assemblage"**
- Sélectionnez le type de transition
- Ajustez la durée de transition
- Cliquez sur **"🔗 Assembler tous les clips"**
- Téléchargez la vidéo finale combinée

### Types de transitions disponibles

| Transition | Description | Utilisation recommandée |
|------------|-------------|------------------------|
| **Fondu** | Fondu enchaîné simple | Transition douce entre scènes |
| **Crossfade** | Chevauchement progressif | Enchaînement fluide |
| **Glissement Gauche** | Slide vers la gauche | Changement de sujet |
| **Glissement Droite** | Slide vers la droite | Retour au sujet |
| **Glissement Haut** | Slide vers le haut | Montée en intensité |
| **Glissement Bas** | Slide vers le bas | Calme/Conclusion |

### Animations de sous-titres disponibles

| Animation | Effet | Impact |
|-----------|-------|--------|
| **Fondu** | Apparition progressive | Classique, professionnel |
| **Glissement Haut** | Entrée depuis le bas | Dynamique, moderne |
| **Glissement Bas** | Entrée depuis le haut | Original |
| **Zoom** | Agrandissement | Accentuation |
| **Machine à écrire** | Lettre par lettre | Rétro, engageant |
| **Rebond** | Effet de rebond | Ludique, jeune |

## 📁 Structure du projet

```
clipp/
├── app.py                 # Interface Streamlit
├── video_processor.py     # Logique de traitement vidéo
├── video_effects.py       # Effets avancés (transitions, animations)
├── requirements.txt       # Dépendances Python
├── output/               # Dossier de sortie des clips (créé automatiquement)
└── README.md
```

## 🔧 Dépannage

### Problème : "FFmpeg not found"

**Solution** : Installez FFmpeg manuellement :
- **Windows** : Téléchargez sur https://ffmpeg.org/download.html et ajoutez au PATH
- **Mac** : `brew install ffmpeg`
- **Linux** : `sudo apt-get install ffmpeg`

### Problème : Erreur avec Whisper / torch

**Solution** : Si vous avez des erreurs liées à PyTorch :
```bash
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Problème : L'application est lente

**Solutions** :
1. Utilisez la **prévisualisation** avant de créer le clip final
2. Réduisez la résolution de sortie dans `video_processor.py`
3. Utilisez le preset "fast" au lieu de "medium"
4. Pour Whisper, utilisez un modèle plus léger (remplacez "base" par "tiny")

### Problème : Les transitions ne fonctionnent pas

**Vérifiez** :
- Vous avez créé au moins 2 clips
- Les clips ont la même résolution
- Essayez avec le type de transition "fade" qui est le plus simple

### Problème : Les sous-titres animés sont trop rapides/lents

**Solution** : Modifiez la durée d'animation dans `video_effects.py` :
```python
animation_config = SubtitleAnimation(
    type=subtitle_animation,
    duration=0.5,  # Augmentez cette valeur
)
```

## ⚙️ Configuration avancée

### Modifier le modèle Whisper

Dans `video_processor.py`, modifiez le modèle :

```python
# Modèles disponibles : tiny, base, small, medium, large
model = whisper.load_model("base")  # Changez ici
```

### Créer vos propres transitions

Dans `video_effects.py`, ajoutez une nouvelle méthode dans `VideoEffects` :

```python
@staticmethod
def create_custom_transition(clip1, clip2, duration):
    # Votre logique de transition ici
    pass
```

### Personnaliser les animations de sous-titres

Modifiez `AnimatedSubtitleGenerator` pour créer de nouveaux effets :

```python
@staticmethod
def create_custom_animation(text, start_time, end_time, ...):
    # Votre animation personnalisée
    pass
```

## 🛣️ Roadmap

- [x] Détection automatique des moments intéressants (basée sur l'audio)
- [x] Ajout de sous-titres automatiques
- [x] Détection de changements de scène
- [x] Sous-titres animés
- [x] Prévisualisation avant export
- [x] Assemblage avec transitions
- [ ] Mode portrait intelligent (tracking du sujet)
- [ ] Effets visuels (stabilisation, filtres)
- [ ] Upload direct vers TikTok/YouTube
- [ ] Templates de style prédéfinis

## 📝 License

MIT License - Libre d'utilisation personnelle et commerciale.

## 🙏 Remerciements

- [MoviePy](https://github.com/Zulko/moviepy) - Pour le traitement vidéo
- [Whisper](https://github.com/openai/whisper) - Pour la reconnaissance vocale
- [Streamlit](https://streamlit.io/) - Pour l'interface web
- [FFmpeg](https://ffmpeg.org/) - Pour le traitement multimédia

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

**Créé avec ❤️ pour les créateurs de contenu**
