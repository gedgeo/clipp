"""Script de test pour vérifier les sous-titres sur les clips générés."""

import sys
sys.path.insert(0, r'C:\Users\Gedge\Desktop\03_Dev\clipp')

from video_processor import VideoProcessor
from pathlib import Path
import os

# Créer un processeur
processor = VideoProcessor()

# Demander le chemin de la vidéo
video_path = input("Entrez le chemin de votre vidéo (ex: C:\\Users\\...\\video.mp4): ").strip()

if not Path(video_path).exists():
    print(f"❌ Vidéo non trouvée: {video_path}")
    sys.exit(1)

print(f"\n✅ Analyse de: {video_path}")
print("-" * 50)

# 1. Générer les sous-titres
print("\n📝 Étape 1: Génération des sous-titres...")
try:
    subtitles = processor.generate_subtitles(video_path, language="fr")
    
    if subtitles:
        print(f"✅ {len(subtitles)} sous-titres générés")
        print("\nAperçu des 5 premiers sous-titres:")
        for i, sub in enumerate(subtitles[:5]):
            print(f"  {i+1}. [{sub['start']:.1f}s - {sub['end']:.1f}s] {sub['text'][:60]}...")
    else:
        print("❌ Aucun sous-titre généré")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erreur génération sous-titres: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Créer un clip court avec sous-titres
print("\n🎬 Étape 2: Création d'un clip test avec sous-titres...")

try:
    # Prendre les 3 premiers sous-titres
    test_subs = subtitles[:3]
    
    if test_subs:
        start_time = test_subs[0]["start"]
        end_time = test_subs[-1]["end"]
        
        print(f"\nCréation d'un clip de {start_time:.1f}s à {end_time:.1f}s")
        print(f"Durée: {end_time - start_time:.1f} secondes")
        
        # Créer le clip
        clip_path = processor.create_clip(
            video_path=video_path,
            start_time=start_time,
            end_time=end_time,
            output_name="clip_test_sans_sous_titres.mp4",
            format_type="tiktok",
            zoom_mode="fill",
            add_subtitles=False,
        )
        
        print(f"✅ Clip créé: {clip_path}")
        
        # Ajouter les sous-titres
        output_with_subs = processor.output_dir / "clip_test_avec_sous_titres.mp4"
        
        print(f"\n📝 Ajout des sous-titres au clip...")
        success = processor.burn_subtitles_to_clip(
            video_path=clip_path,
            output_path=str(output_with_subs),
            subtitles=test_subs,
            font_size=40,
        )
        
        if success:
            print(f"\n✅ SUCCÈS! Clip avec sous-titres créé:")
            print(f"   📁 {output_with_subs}")
            print(f"\n🎬 Ouvrez ce fichier dans votre lecteur vidéo pour vérifier les sous-titres")
        else:
            print("\n❌ Échec de l'ajout des sous-titres")
    else:
        print("❌ Pas assez de sous-titres pour créer un clip test")
        
except Exception as e:
    print(f"❌ Erreur création clip: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Test terminé!")
print("="*50)
