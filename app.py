"""Application Streamlit pour créer des clips TikTok/YouTube Shorts."""

import streamlit as st
from pathlib import Path
import tempfile
import os

from video_processor import VideoProcessor
from video_effects import TransitionType

# Configuration de la page
st.set_page_config(
    page_title="Clipp - Créateur de Clips",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF0050;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #FF0050;
        color: white;
        border-radius: 20px;
        padding: 10px 30px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #E60048;
    }
    .preview-box {
        background-color: #1a1a2e;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #FF0050;
    }
    .feature-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .metric-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎬 Clipp</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Créez des clips pour TikTok, YouTube Shorts et Instagram Reels avec sous-titres animés et transitions</p>', unsafe_allow_html=True)

# Initialisation du processeur
if 'processor' not in st.session_state:
    st.session_state.processor = VideoProcessor()

if 'video_info' not in st.session_state:
    st.session_state.video_info = None

if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None

if 'subtitles' not in st.session_state:
    st.session_state.subtitles = None

if 'scene_changes' not in st.session_state:
    st.session_state.scene_changes = None

if 'preview_path' not in st.session_state:
    st.session_state.preview_path = None

if 'created_clips' not in st.session_state:
    st.session_state.created_clips = []

# Sidebar pour les options
with st.sidebar:
    st.header("⚙️ Configuration")
    
    format_type = st.selectbox(
        "Format de sortie",
        options=["tiktok", "youtube_shorts", "instagram_reels"],
        format_func=lambda x: {
            "tiktok": "TikTok (9:16)",
            "youtube_shorts": "YouTube Shorts (9:16)",
            "instagram_reels": "Instagram Reels (9:16)",
        }[x],
    )
    
    zoom_mode = st.selectbox(
        "Mode de zoom",
        options=["fit", "fill", "center"],
        format_func=lambda x: {
            "fit": "Adapter (bands noires si nécessaire)",
            "fill": "Remplir (crop si nécessaire)",
            "center": "Centrer (pas de redimensionnement)",
        }[x],
        help="fit: montre toute la vidéo | fill: remplit l'écran | center: centre sans changer la taille"
    )
    
    st.divider()
    
    # Options avancées
    st.subheader("🔧 Options avancées")
    
    enable_subtitles = st.checkbox("📝 Générer des sous-titres", value=False)
    
    if enable_subtitles:
        subtitle_lang = st.selectbox(
            "Langue",
            options=["fr", "en", "es", "de", "it", "pt"],
            format_func=lambda x: {
                "fr": "Français",
                "en": "English",
                "es": "Español",
                "de": "Deutsch",
                "it": "Italiano",
                "pt": "Português",
            }[x],
        )
        
        # Configuration du style des sous-titres
        st.markdown("**🎨 Style des sous-titres**")
        
        subtitle_style = st.selectbox(
            "Style prédéfini",
            options=["tiktok_classic", "youtube_bold", "modern_clean", "viral_caps"],
            format_func=lambda x: {
                "tiktok_classic": "🎵 TikTok Classique (Impact)",
                "youtube_bold": "📺 YouTube Bold (Arial)",
                "modern_clean": "✨ Moderne Clean (Montserrat)",
                "viral_caps": "🔥 Viral Caps (Bebas Neue)",
            }[x],
        )
        
        subtitle_font = st.selectbox(
            "Police",
            options=["Impact", "Arial-Bold", "Bebas-Neue", "Montserrat", "Helvetica", "Georgia"],
            format_func=lambda x: {
                "Impact": "Impact (TikTok style)",
                "Arial-Bold": "Arial Bold",
                "Bebas-Neue": "Bebas Neue (Caps)",
                "Montserrat": "Montserrat (Moderne)",
                "Helvetica": "Helvetica",
                "Georgia": "Georgia",
            }[x],
        )
        
        subtitle_position = st.selectbox(
            "Position",
            options=["bottom_margin", "bottom", "center", "top_margin"],
            format_func=lambda x: {
                "bottom_margin": "⬇️ Bas avec marge (recommandé)",
                "bottom": "⬇️ Bas (standard)",
                "center": "⏺️ Centre",
                "top_margin": "⬆️ Haut avec marge",
            }[x],
        )
        
        subtitle_size = st.slider(
            "Taille de police",
            min_value=30,
            max_value=70,
            value=50,
            step=5,
        )
        
        subtitle_color = st.selectbox(
            "Couleur du texte",
            options=["white", "yellow", "cyan", "lime", "pink"],
            format_func=lambda x: {
                "white": "⚪ Blanc",
                "yellow": "🟡 Jaune",
                "cyan": "🔵 Cyan",
                "lime": "🟢 Vert lime",
                "pink": "🩷 Rose",
            }[x],
        )
    else:
        subtitle_lang = "fr"
        subtitle_style = "tiktok_classic"
        subtitle_font = "Impact"
        subtitle_position = "bottom_margin"
        subtitle_size = 50
        subtitle_color = "white"
    
    st.divider()
    st.info("💡 **Astuce**: Le style 'TikTok Classique' avec la police Impact est le plus utilisé pour les clips viraux!")

