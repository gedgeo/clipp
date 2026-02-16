"""Module simplifié de sous-titres pour MoviePy 2.0."""

from typing import List, Dict


def add_subtitles_to_video_simple(
    video_path: str,
    output_path: str,
    subtitles: List[Dict],
    font_size: int = 40,
):
    """Ajoute des sous-titres simples à une vidéo (version compatible MoviePy 2.0).
    
    Args:
        video_path: Chemin vers la vidéo
        output_path: Chemin de sortie
        subtitles: Liste de dicts avec 'start', 'end', 'text'
        font_size: Taille de police
    """
    try:
        from moviepy import VideoFileClip, TextClip, CompositeVideoClip
        
        # Charger la vidéo
        video = VideoFileClip(video_path)
        
        # Créer les clips de texte
        txt_clips = []
        for sub in subtitles:
            try:
                # Créer le texte
                txt = TextClip(
                    text=sub["text"],
                    font_size=font_size,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    text_align="center",
                    size=(video.w * 0.9, None),
                    method="caption",
                )
                
                # Positionner et timer
                txt = txt.with_start(sub["start"]).with_duration(sub["end"] - sub["start"])
                txt = txt.with_position(("center", "bottom"))
                
                txt_clips.append(txt)
            except Exception as e:
                print(f"Erreur création sous-titre: {e}")
                continue
        
        # Combiner
        if txt_clips:
            final = CompositeVideoClip([video] + txt_clips)
        else:
            final = video
        
        # Exporter
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
        )
        
        video.close()
        if txt_clips:
            final.close()
        
        return True
        
    except Exception as e:
        print(f"Erreur ajout sous-titres: {e}")
        import traceback
        traceback.print_exc()
        return False
