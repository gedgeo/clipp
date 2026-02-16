"""Module de traitement vidéo pour créer des clips TikTok/YouTube Shorts."""

import os
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from scipy.signal import find_peaks


class VideoProcessor:
    """Classe pour traiter les vidéos et créer des clips."""
    
    # Formats supportés
    FORMATS = {
        "tiktok": {"width": 1080, "height": 1920, "ratio": 9/16},
        "youtube_shorts": {"width": 1080, "height": 1920, "ratio": 9/16},
        "instagram_reels": {"width": 1080, "height": 1920, "ratio": 9/16},
    }
    
    def __init__(self, output_dir: str = "output"):
        """Initialise le processeur vidéo.
        
        Args:
            output_dir: Répertoire de sortie pour les clips
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def get_video_info(self, video_path: str) -> dict:
        """Récupère les informations de la vidéo."""
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        clip = VideoFileClip(video_path)
        info = {
            "duration": clip.duration,
            "fps": clip.fps,
            "width": clip.w,
            "height": clip.h,
            "aspect_ratio": clip.w / clip.h,
        }
        clip.close()
        return info
    
    def analyze_audio_peaks(
        self,
        video_path: str,
        min_clip_duration: float = 15.0,
        max_clip_duration: float = 60.0,
        num_clips: int = 5,
        prominence: float = 0.1,
    ) -> List[Tuple[float, float]]:
        """Détecte les moments intéressants basés sur les pics audio.
        
        Args:
            video_path: Chemin vers la vidéo
            min_clip_duration: Durée minimale d'un clip
            max_clip_duration: Durée maximale d'un clip
            num_clips: Nombre de clips à détecter
            prominence: Seuil de détection des pics (0-1)
            
        Returns:
            Liste de tuples (start_time, end_time)
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        clip = VideoFileClip(video_path)
        
        if clip.audio is None:
            clip.close()
            # Fallback si pas d'audio
            return self._divide_equally(video_path, min_clip_duration, num_clips)
        
        # Extraire l'audio
        audio = clip.audio
        fps = 44100  # Échantillonnage audio
        
        try:
            # Convertir en array numpy
            audio_array = audio.to_soundarray(fps=fps)
            
            # Prendre un seul canal (mono)
            if len(audio_array.shape) > 1:
                audio_array = audio_array[:, 0]
            
            # Calculer le volume RMS par fenêtre
            window_size = int(fps * 0.5)  # Fenêtre de 0.5 seconde
            volumes = []
            times = []
            
            for i in range(0, len(audio_array) - window_size, window_size):
                window = audio_array[i:i + window_size]
                rms = np.sqrt(np.mean(window**2))
                volumes.append(rms)
                times.append(i / fps)
            
            volumes = np.array(volumes)
            
            # Normaliser
            if volumes.max() > 0:
                volumes = volumes / volumes.max()
            
            # Détecter les pics
            peaks, properties = find_peaks(
                volumes,
                prominence=prominence,
                distance=int(min_clip_duration / 0.5),  # Distance minimale entre pics
            )
            
            # Trier par prominence et prendre les meilleurs
            if len(peaks) > 0:
                prominences = properties['prominences']
                sorted_indices = np.argsort(prominences)[::-1]
                top_peaks = peaks[sorted_indices[:num_clips]]
                
                time_ranges = []
                for peak in top_peaks:
                    center_time = times[peak]
                    start = max(0, center_time - max_clip_duration / 2)
                    end = min(clip.duration, start + max_clip_duration)
                    
                    # Ajuster si on dépasse
                    if end - start < min_clip_duration:
                        start = max(0, end - min_clip_duration)
                    
                    time_ranges.append((start, end))
                
                clip.close()
                return sorted(time_ranges, key=lambda x: x[0])
            else:
                clip.close()
                return self._divide_equally(video_path, min_clip_duration, num_clips)
                
        except Exception as e:
            print(f"Erreur analyse audio: {e}")
            clip.close()
            return self._divide_equally(video_path, min_clip_duration, num_clips)
    
    def _divide_equally(
        self,
        video_path: str,
        clip_duration: float,
        num_clips: int,
    ) -> List[Tuple[float, float]]:
        """Divise la vidéo en segments égaux."""
        info = self.get_video_info(video_path)
        total_duration = info["duration"]
        interval = total_duration / num_clips
        
        time_ranges = []
        for i in range(num_clips):
            start = i * interval
            end = min(start + clip_duration, total_duration)
            time_ranges.append((start, end))
            
        return time_ranges
    
    def detect_scene_changes(
        self,
        video_path: str,
        threshold: float = 30.0,
        min_scene_duration: float = 2.0,
    ) -> List[float]:
        """Détecte les changements de scène dans la vidéo.
        
        Args:
            video_path: Chemin vers la vidéo
            threshold: Seuil de détection (différence entre frames)
            min_scene_duration: Durée minimale entre deux scènes
            
        Returns:
            Liste des timestamps des changements de scène
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        clip = VideoFileClip(video_path)
        fps = clip.fps
        scene_changes = []
        last_scene_time = 0
        
        try:
            # Analyser une frame toutes les 0.5 secondes
            step = 0.5
            prev_frame = None
            
            for t in np.arange(0, clip.duration, step):
                frame = clip.get_frame(t)
                
                if prev_frame is not None:
                    # Calculer la différence moyenne
                    diff = np.mean(np.abs(frame.astype(float) - prev_frame.astype(float)))
                    
                    if diff > threshold and (t - last_scene_time) >= min_scene_duration:
                        scene_changes.append(t)
                        last_scene_time = t
                
                prev_frame = frame
            
            clip.close()
            return scene_changes
            
        except Exception as e:
            print(f"Erreur détection scènes: {e}")
            clip.close()
            return []
    
    def generate_subtitles(
        self,
        video_path: str,
        language: str = "fr",
    ) -> List[dict]:
        """Génère des sous-titres à partir de l'audio.
        
        Args:
            video_path: Chemin vers la vidéo
            language: Code langue (fr, en, etc.)
            
        Returns:
            Liste de dicts avec 'start', 'end', 'text'
        """
        try:
            import whisper
            
            # Charger le modèle (téléchargement automatique si nécessaire)
            model = whisper.load_model("base")
            
            # Transcrire
            result = model.transcribe(video_path, language=language)
            
            subtitles = []
            for segment in result["segments"]:
                subtitles.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                })
            
            return subtitles
            
        except ImportError:
            print("Whisper n'est pas installé. Installez-le avec: pip install openai-whisper")
            return []
        except Exception as e:
            print(f"Erreur génération sous-titres: {e}")
            return []
    
    def add_subtitles_to_clip(
        self,
        video_path: str,
        output_path: str,
        subtitles: List[dict],
        font_size: int = 40,
        font_color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 2,
    ):
        """Ajoute des sous-titres à une vidéo.
        
        Args:
            video_path: Chemin vers la vidéo source
            output_path: Chemin de sortie
            subtitles: Liste de dicts avec 'start', 'end', 'text'
            font_size: Taille de la police
            font_color: Couleur du texte
            stroke_color: Couleur du contour
            stroke_width: Épaisseur du contour
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.VideoClip import TextClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        
        clip = VideoFileClip(video_path)
        txt_clips = []
        
        for sub in subtitles:
            try:
                txt_clip = TextClip(
                    sub["text"],
                    fontsize=font_size,
                    color=font_color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    font="Arial-Bold",
                    method="caption",
                    align="center",
                    size=(clip.w * 0.9, None),
                )
                
                txt_clip = txt_clip.with_start(sub["start"]).with_duration(
                    sub["end"] - sub["start"]
                ).with_position(("center", "bottom")).with_margin(bottom=50, opacity=0)
                
                txt_clips.append(txt_clip)
            except Exception as e:
                print(f"Erreur création sous-titre: {e}")
                continue
        
        # Combiner
        if txt_clips:
            final = CompositeVideoClip([clip] + txt_clips)
            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=30,
            )
            final.close()
        else:
            clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=30,
            )
        
        clip.close()
    
    def create_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_name: Optional[str] = None,
        format_type: str = "tiktok",
        zoom_mode: str = "fit",
        add_subtitles: bool = False,
        subtitles_list: Optional[List[dict]] = None,
    ) -> str:
        """Crée un clip à partir d'une vidéo.
        
        Args:
            video_path: Chemin vers la vidéo source
            start_time: Temps de début en secondes
            end_time: Temps de fin en secondes
            output_name: Nom du fichier de sortie
            format_type: Type de format (tiktok, youtube_shorts, instagram_reels)
            zoom_mode: Mode de zoom (fit, fill, center)
            add_subtitles: Ajouter des sous-titres
            subtitles_list: Liste des sous-titres à ajouter
            
        Returns:
            Chemin du fichier clip créé
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.VideoClip import ColorClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        
        video_path_obj = Path(video_path)
        
        if not output_name:
            output_name = f"{video_path_obj.stem}_clip_{int(start_time)}-{int(end_time)}.mp4"
        
        output_path = self.output_dir / output_name
        
        # Charger la vidéo
        clip = VideoFileClip(str(video_path))
        
        # Extraire le segment
        subclip = clip.subclipped(start_time, end_time)
        
        # Redimensionner selon le format
        format_info = self.FORMATS.get(format_type, self.FORMATS["tiktok"])
        target_width = format_info["width"]
        target_height = format_info["height"]
        
        # Calculer les dimensions
        video_ratio = subclip.w / subclip.h
        target_ratio = target_width / target_height
        
        if zoom_mode == "fit":
            # Adapter à l'écran avec bands noires si nécessaire
            if video_ratio > target_ratio:
                # Vidéo plus large que haute -> réduire la largeur
                new_width = target_width
                new_height = int(target_width / video_ratio)
            else:
                # Vidéo plus haute que large -> réduire la hauteur
                new_height = target_height
                new_width = int(target_height * video_ratio)
            
            resized = subclip.resized(new_size=(new_width, new_height))
            
            # Centrer la vidéo sur fond noir
            x_center = (target_width - new_width) // 2
            y_center = (target_height - new_height) // 2
            
            # Créer un fond noir
            bg = ColorClip(size=(target_width, target_height), color=(0, 0, 0))
            bg = bg.with_duration(resized.duration)
            
            # Combiner
            final = CompositeVideoClip([bg, resized.with_position((x_center, y_center))])
            final = final.with_duration(resized.duration)
            
        elif zoom_mode == "fill":
            # Remplir l'écran en coupant si nécessaire
            if video_ratio > target_ratio:
                # Vidéo plus large -> crop horizontal
                new_height = target_height
                new_width = int(target_height * video_ratio)
                resized = subclip.resized(new_size=(new_width, new_height))
                x_center = (new_width - target_width) // 2
                final = resized.cropped(
                    x1=x_center,
                    y1=0,
                    x2=x_center + target_width,
                    y2=target_height,
                )
            else:
                # Vidéo plus haute -> crop vertical
                new_width = target_width
                new_height = int(target_width / video_ratio)
                resized = subclip.resized(new_size=(new_width, new_height))
                y_center = (new_height - target_height) // 2
                final = resized.cropped(
                    x1=0,
                    y1=y_center,
                    x2=target_width,
                    y2=y_center + target_height,
                )
        else:
            # Mode center - centrer sans redimensionner
            final = subclip.on_color(
                size=(target_width, target_height),
                color=(0, 0, 0),
                pos=("center", "center"),
            )
        
        # Ajouter sous-titres si demandé
        if add_subtitles and subtitles_list:
            temp_path = self.output_dir / f"temp_{output_name}"
            
            # Sauvegarder temporairement
            final.write_videofile(
                str(temp_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,
                preset="medium",
                threads=4,
            )
            
            # Ajouter les sous-titres
            self.add_subtitles_to_clip(
                str(temp_path),
                str(output_path),
                subtitles_list,
            )
            
            # Nettoyer
            temp_path.unlink(missing_ok=True)
        else:
            # Exporter normalement
            final.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,
                preset="medium",
                threads=4,
            )
        
        # Nettoyer
        clip.close()
        subclip.close()
        final.close()
        
        return str(output_path)
    
    def create_multiple_clips(
        self,
        video_path: str,
        time_ranges: List[Tuple[float, float]],
        format_type: str = "tiktok",
        zoom_mode: str = "fit",
        add_subtitles: bool = False,
        subtitles_list: Optional[List[dict]] = None,
    ) -> List[str]:
        """Crée plusieurs clips à partir d'une vidéo.
        
        Args:
            video_path: Chemin vers la vidéo source
            time_ranges: Liste de tuples (start_time, end_time) en secondes
            format_type: Type de format
            zoom_mode: Mode de zoom
            add_subtitles: Ajouter des sous-titres
            subtitles_list: Liste des sous-titres
            
        Returns:
            Liste des chemins des clips créés
        """
        output_paths = []
        
        for i, (start, end) in enumerate(time_ranges):
            output_name = f"clip_{i+1:03d}.mp4"
            try:
                # Filtrer les sous-titres pour ce segment
                segment_subs = None
                if subtitles_list:
                    segment_subs = [
                        s for s in subtitles_list
                        if s["start"] >= start and s["end"] <= end
                    ]
                    # Ajuster les timestamps
                    for s in segment_subs:
                        s["start"] -= start
                        s["end"] -= start
                
                path = self.create_clip(
                    video_path=video_path,
                    start_time=start,
                    end_time=end,
                    output_name=output_name,
                    format_type=format_type,
                    zoom_mode=zoom_mode,
                    add_subtitles=add_subtitles,
                    subtitles_list=segment_subs,
                )
                output_paths.append(path)
            except Exception as e:
                print(f"Erreur lors de la création du clip {i+1}: {e}")
                
        return output_paths
    
    def auto_detect_moments(
        self,
        video_path: str,
        clip_duration: float = 30.0,
        num_clips: int = 5,
        detection_method: str = "smart",
        min_gap: float = 5.0,
    ) -> List[Tuple[float, float]]:
        """Détecte automatiquement des moments intéressants avec algorithme intelligent.
        
        Args:
            video_path: Chemin vers la vidéo
            clip_duration: Durée de chaque clip en secondes
            num_clips: Nombre de clips à générer
            detection_method: Méthode de détection (smart, audio_peaks, scene_change, equal)
            min_gap: Espace minimum entre deux clips (évite les chevauchements)
            
        Returns:
            Liste de tuples (start_time, end_time)
        """
        info = self.get_video_info(video_path)
        total_duration = info["duration"]
        
        # Mode "smart" : combine plusieurs méthodes
        if detection_method == "smart":
            candidates = []
            
            # Essayer la détection audio
            try:
                audio_peaks = self.analyze_audio_peaks(
                    video_path,
                    min_clip_duration=clip_duration * 0.5,
                    max_clip_duration=clip_duration,
                    num_clips=num_clips * 2,  # Plus de candidats
                    prominence=0.05,  # Seuil plus bas
                )
                for start, end in audio_peaks:
                    candidates.append({"start": start, "end": end, "score": 1.0, "type": "audio"})
            except Exception as e:
                print(f"Détection audio échouée: {e}")
            
            # Essayer la détection de scènes
            try:
                scene_changes = self.detect_scene_changes(video_path, threshold=25.0)
                for scene_time in scene_changes:
                    start = max(0, scene_time - clip_duration / 2)
                    end = min(total_duration, start + clip_duration)
                    candidates.append({"start": start, "end": end, "score": 0.8, "type": "scene"})
            except Exception as e:
                print(f"Détection scènes échouée: {e}")
            
            # Ajouter des points réguliers comme fallback
            interval = total_duration / (num_clips + 1)
            for i in range(1, num_clips + 1):
                center = i * interval
                start = max(0, center - clip_duration / 2)
                end = min(total_duration, start + clip_duration)
                candidates.append({"start": start, "end": end, "score": 0.5, "type": "regular"})
            
            # Trier par score décroissant
            candidates.sort(key=lambda x: x["score"], reverse=True)
            
            # Sélectionner les meilleurs candidats sans chevauchement
            selected = []
            used_ranges = []
            
            for candidate in candidates:
                if len(selected) >= num_clips:
                    break
                
                # Vérifier le gap minimum avec les clips déjà sélectionnés
                valid = True
                for used_start, used_end in used_ranges:
                    # Vérifier s'il y a chevauchement ou gap insuffisant
                    if not (candidate["end"] + min_gap <= used_start or candidate["start"] >= used_end + min_gap):
                        valid = False
                        break
                
                if valid:
                    selected.append((candidate["start"], candidate["end"]))
                    used_ranges.append((candidate["start"], candidate["end"]))
            
            # Trier par ordre chronologique
            selected.sort(key=lambda x: x[0])
            
            # Compléter si nécessaire
            while len(selected) < num_clips:
                remaining = num_clips - len(selected)
                additional = self._divide_equally(video_path, clip_duration, remaining)
                
                for start, end in additional:
                    # Vérifier qu'il n'y a pas de chevauchement
                    valid = True
                    for used_start, used_end in used_ranges:
                        if not (end + min_gap <= used_start or start >= used_end + min_gap):
                            valid = False
                            break
                    
                    if valid and len(selected) < num_clips:
                        selected.append((start, end))
                        used_ranges.append((start, end))
                
                break
            
            return selected[:num_clips]
        
        elif detection_method == "audio_peaks":
            return self.analyze_audio_peaks(
                video_path,
                min_clip_duration=clip_duration * 0.5,
                max_clip_duration=clip_duration,
                num_clips=num_clips,
            )
        elif detection_method == "scene_change":
            scene_changes = self.detect_scene_changes(video_path)
            time_ranges = []
            for scene_time in scene_changes[:num_clips]:
                start = max(0, scene_time - clip_duration / 2)
                end = min(total_duration, start + clip_duration)
                time_ranges.append((start, end))
            
            while len(time_ranges) < num_clips:
                remaining = self._divide_equally(video_path, clip_duration, num_clips - len(time_ranges))
                time_ranges.extend(remaining)
                break
                
            return time_ranges[:num_clips]
        else:
            return self._divide_equally(video_path, clip_duration, num_clips)
    
    def generate_clips_auto(
        self,
        video_path: str,
        output_prefix: str = "auto_clip",
        num_clips: int = 5,
        clip_duration: float = 30.0,
        format_type: str = "tiktok",
        zoom_mode: str = "fill",
        enable_subtitles: bool = True,
        subtitle_style: str = "tiktok_classic",
        subtitle_font: str = "Impact",
        subtitle_position: str = "bottom_margin",
        subtitle_size: int = 50,
        subtitle_color: str = "white",
        detection_method: str = "smart",
        add_transitions: bool = False,
        transition_type: str = "fade",
    ) -> Dict:
        """Génère automatiquement des clips avec un seul appel.
        
        Cette méthode automatise tout le processus :
        1. Détection intelligente des moments
        2. Génération des sous-titres si activé
        3. Création des clips avec options choisies
        4. Assemblage avec transitions si demandé
        
        Args:
            video_path: Chemin vers la vidéo source
            output_prefix: Préfixe pour les noms de fichiers
            num_clips: Nombre de clips à générer
            clip_duration: Durée de chaque clip
            format_type: Format de sortie
            zoom_mode: Mode de zoom
            enable_subtitles: Activer les sous-titres
            subtitle_style: Style des sous-titres (tiktok_classic, youtube_bold, etc.)
            subtitle_font: Police des sous-titres
            subtitle_position: Position des sous-titres
            subtitle_size: Taille des sous-titres
            subtitle_color: Couleur des sous-titres
            detection_method: Méthode de détection
            add_transitions: Ajouter des transitions entre clips
            transition_type: Type de transition
            
        Returns:
            Dictionnaire avec les résultats et métadonnées
        """
        from video_effects import TransitionType
        
        results = {
            "success": True,
            "clips": [],
            "assembled": None,
            "subtitles": None,
            "method_used": detection_method,
        }
        
        try:
            # 1. Obtenir les infos
            info = self.get_video_info(video_path)
            results["video_info"] = info
            
            # 2. Générer les sous-titres si demandé
            subtitles_list = None
            if enable_subtitles:
                try:
                    subtitles_list = self.generate_subtitles(video_path)
                    results["subtitles"] = subtitles_list
                except Exception as e:
                    print(f"Génération sous-titres échouée: {e}")
            
            # 3. Détecter les moments
            time_ranges = self.auto_detect_moments(
                video_path,
                clip_duration=clip_duration,
                num_clips=num_clips,
                detection_method=detection_method,
            )
            results["detected_moments"] = time_ranges
            
            # 4. Créer les clips
            clip_paths = []
            for i, (start, end) in enumerate(time_ranges):
                output_name = f"{output_prefix}_{i+1:03d}.mp4"
                
                # Filtrer les sous-titres pour ce segment
                segment_subs = None
                if subtitles_list:
                    segment_subs = [
                        s for s in subtitles_list
                        if s["start"] >= start and s["end"] <= end
                    ]
                    for s in segment_subs:
                        s["start"] -= start
                        s["end"] -= start
                
                # Créer le clip
                # Étape 1: Créer le clip vidéo de base
                # Utiliser un nom simple sans chemin (create_clip ajoute output_dir)
                temp_filename = f"temp_{output_name}"
                path = self.create_clip(
                    video_path=video_path,
                    start_time=start,
                    end_time=end,
                    output_name=temp_filename,  # Juste le nom, pas le chemin complet
                    format_type=format_type,
                    zoom_mode=zoom_mode,
                    add_subtitles=False,  # On ajoute les sous-titres après
                    subtitles_list=None,
                )
                
                # Étape 2: Ajouter les sous-titres si demandé
                if enable_subtitles and segment_subs:
                    final_path = self.output_dir / output_name
                    success = self.burn_subtitles_to_clip(
                        video_path=path,
                        output_path=str(final_path),
                        subtitles=segment_subs,
                        font_size=40,
                    )
                    if success:
                        # Supprimer le fichier temporaire
                        try:
                            os.remove(path)
                        except:
                            pass
                        path = str(final_path)
                    else:
                        # Si l'ajout des sous-titres échoue, renommer le fichier temporaire
                        os.rename(path, str(final_path))
                        path = str(final_path)
                
                clip_paths.append(path)
                results["clips"].append({
                    "path": path,
                    "start": start,
                    "end": end,
                    "duration": end - start,
                })
            
            # 5. Assembler avec transitions si demandé
            if add_transitions and len(clip_paths) > 1:
                assembled_path = self.concatenate_clips_with_transitions(
                    video_paths=clip_paths,
                    output_name=f"{output_prefix}_assembled.mp4",
                    transition_type=transition_type,
                    transition_duration=0.5,
                    format_type=format_type,
                )
                results["assembled"] = assembled_path
            
            return results
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            return results
    
    def create_clip_with_animated_subtitles(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_name: Optional[str] = None,
        format_type: str = "tiktok",
        zoom_mode: str = "fit",
        subtitles_list: Optional[List[dict]] = None,
        subtitle_animation: str = "fade",
        font_size: int = 40,
        font_color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 2,
    ) -> str:
        """Crée un clip avec sous-titres animés.
        
        Args:
            video_path: Chemin vers la vidéo source
            start_time: Temps de début
            end_time: Temps de fin
            output_name: Nom du fichier de sortie
            format_type: Type de format
            zoom_mode: Mode de zoom
            subtitles_list: Liste des sous-titres
            subtitle_animation: Type d'animation (fade, slide_up, slide_down, scale, typewriter, bounce)
            font_size: Taille de police
            font_color: Couleur du texte
            stroke_color: Couleur du contour
            stroke_width: Épaisseur du contour
            
        Returns:
            Chemin du fichier créé
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.VideoClip import ColorClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from video_effects import AnimatedSubtitleGenerator, SubtitleAnimation
        
        video_path_obj = Path(video_path)
        
        if not output_name:
            output_name = f"{video_path_obj.stem}_clip_animated_{int(start_time)}-{int(end_time)}.mp4"
        
        output_path = self.output_dir / output_name
        
        # Charger et traiter la vidéo
        clip = VideoFileClip(str(video_path))
        subclip = clip.subclipped(start_time, end_time)
        
        # Redimensionner
        format_info = self.FORMATS.get(format_type, self.FORMATS["tiktok"])
        target_width = format_info["width"]
        target_height = format_info["height"]
        
        video_ratio = subclip.w / subclip.h
        target_ratio = target_width / target_height
        
        if zoom_mode == "fit":
            if video_ratio > target_ratio:
                new_width = target_width
                new_height = int(target_width / video_ratio)
            else:
                new_height = target_height
                new_width = int(target_height * video_ratio)
            
            resized = subclip.resized(new_size=(new_width, new_height))
            x_center = (target_width - new_width) // 2
            y_center = (target_height - new_height) // 2
            
            # Créer un fond noir
            bg = ColorClip(size=(target_width, target_height), color=(0, 0, 0))
            bg = bg.with_duration(resized.duration)
            
            # Combiner
            final = CompositeVideoClip([bg, resized.with_position((x_center, y_center))])
            final = final.with_duration(resized.duration)
        elif zoom_mode == "fill":
            if video_ratio > target_ratio:
                new_height = target_height
                new_width = int(target_height * video_ratio)
                resized = subclip.resized(new_size=(new_width, new_height))
                x_center = (new_width - target_width) // 2
                final = resized.cropped(
                    x1=x_center, y1=0,
                    x2=x_center + target_width, y2=target_height,
                )
            else:
                new_width = target_width
                new_height = int(target_width / video_ratio)
                resized = subclip.resized(new_size=(new_width, new_height))
                y_center = (new_height - target_height) // 2
                final = resized.cropped(
                    x1=0, y1=y_center,
                    x2=target_width, y2=y_center + target_height,
                )
        else:
            final = subclip.on_color(
                size=(target_width, target_height),
                color=(0, 0, 0),
                pos=("center", "center"),
            )
        
        # Ajouter sous-titres animés
        if subtitles_list:
            animation_config = SubtitleAnimation(
                type=subtitle_animation,  # type: ignore
                duration=0.3,
            )
            
            txt_clips = []
            for sub in subtitles_list:
                if sub["start"] >= start_time and sub["end"] <= end_time:
                    txt_clip = AnimatedSubtitleGenerator.create_animated_subtitle(
                        text=sub["text"],
                        start_time=sub["start"] - start_time,
                        end_time=sub["end"] - start_time,
                        video_width=target_width,
                        video_height=target_height,
                        animation=animation_config,
                        font_size=font_size,
                        font_color=font_color,
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                    )
                    txt_clips.append(txt_clip)
            
            if txt_clips:
                final = CompositeVideoClip([final] + txt_clips)
        
        # Exporter
        final.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            threads=4,
        )
        
        # Nettoyer
        clip.close()
        subclip.close()
        final.close()
        
        return str(output_path)
    
    def concatenate_clips_with_transitions(
        self,
        video_paths: List[str],
        output_name: str,
        transition_type: str = "fade",
        transition_duration: float = 0.5,
        format_type: str = "tiktok",
    ) -> str:
        """Concatène plusieurs clips avec des transitions.
        
        Args:
            video_paths: Liste des chemins des vidéos à concaténer
            output_name: Nom du fichier de sortie
            transition_type: Type de transition (fade, slide_left, slide_right, slide_up, slide_down, crossfade)
            transition_duration: Durée de la transition en secondes
            format_type: Type de format
            
        Returns:
            Chemin du fichier créé
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy import concatenate_videoclips
        from video_effects import VideoEffects, TransitionType
        
        if not video_paths:
            raise ValueError("La liste des vidéos est vide")
        
        output_path = self.output_dir / output_name
        
        # Charger tous les clips
        clips = [VideoFileClip(str(path)) for path in video_paths]
        
        # Appliquer les transitions
        transition_map = {
            "fade": TransitionType.FADE,
            "slide_left": TransitionType.SLIDE_LEFT,
            "slide_right": TransitionType.SLIDE_RIGHT,
            "slide_up": TransitionType.SLIDE_UP,
            "slide_down": TransitionType.SLIDE_DOWN,
            "crossfade": TransitionType.CROSSFADE,
        }
        
        trans_type = transition_map.get(transition_type, TransitionType.FADE)
        
        if len(clips) == 1:
            # Un seul clip, pas besoin de transition
            final = clips[0]
        else:
            # Appliquer les transitions entre chaque clip
            result_clips = [clips[0]]
            
            for i in range(1, len(clips)):
                # Combiner avec transition
                combined = VideoEffects.create_transition(
                    result_clips[-1],
                    clips[i],
                    trans_type,
                    transition_duration,
                )
                result_clips[-1] = combined
            
            final = result_clips[-1]
        
        # Redimensionner au format cible
        format_info = self.FORMATS.get(format_type, self.FORMATS["tiktok"])
        final_resized = final.resized(new_size=(format_info["width"], format_info["height"]))
        
        # Exporter
        final_resized.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            threads=4,
        )
        
        # Nettoyer
        for clip in clips:
            clip.close()
        final.close()
        final_resized.close()
        
        return str(output_path)
    
    def create_preview(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_name: Optional[str] = None,
        quality: str = "low",
        max_duration: float = 10.0,
    ) -> str:
        """Crée une prévisualisation basse qualité.
        
        Args:
            video_path: Chemin vers la vidéo
            start_time: Temps de début
            end_time: Temps de fin
            output_name: Nom du fichier de sortie
            quality: Qualité (low, medium)
            max_duration: Durée max de la prévisualisation
            
        Returns:
            Chemin du fichier de prévisualisation
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        if not output_name:
            output_name = f"preview_{int(start_time)}-{int(end_time)}.mp4"
        
        output_path = self.output_dir / output_name
        
        clip = VideoFileClip(str(video_path))
        
        # Extraire le segment
        duration = min(end_time - start_time, max_duration)
        preview = clip.subclipped(start_time, start_time + duration)
        
        # Paramètres selon la qualité
        if quality == "low":
            fps = 15
            resolution = (360, 640)
            bitrate = "500k"
            preset = "ultrafast"
        else:
            fps = 24
            resolution = (540, 960)
            bitrate = "1000k"
            preset = "superfast"
        
        # Redimensionner
        preview_resized = preview.resized(new_size=resolution)
        
        # Exporter
        preview_resized.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=fps,
            bitrate=bitrate,
            preset=preset,
            threads=4,
        )
        
        clip.close()
        preview.close()
        preview_resized.close()
        
        return str(output_path)
    
    def burn_subtitles_to_clip(
        self,
        video_path: str,
        output_path: str,
        subtitles: List[Dict],
        font_size: int = 50,
        font: str = "Impact",
        position: str = "bottom_margin",
        color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 3,
    ) -> bool:
        """Ajoute les sous-titres à une vidéo existante (gravure permanente).
        
        Cette méthode est plus robuste et fonctionne avec MoviePy 2.0.
        
        Args:
            video_path: Chemin vers la vidéo
            output_path: Chemin de sortie
            subtitles: Liste de dicts avec 'start', 'end', 'text'
            font_size: Taille de police
            font: Nom de la police (Arial, Impact, Bebas-Neue, etc.)
            position: Position des sous-titres (bottom, bottom_margin, center, top, top_margin)
            color: Couleur du texte
            stroke_color: Couleur du contour
            stroke_width: Épaisseur du contour
            
        Returns:
            True si succès, False sinon
        """
        try:
            from moviepy import VideoFileClip, TextClip, CompositeVideoClip
            from subtitle_config import get_position_coordinates
            
            print(f"Ajout des sous-titres à {video_path}...")
            print(f"Nombre de sous-titres: {len(subtitles)}")
            print(f"Configuration: font={font}, size={font_size}, position={position}")
            
            # Charger la vidéo
            video = VideoFileClip(video_path)
            
            # Obtenir les coordonnées de position
            pos = get_position_coordinates(position)
            
            # Créer les clips de texte
            txt_clips = []
            for i, sub in enumerate(subtitles):
                try:
                    # Vérifier que les timestamps sont valides
                    start = max(0, sub["start"])
                    end = min(video.duration, sub["end"])
                    duration = end - start
                    
                    if duration <= 0:
                        continue
                    
                    # Créer le texte avec la police choisie
                    txt = TextClip(
                        text=sub["text"],
                        font=font,
                        font_size=font_size,
                        color=color,
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                        text_align="center",
                        size=(int(video.w * 0.95), None),
                        method="caption",
                    )
                    
                    # Timer et positionner
                    txt = txt.with_start(start).with_duration(duration)
                    txt = txt.with_position(pos)
                    
                    txt_clips.append(txt)
                    if i < 3:  # Log seulement les 3 premiers pour ne pas spammer
                        print(f"  Sous-titre {i+1}: [{start:.1f}s - {end:.1f}s] {sub['text'][:40]}...")
                    
                except Exception as e:
                    print(f"  Erreur sous-titre {i+1}: {e}")
                    continue
            
            # Combiner avec la vidéo
            if txt_clips:
                print(f"Combinaison de {len(txt_clips)} sous-titres avec la vidéo...")
                final = CompositeVideoClip([video] + txt_clips)
            else:
                print("Aucun sous-titre à ajouter")
                final = video
            
            # Exporter
            final.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,
                preset="medium",
                threads=4,
            )
            
            # Nettoyer
            video.close()
            if txt_clips:
                final.close()
            
            print(f"✅ Sous-titres ajoutés avec succès: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur ajout sous-titres: {e}")
            import traceback
            traceback.print_exc()
            return False