# Zone principale
tab1, tab2, tab3, tab4 = st.tabs(["📁 Importer", "✂️ Clip Manuel", "🎯 Auto-Détection", "🔗 Assemblage"])

with tab1:
    st.subheader("📁 Importer une vidéo")
    
    uploaded_file = st.file_uploader(
        "Choisissez une vidéo",
        type=["mp4", "avi", "mov", "mkv", "webm"],
        help="Formats supportés: MP4, AVI, MOV, MKV, WEBM"
    )
    
    if uploaded_file is not None:
        # Sauvegarder le fichier temporairement
        if st.session_state.uploaded_file_path is None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                st.session_state.uploaded_file_path = tmp_file.name
                
            # Récupérer les infos
            try:
                st.session_state.video_info = st.session_state.processor.get_video_info(
                    st.session_state.uploaded_file_path
                )
                
                # Générer les sous-titres si activé
                if enable_subtitles:
                    with st.spinner("🎙️ Génération des sous-titres..."):
                        st.session_state.subtitles = st.session_state.processor.generate_subtitles(
                            st.session_state.uploaded_file_path,
                            language=subtitle_lang,
                        )
                        if st.session_state.subtitles:
                            st.success(f"✅ {len(st.session_state.subtitles)} segments de sous-titres générés")
                
                # Détecter les changements de scène
                with st.spinner("🎬 Détection des changements de scène..."):
                    st.session_state.scene_changes = st.session_state.processor.detect_scene_changes(
                        st.session_state.uploaded_file_path
                    )
                    if st.session_state.scene_changes:
                        st.success(f"✅ {len(st.session_state.scene_changes)} changements de scène détectés")
                        
            except Exception as e:
                st.error(f"Erreur lors de la lecture de la vidéo: {e}")
                st.session_state.uploaded_file_path = None
        
        # Afficher les infos
        if st.session_state.video_info:
            info = st.session_state.video_info
            st.success("✅ Vidéo chargée avec succès!")
            
            cols = st.columns(4)
            with cols[0]:
                st.metric("Durée", f"{info['duration']:.1f}s")
            with cols[1]:
                st.metric("Résolution", f"{info['width']}x{info['height']}")
            with cols[2]:
                st.metric("FPS", f"{info['fps']:.0f}")
            with cols[3]:
                ratio = info['aspect_ratio']
                ratio_str = f"{ratio:.2f}:1"
                if ratio > 1.7:
                    ratio_str = "16:9 (Paysage)"
                elif ratio < 0.8:
                    ratio_str = "9:16 (Portrait)"
                elif 1.3 < ratio < 1.4:
                    ratio_str = "4:3"
                st.metric("Format", ratio_str)
            
            # Afficher les sous-titres si générés
            if st.session_state.subtitles:
                with st.expander("📝 Voir les sous-titres générés"):
                    for i, sub in enumerate(st.session_state.subtitles[:10]):
                        st.text(f"[{sub['start']:.1f}s - {sub['end']:.1f}s]: {sub['text']}")
                    if len(st.session_state.subtitles) > 10:
                        st.info(f"... et {len(st.session_state.subtitles) - 10} segments supplémentaires")
            
            # Afficher les changements de scène
            if st.session_state.scene_changes:
                with st.expander("🎬 Voir les changements de scène"):
                    st.write(f"Timestamps: {', '.join([f'{t:.1f}s' for t in st.session_state.scene_changes[:20]])}")

