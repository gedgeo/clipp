"""Script de test pour vérifier que les sous-titres fonctionnent."""

import sys
sys.path.insert(0, r'C:\Users\Gedge\Desktop\03_Dev\clipp')

from video_processor import VideoProcessor
from pathlib import Path

# Créer un processeur
processor = VideoProcessor()

# Test avec une vidéo de test
test_video = r"C:\chemin\vers\ta\video.mp4"  # Remplace par ton chemin

if Path(test_video).exists():
    print("✅ Test de génération de sous-titres...")
    
    # 1. Générer les sous-titres
    subtitles = processor.generate_subtitles(test_video)
    
    if subtitles:
        print(f"✅ {len(subtitles)} sous-titres générés")
        for i, sub in enumerate(subtitles[:3]):
            print(f"  {i+1}. [{sub['start']:.1f}s - {sub['end']:.1f}s]: {sub['text'][:50]}")
        
        # 2. Créer un clip avec sous-titres
        print("\n✅ Création du clip avec sous-titres...")
        output_path = processor.output_dir / "test_avec_sous_titres.mp4"
        
        success = processor.burn_subtitles_to_clip(
            video_path=test_video,
            output_path=str(output_path),
            subtitles=subtitles[:10],  # Juste les 10 premiers pour tester
        )
        
        if success:
            print(f"\n✅ Clip créé avec succès: {output_path}")
        else:
            print("\n❌ Échec de la création du clip")
    else:
        print("❌ Aucun sous-titre généré")
else:
    print(f"❌ Vidéo non trouvée: {test_video}")
    print("Modifie le chemin dans ce script pour tester")
