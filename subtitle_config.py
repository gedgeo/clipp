"""Module de configuration des sous-titres."""

from typing import Literal


# Positions disponibles pour les sous-titres
SUBTITLE_POSITIONS = {
    "bottom": ("center", "bottom"),  # Bas (défaut)
    "bottom_margin": ("center", 0.85),  # Bas avec marge
    "center": ("center", "center"),  # Centre
    "top": ("center", "top"),  # Haut
    "top_margin": ("center", 0.15),  # Haut avec marge
}

# Polices disponibles (doivent être installées sur le système)
AVAILABLE_FONTS = {
    "Arial": "Arial",
    "Arial-Bold": "Arial-Bold",
    "Helvetica": "Helvetica",
    "Times": "Times",
    "Courier": "Courier",
    "Georgia": "Georgia",
    "Verdana": "Verdana",
    "Impact": "Impact",  # Parfait pour TikTok/Shorts
    "Comic-Sans-MS": "Comic-Sans-MS",
    "Bebas-Neue": "Bebas-Neue",  # Très populaire pour les sous-titres viraux
    "Roboto": "Roboto",
    "Montserrat": "Montserrat",
}

# Tailles de police recommandées
FONT_SIZES = {
    "small": 30,
    "medium": 40,
    "large": 50,
    "xlarge": 60,
}

# Styles de sous-titres populaires sur TikTok/Shorts
SUBTITLE_STYLES = {
    "tiktok_classic": {
        "font": "Impact",
        "font_size": 50,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 3,
        "position": "bottom_margin",
    },
    "youtube_bold": {
        "font": "Arial-Bold",
        "font_size": 45,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 2,
        "position": "bottom",
    },
    "modern_clean": {
        "font": "Montserrat",
        "font_size": 40,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 2,
        "position": "bottom_margin",
    },
    "viral_caps": {
        "font": "Bebas-Neue",
        "font_size": 55,
        "color": "yellow",
        "stroke_color": "black",
        "stroke_width": 3,
        "position": "center",
    },
}


def get_subtitle_config(
    style: str = "tiktok_classic",
    custom_font: str = None,
    custom_size: int = None,
    custom_position: str = None,
    custom_color: str = None,
) -> dict:
    """Retourne la configuration des sous-titres.
    
    Args:
        style: Nom du style prédéfini
        custom_font: Police personnalisée (optionnel)
        custom_size: Taille personnalisée (optionnel)
        custom_position: Position personnalisée (optionnel)
        custom_color: Couleur personnalisée (optionnel)
        
    Returns:
        Dictionnaire de configuration
    """
    config = SUBTITLE_STYLES.get(style, SUBTITLE_STYLES["tiktok_classic"]).copy()
    
    if custom_font:
        config["font"] = custom_font
    if custom_size:
        config["font_size"] = custom_size
    if custom_position:
        config["position"] = custom_position
    if custom_color:
        config["color"] = custom_color
        
    return config


def get_position_coordinates(position_key: str) -> tuple:
    """Retourne les coordonnées de position.
    
    Args:
        position_key: Clé de position
        
    Returns:
        Tuple (horizontal, vertical)
    """
    return SUBTITLE_POSITIONS.get(position_key, SUBTITLE_POSITIONS["bottom"])