with tab2:
    st.subheader("✂️ Créer un clip avec Prévisualisation")
    
    if st.session_state.video_info:
        info = st.session_state.video_info
        max_duration = info['duration']
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Sélection des timestamps
            start_time = st.slider(
                "Début",
                min_value=0.0,
                max_value=max_duration - 1,
                value=0.0,
                step=1.0,
                format="%.1fs",
            )
            
            end_time = st.slider(
                "Fin",
                min_value=start_time + 1,
                max_value=max_duration,
                value=min(start_time + 30, max_duration),
                step=1.0,
                format="%.1fs",
            )
        
        with col_right:
            clip_duration = end_time - start_time
            st.info(f"⏱️ Durée du clip: **{clip_duration:.1f}s**")
            
            # Afficher les sous-titres dans cette plage
            if st.session_state.subtitles:
                segment_subs = [
                    s for s in st.session_state.subtitles
                    if s['start'] >= start_time and s['end'] <= end_time
                ]
                if segment_subs:
                    st.write("📝 Sous-titres dans ce segment:")
                    for sub in segment_subs[:3]:
                        st.caption(f"• {sub['text']}")
        
        # Boutons d'action
        col_prev, col_create = st.columns(2)
        
        with col_prev:
            if st.button("👁️ Prévisualiser (10s)", use_container_width=True):
                with st.spinner("Génération de la prévisualisation..."):
                    try:
                        preview_path = st.session_state.processor.create_preview(
                            video_path=str(st.session_state.uploaded_file_path),
                            start_time=start_time,
                            end_time=end_time,
                            quality="low",
                            max_duration=10.0,
                        )
                        st.session_state.preview_path = preview_path
                        st.success("✅ Prévisualisation créée!")
                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")
        
        with col_create:
            if st.button("🚀 Créer le clip final", use_container_width=True, type="primary"):
                with st.spinner("Création du clip en cours..."):
                    try:
                        # Filtrer les sous-titres pour ce segment
                        segment_subs = None
                        if enable_subtitles and st.session_state.subtitles:
                            segment_subs = [
                                s for s in st.session_state.subtitles
                                if s['start'] >= start_time and s['end'] <= end_time
                            ]
                            for s in segment_subs:
                                s['start'] -= start_time
                                s['end'] -= start_time
                        
                        # Créer avec sous-titres animés si activé
                        if enable_subtitles and subtitle_animation != "none":
                            output_path = st.session_state.processor.create_clip_with_animated_subtitles(
                                video_path=str(st.session_state.uploaded_file_path),
                                start_time=start_time,
                                end_time=end_time,
                                format_type=format_type,
                                zoom_mode=zoom_mode,
                                subtitles_list=segment_subs,
                                subtitle_animation=subtitle_animation,
                            )
                        else:
                            output_path = st.session_state.processor.create_clip(
                                video_path=str(st.session_state.uploaded_file_path),
                                start_time=start_time,
                                end_time=end_time,
                                format_type=format_type,
                                zoom_mode=zoom_mode,
                                add_subtitles=enable_subtitles,
                                subtitles_list=segment_subs,
                            )
                        
                        st.success(f"✅ Clip créé: {Path(output_path).name}")
                        
                        # Ajouter à la liste des clips créés
                        st.session_state.created_clips.append(output_path)
                        
                        # Bouton de téléchargement
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="📥 Télécharger le clip",
                                data=f,
                                file_name=Path(output_path).name,
                                mime="video/mp4",
                                use_container_width=True,
                            )
                            
                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")
                        st.exception(e)
        
        # Afficher la prévisualisation
        if st.session_state.preview_path and Path(st.session_state.preview_path).exists():
            st.markdown('<div class="preview-box">', unsafe_allow_html=True)
            st.subheader("👁️ Prévisualisation")
            st.video(st.session_state.preview_path)
            st.caption("⚠️ Prévisualisation basse qualité (360p) - Le rendu final sera en 1080p")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Importez d'abord une vidéo dans l'onglet 'Importer'")

