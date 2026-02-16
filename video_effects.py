"""Module avancé de traitement vidéo avec transitions et animations."""

import os
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Literal
from dataclasses import dataclass
from enum import Enum


class TransitionType(Enum):
    """Types de transitions disponibles."""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    CROSSFADE = "crossfade"


@dataclass
class TransitionConfig:
    """Configuration d'une transition."""
    type: TransitionType
    duration: float = 0.5  # Durée en secondes
    

@dataclass
class SubtitleAnimation:
    """Configuration d'animation de sous-titre."""
    type: Literal["fade", "slide_up", "slide_down", "scale", "typewriter", "bounce", "none"] = "fade"
    duration: float = 0.3  # Durée de l'animation
    delay: float = 0.0     # Délai avant animation


class VideoEffects:
    """Classe pour les effets vidéo avancés."""
    
    @staticmethod
    def create_transition(
        clip1,
        clip2,
        transition_type: TransitionType,
        duration: float = 0.5,
    ):
        """Crée une transition entre deux clips.
        
        Args:
            clip1: Premier clip
            clip2: Deuxième clip
            transition_type: Type de transition
            duration: Durée de la transition en secondes
            
        Returns:
            Clip combiné avec transition
        """
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy import concatenate_videoclips
        from moviepy.video.fx.all import fadein, fadeout
        
        w, h = clip1.w, clip1.h
        
        if transition_type == TransitionType.FADE:
            # Fade out du premier, fade in du second
            clip1_fade = clip1.fx(fadeout, duration)
            clip2_fade = clip2.fx(fadein, duration)
            return concatenate_videoclips([clip1_fade, clip2_fade])
            
        elif transition_type == TransitionType.CROSSFADE:
            # Crossfade (chevauchement)
            clip1_part = clip1.subclipped(0, clip1.duration - duration)
            transition_part1 = clip1.subclipped(clip1.duration - duration, clip1.duration).fx(fadeout, duration)
            transition_part2 = clip2.subclipped(0, duration).fx(fadein, duration)
            clip2_part = clip2.subclipped(duration, clip2.duration)
            
            # Combiner la transition
            transition = CompositeVideoClip([
                transition_part1.with_start(0),
                transition_part2.with_start(0),
            ])
            
            return concatenate_videoclips([clip1_part, transition, clip2_part])
            
        elif transition_type == TransitionType.SLIDE_LEFT:
            return VideoEffects._slide_transition(clip1, clip2, "left", duration)
        elif transition_type == TransitionType.SLIDE_RIGHT:
            return VideoEffects._slide_transition(clip1, clip2, "right", duration)
        elif transition_type == TransitionType.SLIDE_UP:
            return VideoEffects._slide_transition(clip1, clip2, "up", duration)
        elif transition_type == TransitionType.SLIDE_DOWN:
            return VideoEffects._slide_transition(clip1, clip2, "down", duration)
        elif transition_type == TransitionType.ZOOM_IN:
            return VideoEffects._zoom_transition(clip1, clip2, "in", duration)
        elif transition_type == TransitionType.ZOOM_OUT:
            return VideoEffects._zoom_transition(clip1, clip2, "out", duration)
        elif transition_type == TransitionType.WIPE_LEFT:
            return VideoEffects._wipe_transition(clip1, clip2, "left", duration)
        elif transition_type == TransitionType.WIPE_RIGHT:
            return VideoEffects._wipe_transition(clip1, clip2, "right", duration)
        else:
            # Par défaut: simple concaténation
            return concatenate_videoclips([clip1, clip2])
    
    @staticmethod
    def _slide_transition(clip1, clip2, direction: str, duration: float):
        """Transition par glissement."""
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.fx.all import slide_in, slide_out
        
        w, h = clip1.w, clip1.h
        
        # Clip 1 sort
        if direction == "left":
            clip1_out = clip1.fx(slide_out, duration, side="right")
            clip2_in = clip2.fx(slide_in, duration, side="left")
        elif direction == "right":
            clip1_out = clip1.fx(slide_out, duration, side="left")
            clip2_in = clip2.fx(slide_in, duration, side="right")
        elif direction == "up":
            clip1_out = clip1.fx(slide_out, duration, side="bottom")
            clip2_in = clip2.fx(slide_in, duration, side="top")
        else:  # down
            clip1_out = clip1.fx(slide_out, duration, side="top")
            clip2_in = clip2.fx(slide_in, duration, side="bottom")
        
        # Partie sans transition
        clip1_part = clip1.subclipped(0, clip1.duration - duration)
        clip2_part = clip2.subclipped(duration, clip2.duration)
        
        # Combiner
        from moviepy import concatenate_videoclips
        
        # Transition
        transition = CompositeVideoClip([
            clip1_out.subclipped(clip1.duration - duration, clip1.duration).with_start(0),
            clip2_in.subclipped(0, duration).with_start(0),
        ])
        
        return concatenate_videoclips([clip1_part, transition, clip2_part])
    
    @staticmethod
    def _zoom_transition(clip1, clip2, zoom_type: str, duration: float):
        """Transition par zoom."""
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy import concatenate_videoclips
        
        def make_frame_zoom_out(t):
            """Zoom out sur clip1."""
            scale = 1 + (1 - t / duration) * 0.5
            return clip1.get_frame(clip1.duration - duration + t)
        
        def make_frame_zoom_in(t):
            """Zoom in sur clip2."""
            scale = 1 + (t / duration) * 0.5
            return clip2.get_frame(t)
        
        # Pour l'instant, utiliser un simple fade
        return VideoEffects.create_transition(clip1, clip2, TransitionType.FADE, duration)
    
    @staticmethod
    def _wipe_transition(clip1, clip2, direction: str, duration: float):
        """Transition par effet wipe (rideau)."""
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy import concatenate_videoclips
        
        # Pour l'instant, utiliser un simple fade
        return VideoEffects.create_transition(clip1, clip2, TransitionType.FADE, duration)