with tab3:
    st.subheader("🎯 Génération automatique de clips")
    
    if st.session_state.video_info:
        # Mode Super Auto - One Click
        st.markdown("### 🤖 Mode Super Auto (One-Click)")
        st.info("Ce mode analyse automatiquement votre vidéo et génère les meilleurs clips sans aucune configuration!")
        
        col_auto1, col_auto2, col_auto3 = st.columns(3)
        with col_auto1:
            auto_num_clips = st.number_input("Nombre de clips à générer", min_value=1, max_value=10, value=3, key="auto_num")
        with col_auto2:
            auto_duration = st.number_input("Durée cible par clip (s)", min_value=15.0, max_value=60.0, value=30.0, step=5.0, key="auto_duration")
        with col_auto3:
            auto_assemble = st.checkbox("Assembler automatiquement", value=True, help="Crée une vidéo finale avec toutes les transitions")
        
        if st.button("🚀 GÉNÉRATION AUTO COMPLÈTE", use_container_width=True, type="primary"):
            with st.spinner("🎬 Analyse intelligente et génération automatique en cours..."):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Utiliser la nouvelle méthode automatique
                    status_text.text("🧠 Analyse multi-critères de la vidéo...")
                    
                    results = st.session_state.processor.generate_clips_auto(
                        video_path=str(st.session_state.uploaded_file_path),
                        output_prefix="auto_clip",
                        num_clips=int(auto_num_clips),
                        clip_duration=auto_duration,
                        format_type=format_type,
                        zoom_mode="fill",  # Toujours fill pour l'auto
                        enable_subtitles=enable_subtitles,
                        subtitle_animation=subtitle_animation if enable_subtitles else "none",
                        detection_method="smart",
                        add_transitions=auto_assemble,
                        transition_type="fade",
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Génération terminée!")
                    
                    if results["success"]:
                        st.success(f"✅ {len(results['clips'])} clips générés automatiquement!")
                        
                        # Afficher les clips créés
                        st.subheader("📥 Clips générés")
                        for i, clip_info in enumerate(results["clips"]):
                            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                            with col_dl1:
                                st.write(f"**Clip {i+1}**")
                            with col_dl2:
                                st.caption(f"{clip_info['start']:.1f}s - {clip_info['end']:.1f}s")
                            with col_dl3:
                                with open(clip_info["path"], "rb") as f:
                                    st.download_button(
                                        label="📥",
                                        data=f,
                                        file_name=Path(clip_info["path"]).name,
                                        mime="video/mp4",
                                        key=f"auto_dl_{i}",
                                    )
                            
                            # Ajouter à la liste
                            st.session_state.created_clips.append(clip_info["path"])
                        
                        # Afficher la vidéo assemblée si créée
                        if results.get("assembled"):
                            st.subheader("🎬 Vidéo finale assemblée")
                            st.video(results["assembled"])
                            with open(results["assembled"], "rb") as f:
                                st.download_button(
                                    label="📥 Télécharger la vidéo complète",
                                    data=f,
                                    file_name="auto_clip_assembled.mp4",
                                    mime="video/mp4",
                                    use_container_width=True,
                                )
                        
                        # Résumé
                        with st.expander("📊 Détails de la génération"):
                            st.write(f"**Méthode utilisée:** {results['method_used']}")
                            st.write(f"**Sous-titres générés:** {'Oui' if results['subtitles'] else 'Non'}")
                            st.write(f"**Moments détectés:** {len(results['detected_moments'])}")
                            for i, (start, end) in enumerate(results['detected_moments']):
                                st.write(f"  • Clip {i+1}: {start:.1f}s - {end:.1f}s")
                    else:
                        st.error(f"❌ Erreur: {results.get('error', 'Inconnue')}")
                        
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                    st.exception(e)
        
        st.divider()
        st.markdown("### ⚙️ Mode Avancé (Configuration manuelle)")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            num_clips = st.number_input("Nombre de clips", min_value=1, max_value=20, value=5)
        with col4:
            clip_duration_auto = st.number_input(
                "Durée par clip (s)", 
                min_value=5.0, 
                max_value=120.0, 
                value=30.0,
                step=5.0
            )
        with col5:
            detection_method = st.selectbox(
                "Méthode de détection",
                options=["smart", "audio_peaks", "scene_change", "equal"],
                format_func=lambda x: {
                    "smart": "🧠 Intelligent (recommandé)",
                    "audio_peaks": "🔊 Pics audio",
                    "scene_change": "🎬 Changements de scène",
                    "equal": "⚖️ Division égale",
                }[x],
            )
        
        # Paramètres avancés
        with st.expander("🔧 Paramètres avancés"):
            min_gap = st.slider(
                "Espace minimum entre clips (s)",
                min_value=0.0,
                max_value=30.0,
                value=5.0,
                step=1.0,
                help="Évite les chevauchements entre clips"
            )
        
        st.write("")
        if st.button("🎲 Générer avec paramètres", use_container_width=True):
            with st.spinner("Analyse et génération des clips en cours..."):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Étape 1: Détection des moments
                    status_text.text("🔍 Détection des moments intéressants...")
                    time_ranges = st.session_state.processor.auto_detect_moments(
                        str(st.session_state.uploaded_file_path),
                        clip_duration=clip_duration_auto,
                        num_clips=int(num_clips),
                        detection_method=detection_method,
                        min_gap=min_gap,
                    )
                    progress_bar.progress(20)
                    
                    # Étape 2: Génération des clips
                    status_text.text(f"🎬 Création de {len(time_ranges)} clips...")
                    
                    # Utiliser les sous-titres animés si activé
                    if enable_subtitles and subtitle_animation != "none":
                        output_paths = []
                        for i, (start, end) in enumerate(time_ranges):
                            segment_subs = None
                            if st.session_state.subtitles:
                                segment_subs = [
                                    s for s in st.session_state.subtitles
                                    if s['start'] >= start and s['end'] <= end
                                ]
                                for s in segment_subs:
                                    s['start'] -= start
                                    s['end'] -= start
                            
                            path = st.session_state.processor.create_clip_with_animated_subtitles(
                                video_path=str(st.session_state.uploaded_file_path),
                                start_time=start,
                                end_time=end,
                                output_name=f"clip_{i+1:03d}_animated.mp4",
                                format_type=format_type,
                                zoom_mode=zoom_mode,
                                subtitles_list=segment_subs,
                                subtitle_animation=subtitle_animation,
                            )
                            output_paths.append(path)
                            progress_bar.progress(20 + int(60 * (i + 1) / len(time_ranges)))
                    else:
                        output_paths = st.session_state.processor.create_multiple_clips(
                            video_path=str(st.session_state.uploaded_file_path),
                            time_ranges=time_ranges,
                            format_type=format_type,
                            zoom_mode=zoom_mode,
                            add_subtitles=enable_subtitles,
                            subtitles_list=st.session_state.subtitles,
                        )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Terminé!")
                    
                    st.success(f"✅ {len(output_paths)} clips créés avec succès!")
                    
                    # Ajouter à la liste
                    st.session_state.created_clips.extend(output_paths)
                    
                    # Afficher les liens de téléchargement
                    st.subheader("📥 Télécharger les clips")
                    
                    for i, path in enumerate(output_paths):
                        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                        with col_dl1:
                            st.write(f"**Clip {i+1}**")
                        with col_dl2:
                            st.caption(f"{Path(path).name}")
                        with col_dl3:
                            with open(path, "rb") as f:
                                st.download_button(
                                    label="📥",
                                    data=f,
                                    file_name=Path(path).name,
                                    mime="video/mp4",
                                    key=f"dl_{path}",
                                )
                    
                    # Résumé
                    with st.expander("📊 Résumé des clips"):
                        for i, (start, end) in enumerate(time_ranges):
                            st.write(f"**Clip {i+1}:** {start:.1f}s - {end:.1f}s (durée: {end-start:.1f}s)")
                            
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                    st.exception(e)
    else:
        st.info("👆 Importez d'abord une vidéo dans l'onglet 'Importer'")

with tab4:
    st.subheader("🔗 Assemblage de clips avec Transitions")
    
    if st.session_state.created_clips:
        st.write(f"📁 {len(st.session_state.created_clips)} clips disponibles pour l'assemblage")
        
        # Afficher les clips créés
        with st.expander("📋 Voir les clips créés"):
            for i, clip_path in enumerate(st.session_state.created_clips):
                st.text(f"{i+1}. {Path(clip_path).name}")
        
        # Options de transition
        col_trans1, col_trans2 = st.columns(2)
        
        with col_trans1:
            transition_type = st.selectbox(
                "Type de transition",
                options=["fade", "crossfade", "slide_left", "slide_right", "slide_up", "slide_down"],
                format_func=lambda x: {
                    "fade": "✨ Fondu",
                    "crossfade": "🔄 Fondu enchaîné",
                    "slide_left": "⬅️ Glissement gauche",
                    "slide_right": "➡️ Glissement droite",
                    "slide_up": "⬆️ Glissement haut",
                    "slide_down": "⬇️ Glissement bas",
                }[x],
            )
        
        with col_trans2:
            transition_duration = st.slider(
                "Durée de transition (s)",
                min_value=0.2,
                max_value=2.0,
                value=0.5,
                step=0.1,
            )
        
        if st.button("🔗 Assembler tous les clips", use_container_width=True, type="primary"):
            with st.spinner("Assemblage avec transitions..."):
                try:
                    output_path = st.session_state.processor.concatenate_clips_with_transitions(
                        video_paths=st.session_state.created_clips,
                        output_name="assembled_video.mp4",
                        transition_type=transition_type,
                        transition_duration=transition_duration,
                        format_type=format_type,
                    )
                    
                    st.success(f"✅ Vidéo assemblée: {Path(output_path).name}")
                    
                    # Afficher la vidéo
                    st.video(output_path)
                    
                    # Bouton de téléchargement
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger la vidéo assemblée",
                            data=f,
                            file_name="assembled_video.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )
                        
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                    st.exception(e)
        
        # Option pour vider la liste
        if st.button("🗑️ Vider la liste des clips", use_container_width=True):
            st.session_state.created_clips = []
            st.rerun()
    else:
        st.info("👆 Créez d'abord des clips dans les onglets précédents pour les assembler")

# Section informations
st.divider()
with st.expander("ℹ️ Guide des fonctionnalités"):
    st.markdown("""
    ### 🚀 Nouvelles fonctionnalités
    
    #### ✨ Sous-titres Animés
    Choisissez parmi 6 animations différentes:
    - **Fondu**: Apparition/disparition progressive
    - **Glissement**: Entrée depuis le haut ou le bas
    - **Zoom**: Agrandissement progressif
    - **Machine à écrire**: Lettres qui apparaissent une par une
    - **Rebond**: Effet de rebond à l'apparition
    
    #### 👁️ Prévisualisation
    - Visualisez vos clips avant export final
    - Rendu rapide en 360p (10s max)
    - Permet de vérifier les sous-titres et le cadrage
    
    #### 🔗 Assemblage avec Transitions
    - Combinez plusieurs clips en une seule vidéo
    - 6 types de transitions disponibles:
      - Fondu simple et enchaîné
      - Glissements dans 4 directions
    - Durée de transition configurable (0.2s - 2s)
    
    ### 📖 Guide d'utilisation
    
    1. **Importer** votre vidéo
    2. **Créer des clips** manuellement ou automatiquement
    3. **Prévisualiser** avant export
    4. **Assembler** les clips avec des transitions (optionnel)
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🎬 <b>Clipp</b> - Créez facilement des contenus pour les réseaux sociaux</p>
    <p style="font-size: 0.8rem;">
        Fonctionnalités: Sous-titres animés | Prévisualisation | Transitions | Détection audio/scène
    </p>
</div>
""", unsafe_allow_html=True)

# Nettoyage
if st.session_state.uploaded_file_path and not uploaded_file:
    try:
        os.unlink(st.session_state.uploaded_file_path)
    except:
        pass
    st.session_state.uploaded_file_path = None
    st.session_state.video_info = None
    st.session_state.subtitles = None
    st.session_state.scene_changes = None
    st.session_state.preview_path = None
    st.rerun()