class AnimatedSubtitleGenerator:
    """Générateur de sous-titres animés."""
    
    @staticmethod
    def create_animated_subtitle(
        text: str,
        start_time: float,
        end_time: float,
        video_width: int,
        video_height: int,
        animation: SubtitleAnimation = None,
        font_size: int = 40,
        font_color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 2,
        font: str = "Arial-Bold",
    ):
        """Crée un sous-titre animé.
        
        Args:
            text: Texte du sous-titre
            start_time: Temps de début
            end_time: Temps de fin
            video_width: Largeur de la vidéo
            video_height: Hauteur de la vidéo
            animation: Type d'animation
            font_size: Taille de police
            font_color: Couleur du texte
            stroke_color: Couleur du contour
            stroke_width: Épaisseur du contour
            font: Police
            
        Returns:
            Clip de texte animé
        """
        from moviepy.video.VideoClip import TextClip
        from moviepy.video.fx.all import fadein, fadeout
        
        if animation is None:
            animation = SubtitleAnimation()
        
        duration = end_time - start_time
        
        # Créer le texte de base
        txt_clip = TextClip(
            text,
            fontsize=font_size,
            color=font_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            font=font,
            method="caption",
            align="center",
            size=(video_width * 0.9, None),
        )
        
        # Appliquer l'animation
        if animation.type == "fade":
            # Fade in/out simple
            anim_duration = min(animation.duration, duration / 3)
            txt_clip = txt_clip.with_start(start_time).with_duration(duration)
            txt_clip = txt_clip.fx(fadein, anim_duration).fx(fadeout, anim_duration)
            
        elif animation.type == "slide_up":
            # Glissement vers le haut
            from moviepy.video.fx.all import slide_in
            txt_clip = txt_clip.with_start(start_time).with_duration(duration)
            txt_clip = txt_clip.fx(slide_in, animation.duration, side="bottom")
            txt_clip = txt_clip.fx(fadeout, animation.duration)
            
        elif animation.type == "slide_down":
            # Glissement vers le bas
            from moviepy.video.fx.all import slide_in
            txt_clip = txt_clip.with_start(start_time).with_duration(duration)
            txt_clip = txt_clip.fx(slide_in, animation.duration, side="top")
            txt_clip = txt_clip.fx(fadeout, animation.duration)
            
        elif animation.type == "scale":
            # Zoom progressif
            def scale_effect(get_frame, t):
                """Effet de zoom."""
                from moviepy.video.fx.all import resize
                frame = get_frame(t)
                # Zoom de 0.8 à 1.0
                progress = min(1, t / animation.duration) if animation.duration > 0 else 1
                scale = 0.8 + 0.2 * progress
                # Redimensionner
                return frame  # Simplifié pour l'instant
            
            txt_clip = txt_clip.with_start(start_time).with_duration(duration)
            
        elif animation.type == "typewriter":
            # Effet machine à écrire (lettre par lettre)
            txt_clip = AnimatedSubtitleGenerator._typewriter_effect(
                text, start_time, end_time, video_width, video_height,
                font_size, font_color, stroke_color, stroke_width, font
            )
            
        elif animation.type == "bounce":
            # Effet rebond
            def bounce_effect(get_frame, t):
                """Effet rebond."""
                import numpy as np
                frame = get_frame(t)
                # Simplifié pour l'instant
                return frame
            
            txt_clip = txt_clip.with_start(start_time).with_duration(duration)
            
        else:  # none
            txt_clip = txt_clip.with_start(start_time).with_duration(duration)
        
        # Positionner en bas
        return txt_clip.with_position(("center", "bottom")).with_margin(bottom=50, opacity=0)
    
    @staticmethod
    def _typewriter_effect(
        text: str,
        start_time: float,
        end_time: float,
        video_width: int,
        video_height: int,
        font_size: int,
        font_color: str,
        stroke_color: str,
        stroke_width: int,
        font: str,
    ):
        """Crée un effet machine à écrire."""
        from moviepy.video.VideoClip import TextClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.fx.all import fadein
        
        duration = end_time - start_time
        chars = list(text)
        char_duration = duration / len(chars) if chars else duration
        
        clips = []
        current_text = ""
        
        for i, char in enumerate(chars):
            current_text += char
            txt_clip = TextClip(
                current_text,
                fontsize=font_size,
                color=font_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                font=font,
                method="caption",
                align="center",
                size=(video_width * 0.9, None),
            )
            
            clip_start = start_time + i * char_duration
            clip_duration = char_duration if i < len(chars) - 1 else duration - i * char_duration
            
            txt_clip = txt_clip.with_start(clip_start).with_duration(clip_duration)
            txt_clip = txt_clip.with_position(("center", "bottom")).with_margin(bottom=50, opacity=0)
            
            clips.append(txt_clip)
        
        return CompositeVideoClip(clips)


class PreviewGenerator:
    """Générateur de prévisualisations."""
    
    @staticmethod
    def create_preview(
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
        quality: str = "low",
        max_duration: float = 10.0,
    ):
        """Crée une prévisualisation basse qualité.
        
        Args:
            video_path: Chemin vers la vidéo source
            start_time: Temps de début
            end_time: Temps de fin
            output_path: Chemin de sortie
            quality: Qualité (low, medium)
            max_duration: Durée max de la prévisualisation
        """
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        clip = VideoFileClip(video_path)
        
        # Extraire le segment
        duration = min(end_time - start_time, max_duration)
        preview = clip.subclipped(start_time, start_time + duration)
        
        # Paramètres selon la qualité
        if quality == "low":
            fps = 15
            resolution = (360, 640)  # 360p vertical
            bitrate = "500k"
        else:  # medium
            fps = 24
            resolution = (540, 960)  # 540p vertical
            bitrate = "1000k"
        
        # Redimensionner
        preview_resized = preview.resized(new_size=resolution)
        
        # Exporter
        preview_resized.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=fps,
            bitrate=bitrate,
            preset="ultrafast",  # Rapide mais moins compressé
            threads=4,
        )
        
        clip.close()
        preview.close()
        preview_resized.close()
