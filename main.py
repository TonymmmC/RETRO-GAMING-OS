#!/usr/bin/env python3
"""
Gaming Modern OS - Boot Loader Principal con Música de Fondo
Sistema operativo moderno para juegos con sistema de configuración completo
"""

import pygame
import sys
import os
import time
import json
import math
from pathlib import Path

# Importar módulos del sistema
try:
    from ui.game_launcher import GameLauncher
except ImportError:
    GameLauncher = None
    print("⚠️ Advertencia: ui.game_launcher no encontrado. Usando lanzador simple.")

try:
    from ui.settings_manager import SettingsManager
except ImportError:
    SettingsManager = None
    print("⚠️ Advertencia: ui.settings_manager no encontrado. Settings deshabilitado.")

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

class GamingModernOS:
    """
    Clase principal para el Gaming Modern OS.
    Sistema operativo gaming con diseño moderno y minimalista.
    """
    def __init__(self):
        # Configuración del sistema por defecto
        self.default_config = {
            "theme": "dark",
            "resolution": [1100, 700],
            "fullscreen": False,
            "sound_enabled": True,
            "boot_animation": True,
            "performance_mode": "balanced",
            "auto_scan_games": True,
            "minimize_to_tray": False,
            "auto_save_settings": True,
            "check_updates": True,
            "master_volume": 80,
            "music_volume": 60,
            "fps_limit": 60,
            "games_directory": "./games/",
            "last_played": []
        }
        
        self.config = self.default_config.copy()
        self.load_config()
        
        # Configurar pantalla según configuración
        self.apply_display_settings()
        
        # Variables de música
        self.main_music_playing = False
        self.main_music_path = "assets/sounds/main/main.mp3"
        self.music_initialized = False
        
        # Tema moderno - Colores flat y limpios
        self.colors = {
            "bg_primary": (26, 26, 26),          # #1a1a1a - Fondo principal oscuro
            "bg_secondary": (45, 45, 45),        # #2d2d2d - Fondo de cards
            "bg_surface": (61, 61, 61),          # #3d3d3d - Superficie elevada
            "text_primary": (255, 255, 255),     # #ffffff - Texto principal
            "text_secondary": (160, 160, 160),   # #a0a0a0 - Texto secundario
            "accent": (0, 122, 255),             # #007AFF - Azul moderno de acento
            "success": (52, 199, 89),            # #34C759 - Verde éxito
            "warning": (255, 149, 0),            # #FF9500 - Naranja advertencia
            "danger": (255, 59, 48),             # #FF3B30 - Rojo peligro
            "shadow": (0, 0, 0, 60),             # Sombra suave
            "overlay": (0, 0, 0, 180)            # Overlay modal
        }
        
        # Aplicar tema según configuración
        self.apply_theme()
        
        # Fuentes modernas (Inter-style)
        self.fonts = {
            "heading_xl": pygame.font.Font(None, 48),    # Títulos principales
            "heading_lg": pygame.font.Font(None, 36),    # Títulos sección
            "heading_md": pygame.font.Font(None, 28),    # Subtítulos
            "body_lg": pygame.font.Font(None, 22),       # Texto normal grande
            "body_md": pygame.font.Font(None, 18),       # Texto normal
            "body_sm": pygame.font.Font(None, 16),       # Texto pequeño
            "caption": pygame.font.Font(None, 14),       # Captions
            "tiny": pygame.font.Font(None, 12)           # Texto muy pequeño
        }
        
        # Estados del sistema
        self.current_state = "boot"
        self.boot_progress = 0
        self.boot_messages = [
            "Initializing system...",
            "Loading game library...",
            "Loading settings...",
            "Loading audio...",
            "Preparing interface...",
            "System ready!"
        ]
        self.boot_message_index = 0
        self.boot_start_time = time.time()
        
        # Control del juego
        self.clock = pygame.time.Clock()
        self.selected_option = 0
        self.animation_time = 0
        
        # Inicializar módulos
        self.game_launcher = None
        self.settings_manager = None
        
        if GameLauncher:
            self.game_launcher = GameLauncher(self.screen, self.colors, self.fonts)
        else:
            self.games = self.scan_games_simple()
        
        if SettingsManager:
            self.settings_manager = SettingsManager(
                self.screen, self.colors, self.fonts, self.config,
                save_callback=self.on_settings_saved
            )
        
        # Inicializar música
        self.initialize_music()
        
        print(f"🎮 Gaming Modern OS iniciado")
        print(f"🎯 Game launcher: {'Advanced' if self.game_launcher else 'Simple'}")
        print(f"⚙️ Settings: {'Available' if self.settings_manager else 'Disabled'}")
        print(f"🎵 Main music: {'Available' if self.music_initialized else 'Not found'}")
    
    def initialize_music(self):
        """Inicializar sistema de música"""
        try:
            # Crear directorio de assets si no existe
            assets_dir = Path("assets/sounds/main")
            assets_dir.mkdir(parents=True, exist_ok=True)
            
            # Verificar si existe el archivo de música
            music_path = Path(self.main_music_path)
            if music_path.exists():
                self.music_initialized = True
                print(f"✓ Música encontrada: {self.main_music_path}")
            else:
                self.music_initialized = False
                print(f"⚠️ Música no encontrada: {self.main_music_path}")
                print("💡 Coloca tu archivo main.mp3 en assets/sounds/main/")
                
        except Exception as e:
            print(f"❌ Error inicializando música: {e}")
            self.music_initialized = False
    
    def play_main_music(self):
        """Reproducir música principal en bucle"""
        if not self.music_initialized or not self.config.get("sound_enabled", True):
            return
            
        try:
            if not self.main_music_playing:
                # Configurar volumen según configuración
                music_volume = self.config.get("music_volume", 60) / 100
                pygame.mixer.music.set_volume(music_volume)
                
                # Cargar y reproducir música en bucle
                pygame.mixer.music.load(self.main_music_path)
                pygame.mixer.music.play(-1)  # -1 = bucle infinito
                self.main_music_playing = True
                print("🎵 Música principal iniciada")
                
        except Exception as e:
            print(f"❌ Error reproduciendo música: {e}")
            self.music_initialized = False
    
    def stop_main_music(self):
        """Detener música principal"""
        try:
            if self.main_music_playing:
                pygame.mixer.music.stop()
                self.main_music_playing = False
                print("🎵 Música principal detenida")
        except Exception as e:
            print(f"❌ Error deteniendo música: {e}")
    
    def update_music_volume(self):
        """Actualizar volumen de música según configuración"""
        if self.main_music_playing:
            try:
                music_volume = self.config.get("music_volume", 60) / 100
                pygame.mixer.music.set_volume(music_volume)
            except:
                pass
    
    def should_play_main_music(self):
        """Determinar si debe reproducirse la música principal"""
        # Solo en estados del menú principal
        menu_states = ["boot", "main_menu", "settings", "system_info"]
        return self.current_state in menu_states
    
    def apply_display_settings(self):
        """Aplicar configuración de pantalla"""
        resolution = self.config.get("resolution", [1100, 700])
        fullscreen = self.config.get("fullscreen", False)
        
        if fullscreen:
            self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(resolution)
        
        pygame.display.set_caption("Gaming Modern OS v2.1")
    
    def apply_theme(self):
        """Aplicar tema según configuración"""
        theme = self.config.get("theme", "dark")
        
        if theme == "light":
            self.colors.update({
                "bg_primary": (248, 249, 250),       # #f8f9fa
                "bg_secondary": (255, 255, 255),     # #ffffff
                "bg_surface": (233, 236, 239),       # #e9ecef
                "text_primary": (33, 37, 41),        # #212529
                "text_secondary": (108, 117, 125),   # #6c757d
                "shadow": (0, 0, 0, 30),
                "overlay": (255, 255, 255, 180)
            })
        elif theme == "auto":
            # Determinar tema basado en la hora
            current_hour = time.localtime().tm_hour
            if 6 <= current_hour <= 18:  # Día
                self.apply_light_theme()
            else:  # Noche
                self.apply_dark_theme()
    
    def apply_light_theme(self):
        """Aplicar tema claro"""
        self.colors.update({
            "bg_primary": (248, 249, 250),
            "bg_secondary": (255, 255, 255),
            "bg_surface": (233, 236, 239),
            "text_primary": (33, 37, 41),
            "text_secondary": (108, 117, 125),
            "shadow": (0, 0, 0, 30),
            "overlay": (255, 255, 255, 180)
        })
    
    def apply_dark_theme(self):
        """Aplicar tema oscuro"""
        self.colors.update({
            "bg_primary": (26, 26, 26),
            "bg_secondary": (45, 45, 45),
            "bg_surface": (61, 61, 61),
            "text_primary": (255, 255, 255),
            "text_secondary": (160, 160, 160),
            "shadow": (0, 0, 0, 60),
            "overlay": (0, 0, 0, 180)
        })
    
    def on_settings_saved(self, new_config):
        """Callback cuando se guardan las configuraciones"""
        old_resolution = self.config.get("resolution")
        old_fullscreen = self.config.get("fullscreen")
        old_theme = self.config.get("theme")
        old_music_volume = self.config.get("music_volume")
        old_sound_enabled = self.config.get("sound_enabled")
        
        # Actualizar configuración
        self.config.update(new_config)
        
        # Aplicar cambios si es necesario
        new_resolution = self.config.get("resolution")
        new_fullscreen = self.config.get("fullscreen")
        new_theme = self.config.get("theme")
        new_music_volume = self.config.get("music_volume")
        new_sound_enabled = self.config.get("sound_enabled")
        
        # Cambios de pantalla
        if (old_resolution != new_resolution or old_fullscreen != new_fullscreen):
            self.apply_display_settings()
            # Reinicializar módulos que dependen de la pantalla
            if self.game_launcher:
                self.game_launcher = GameLauncher(self.screen, self.colors, self.fonts)
            if self.settings_manager:
                self.settings_manager.screen = self.screen
        
        # Cambios de tema
        if old_theme != new_theme:
            self.apply_theme()
            # Actualizar colores en módulos
            if self.game_launcher:
                self.game_launcher.colors = self.colors
            if self.settings_manager:
                self.settings_manager.colors = self.colors
        
        # Cambios de audio
        if old_music_volume != new_music_volume:
            self.update_music_volume()
        
        if old_sound_enabled != new_sound_enabled:
            if new_sound_enabled and self.should_play_main_music():
                self.play_main_music()
            elif not new_sound_enabled:
                self.stop_main_music()
        
        print(f"⚙️ Configuración actualizada: {len(new_config)} opciones")
    
    def load_config(self):
        """Carga configuración del sistema"""
        config_path = Path("config/settings.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                print(f"✓ Configuración cargada: {config_path}")
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                self.config = self.default_config.copy()
        else:
            print("📝 Usando configuración por defecto")
    
    def save_config(self):
        """Guarda configuración del sistema"""
        config_path = Path("config")
        config_path.mkdir(exist_ok=True)
        
        try:
            with open(config_path / "settings.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✓ Configuración guardada")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def scan_games_simple(self):
        """Escanea juegos en modo simple"""
        allowed_games = ["snake", "tetris", "pong", "breakout"]
        games_found = []
        builtin_dir = Path("games/builtin")
        
        if builtin_dir.exists():
            for game_name in allowed_games:
                file_path = builtin_dir / f"{game_name}.py"
                if file_path.exists():
                    title_map = {
                        "snake": "Snake Modern",
                        "tetris": "Tetris Modern",
                        "pong": "Pong Modern",
                        "breakout": "Breakout Modern"
                    }
                    games_found.append({
                        "title": title_map.get(game_name, game_name.title()),
                        "filename": file_path.name,
                        "path": str(file_path),
                        "category": "Arcade"
                    })
        return games_found
    
    def play_ui_sound(self, sound_type="click"):
        """Reproduce sonidos modernos de UI"""
        if not self.config.get("sound_enabled", True):
            return
        
        try:
            frequencies = {
                "click": 1200,
                "hover": 800,
                "success": 1600,
                "error": 400,
                "navigate": 1000
            }
            
            frequency = frequencies.get(sound_type, 800)
            duration = 60
            volume = self.config.get("master_volume", 80) / 100 * 0.1
            
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            
            for i in range(frames):
                t = float(i) / sample_rate
                envelope = math.exp(-t * 8)
                wave = math.sin(2 * math.pi * frequency * t) * envelope * volume
                arr.append([int(32767 * wave)] * 2)
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except:
            pass
    
    def draw_modern_card(self, surface, rect, elevation=1):
        """Dibuja una card moderna con sombra"""
        shadow_offset = elevation * 2
        shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, 
                                 rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.colors["shadow"], 
                        (0, 0, rect.width, rect.height), border_radius=12)
        surface.blit(shadow_surface, shadow_rect.topleft)
        
        pygame.draw.rect(surface, self.colors["bg_secondary"], rect, border_radius=12)
    
    def draw_boot_screen(self):
        """Pantalla de arranque moderna"""
        self.screen.fill(self.colors["bg_primary"])
        
        # Logo moderno centrado
        logo_text = self.fonts["heading_xl"].render("Gaming OS", True, self.colors["text_primary"])
        logo_x = (self.screen.get_width() - logo_text.get_width()) // 2
        self.screen.blit(logo_text, (logo_x, 200))
        
        # Subtítulo
        subtitle = self.fonts["body_lg"].render("Modern Gaming Experience", True, self.colors["text_secondary"])
        subtitle_x = (self.screen.get_width() - subtitle.get_width()) // 2
        self.screen.blit(subtitle, (subtitle_x, 250))
        
        # Versión
        version = self.fonts["caption"].render("v2.1 - With Audio System", True, self.colors["text_secondary"])
        version_x = (self.screen.get_width() - version.get_width()) // 2
        self.screen.blit(version, (version_x, 280))
        
        # Indicador de música
        if self.music_initialized:
            music_status = "🎵 Audio Ready"
            music_color = self.colors["success"]
        else:
            music_status = "🔇 No Background Music"
            music_color = self.colors["warning"]
        
        music_text = self.fonts["caption"].render(music_status, True, music_color)
        music_x = (self.screen.get_width() - music_text.get_width()) // 2
        self.screen.blit(music_text, (music_x, 300))
        
        # Mensaje de estado
        if self.boot_message_index < len(self.boot_messages):
            message = self.boot_messages[self.boot_message_index]
            message_text = self.fonts["body_md"].render(message, True, self.colors["text_secondary"])
            message_x = (self.screen.get_width() - message_text.get_width()) // 2
            self.screen.blit(message_text, (message_x, 350))
        
        # Barra de progreso moderna
        progress_width = 300
        progress_height = 4
        progress_x = (self.screen.get_width() - progress_width) // 2
        progress_y = 400
        
        # Fondo de la barra
        bg_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
        pygame.draw.rect(self.screen, self.colors["bg_surface"], bg_rect, border_radius=2)
        
        # Progreso
        fill_width = int((self.boot_progress / 100) * progress_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(progress_x, progress_y, fill_width, progress_height)
            pygame.draw.rect(self.screen, self.colors["accent"], fill_rect, border_radius=2)
    
    def draw_main_interface(self):
        """Interfaz principal moderna"""
        self.screen.fill(self.colors["bg_primary"])
        
        # Header
        header_rect = pygame.Rect(0, 0, self.screen.get_width(), 80)
        pygame.draw.rect(self.screen, self.colors["bg_secondary"], header_rect)
        
        # Título en header
        title = self.fonts["heading_lg"].render("Gaming Library", True, self.colors["text_primary"])
        self.screen.blit(title, (30, 25))
        
        # Indicador de música en header
        if self.main_music_playing:
            music_indicator = "🎵"
            music_color = self.colors["success"]
        else:
            music_indicator = "🔇"
            music_color = self.colors["text_secondary"]
        
        music_text = self.fonts["body_md"].render(music_indicator, True, music_color)
        self.screen.blit(music_text, (self.screen.get_width() - 180, 30))
        
        # Información de sistema en header
        theme_info = f"Theme: {self.config.get('theme', 'dark').title()}"
        theme_text = self.fonts["caption"].render(theme_info, True, self.colors["text_secondary"])
        theme_x = self.screen.get_width() - theme_text.get_width() - 150
        self.screen.blit(theme_text, (theme_x, 25))
        
        # Hora en header (derecha)
        current_time = time.strftime("%H:%M")
        time_text = self.fonts["body_md"].render(current_time, True, self.colors["text_secondary"])
        time_x = self.screen.get_width() - time_text.get_width() - 30
        self.screen.blit(time_text, (time_x, 30))
        
        # Opciones principales como cards modernas
        if self.game_launcher and self.settings_manager:
            options = [
                {"title": "Game Library", "subtitle": "Browse and play games", "icon": "🎮"},
                {"title": "Settings", "subtitle": "System preferences", "icon": "⚙️"},
                {"title": "System Info", "subtitle": "View system status", "icon": "📊"},
                {"title": "Exit", "subtitle": "Close Gaming OS", "icon": "🚪"}
            ]
        elif self.game_launcher:
            options = [
                {"title": "Game Library", "subtitle": "Browse and play games", "icon": "🎮"},
                {"title": "Settings", "subtitle": "System preferences (Limited)", "icon": "⚙️"},
                {"title": "Exit", "subtitle": "Close Gaming OS", "icon": "🚪"}
            ]
        else:
            options = [
                {"title": "Snake Modern", "subtitle": "Classic snake with modern UI", "icon": "🐍"},
                {"title": "Tetris Modern", "subtitle": "Block puzzle game", "icon": "🧩"},
                {"title": "Pong Modern", "subtitle": "Two-player classic", "icon": "🏓"},
                {"title": "Breakout Modern", "subtitle": "Break all the bricks", "icon": "🧱"},
                {"title": "Exit", "subtitle": "Close Gaming OS", "icon": "🚪"}
            ]
        
        # Dibujar cards de opciones
        start_y = 120
        card_height = 80
        card_margin = 20
        
        for i, option in enumerate(options):
            is_selected = i == self.selected_option
            
            # Posición de la card
            card_rect = pygame.Rect(50, start_y + i * (card_height + card_margin), 
                                   self.screen.get_width() - 100, card_height)
            
            # Efecto hover/selección
            if is_selected:
                pulse = 0.95 + 0.05 * math.sin(self.animation_time * 0.1)
                card_color = tuple(int(c * pulse) for c in self.colors["bg_surface"])
            else:
                card_color = self.colors["bg_secondary"]
            
            # Dibujar card
            self.draw_modern_card(self.screen, card_rect, elevation=2 if is_selected else 1)
            if is_selected:
                pygame.draw.rect(self.screen, card_color, card_rect, border_radius=12)
                pygame.draw.rect(self.screen, self.colors["accent"], card_rect, width=2, border_radius=12)
            else:
                pygame.draw.rect(self.screen, card_color, card_rect, border_radius=12)
            
            # Contenido de la card
            icon_text = self.fonts["heading_md"].render(option["icon"], True, self.colors["text_primary"])
            self.screen.blit(icon_text, (card_rect.x + 20, card_rect.y + 15))
            
            title_text = self.fonts["body_lg"].render(option["title"], True, self.colors["text_primary"])
            self.screen.blit(title_text, (card_rect.x + 70, card_rect.y + 15))
            
            subtitle_text = self.fonts["body_sm"].render(option["subtitle"], True, self.colors["text_secondary"])
            self.screen.blit(subtitle_text, (card_rect.x + 70, card_rect.y + 40))
        
        # Footer con controles
        footer_y = self.screen.get_height() - 50
        controls = "↑↓ Navigate • Enter Select • Esc Exit"
        controls_text = self.fonts["caption"].render(controls, True, self.colors["text_secondary"])
        controls_x = (self.screen.get_width() - controls_text.get_width()) // 2
        self.screen.blit(controls_text, (controls_x, footer_y))
    
    def draw_system_info(self):
        """Dibujar información del sistema"""
        self.screen.fill(self.colors["bg_primary"])
        
        # Header
        header_rect = pygame.Rect(0, 0, self.screen.get_width(), 70)
        pygame.draw.rect(self.screen, self.colors["bg_secondary"], header_rect)
        
        title = self.fonts["heading_lg"].render("System Information", True, self.colors["text_primary"])
        self.screen.blit(title, (30, 20))
        
        # Información del sistema
        info_y = 100
        info_items = [
            ("Gaming OS Version", "2.1"),
            ("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            ("Pygame Version", pygame.version.ver),
            ("Display Resolution", f"{self.screen.get_width()}x{self.screen.get_height()}"),
            ("Fullscreen Mode", "Yes" if self.config.get('fullscreen') else "No"),
            ("Theme", self.config.get('theme', 'dark').title()),
            ("Sound Enabled", "Yes" if self.config.get('sound_enabled') else "No"),
            ("Master Volume", f"{self.config.get('master_volume', 80)}%"),
            ("Music Volume", f"{self.config.get('music_volume', 60)}%"),
            ("Background Music", "Playing" if self.main_music_playing else "Stopped"),
            ("Performance Mode", self.config.get('performance_mode', 'balanced').title()),
            ("Games Directory", self.config.get('games_directory', './games/')),
            ("Auto Scan Games", "Yes" if self.config.get('auto_scan_games') else "No")
        ]
        
        # Dividir en dos columnas
        col1_items = info_items[:len(info_items)//2 + 1]
        col2_items = info_items[len(info_items)//2 + 1:]
        
        # Columna 1
        for i, (label, value) in enumerate(col1_items):
            label_text = self.fonts["body_sm"].render(f"{label}:", True, self.colors["text_secondary"])
            value_text = self.fonts["body_sm"].render(value, True, self.colors["text_primary"])
            
            self.screen.blit(label_text, (50, info_y + i * 30))
            self.screen.blit(value_text, (250, info_y + i * 30))
        
        # Columna 2
        col2_x = self.screen.get_width() // 2 + 50
        for i, (label, value) in enumerate(col2_items):
            label_text = self.fonts["body_sm"].render(f"{label}:", True, self.colors["text_secondary"])
            value_text = self.fonts["body_sm"].render(value, True, self.colors["text_primary"])
            
            self.screen.blit(label_text, (col2_x, info_y + i * 30))
            self.screen.blit(value_text, (col2_x + 200, info_y + i * 30))
        
        # Footer
        footer_y = self.screen.get_height() - 50
        footer_text = "Press ESC to go back"
        footer_render = self.fonts["caption"].render(footer_text, True, self.colors["text_secondary"])
        footer_x = (self.screen.get_width() - footer_render.get_width()) // 2
        self.screen.blit(footer_render, (footer_x, footer_y))
    
    def update_boot_sequence(self):
        """Actualiza secuencia de arranque"""
        if not self.config.get("boot_animation", True):
            self.boot_progress = 100
            self.current_state = "main_menu"
            return
        
        elapsed = time.time() - self.boot_start_time
        self.boot_progress = min(100, (elapsed / 3.5) * 100)  # Aumentado tiempo para mostrar audio
        
        # Cambiar mensajes
        message_threshold = (self.boot_message_index + 1) * (100 / len(self.boot_messages))
        if self.boot_progress >= message_threshold and self.boot_message_index < len(self.boot_messages) - 1:
            self.boot_message_index += 1
            self.play_ui_sound("hover")
        
        # Completar boot
        if self.boot_progress >= 100:
            self.current_state = "main_menu"
            self.play_ui_sound("success")
            # Iniciar música principal cuando termine el boot
            if self.should_play_main_music():
                self.play_main_music()
    
    def launch_game(self, game_path):
        """Lanza un juego y detiene la música"""
        try:
            import subprocess
            print(f"🚀 Launching: {game_path}")
            
            # Detener música antes de lanzar el juego
            self.stop_main_music()
            
            # Efecto visual de lanzamiento
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill(self.colors["overlay"])
            self.screen.blit(overlay, (0, 0))
            
            launching_text = self.fonts["heading_md"].render("Launching game...", True, self.colors["text_primary"])
            text_x = (self.screen.get_width() - launching_text.get_width()) // 2
            text_y = (self.screen.get_height() - launching_text.get_height()) // 2
            self.screen.blit(launching_text, (text_x, text_y))
            pygame.display.flip()
            
            time.sleep(0.5)
            
            result = subprocess.run([sys.executable, game_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Game '{game_path}' executed successfully.")
                self.play_ui_sound("success")
            else:
                print(f"❌ Game error (code {result.returncode}):")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                self.play_ui_sound("error")
            
            # Reiniciar música cuando vuelva del juego
            if self.should_play_main_music():
                self.play_main_music()
            
            return True
        except Exception as e:
            print(f"❌ Failed to launch game '{game_path}': {e}")
            self.play_ui_sound("error")
            # Reiniciar música en caso de error también
            if self.should_play_main_music():
                self.play_main_music()
            return False
    
    def handle_events(self):
        """Maneja eventos del sistema"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "main_menu":
                        return False
                    elif self.current_state in ["game_launcher", "settings", "system_info"]:
                        self.current_state = "main_menu"
                        self.selected_option = 0
                        self.play_ui_sound("click")
                        # Asegurar que la música esté sonando al volver al menú
                        if self.should_play_main_music():
                            self.play_main_music()
                
                elif self.current_state == "main_menu":
                    if self.game_launcher and self.settings_manager:
                        max_options = 4
                    elif self.game_launcher:
                        max_options = 3
                    else:
                        max_options = 5
                    
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % max_options
                        self.play_ui_sound("hover")
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % max_options
                        self.play_ui_sound("hover")
                    elif event.key == pygame.K_RETURN:
                        self.play_ui_sound("click")
                        
                        if self.game_launcher and self.settings_manager:
                            if self.selected_option == 0:  # Game Library
                                self.current_state = "game_launcher"
                                self.selected_option = 0
                            elif self.selected_option == 1:  # Settings
                                self.current_state = "settings"
                            elif self.selected_option == 2:  # System Info
                                self.current_state = "system_info"
                            elif self.selected_option == 3:  # Exit
                                return False
                        elif self.game_launcher:
                            if self.selected_option == 0:  # Game Library
                                self.current_state = "game_launcher"
                                self.selected_option = 0
                            elif self.selected_option == 1:  # Settings (Limited)
                                print("⚙️ Settings limitado - Instale ui.settings_manager para funcionalidad completa")
                            elif self.selected_option == 2:  # Exit
                                return False
                        else:
                            # Modo simple sin launcher
                            if self.selected_option == 0:  # Snake
                                game = next((g for g in self.games if "snake" in g["filename"]), None)
                                if game: self.launch_game(game["path"])
                            elif self.selected_option == 1:  # Tetris
                                game = next((g for g in self.games if "tetris" in g["filename"]), None)
                                if game: self.launch_game(game["path"])
                            elif self.selected_option == 2:  # Pong
                                game = next((g for g in self.games if "pong" in g["filename"]), None)
                                if game: self.launch_game(game["path"])
                            elif self.selected_option == 3:  # Breakout
                                game = next((g for g in self.games if "breakout" in g["filename"]), None)
                                if game: self.launch_game(game["path"])
                            elif self.selected_option == 4:  # Exit
                                return False
                
                elif self.current_state == "game_launcher" and self.game_launcher:
                    result = self.game_launcher.handle_input(event)
                    if result == "back":
                        self.current_state = "main_menu"
                        self.selected_option = 0
                        self.play_ui_sound("click")
                        # Asegurar música al volver del game launcher
                        if self.should_play_main_music():
                            self.play_main_music()
                    elif result == "beep":
                        self.play_ui_sound("hover")
                    elif result == "error":
                        self.play_ui_sound("error")
                    elif isinstance(result, tuple) and result[0] == "launch_game":
                        # Se lanzó un juego desde el launcher
                        pass  # La música ya se detuvo en launch_game
                
                elif self.current_state == "settings" and self.settings_manager:
                    result = self.settings_manager.handle_input(event)
                    if result == "back":
                        self.current_state = "main_menu"
                        self.selected_option = 1  # Volver a Settings
                        self.play_ui_sound("click")
                        # Asegurar música al volver de settings
                        if self.should_play_main_music():
                            self.play_main_music()
                    elif result in ["navigate", "toggle", "select"]:
                        self.play_ui_sound("hover")
                    elif result == "save":
                        self.play_ui_sound("success")
                    elif result == "error":
                        self.play_ui_sound("error")
        
        return True
    
    def update_music_state(self):
        """Actualizar estado de la música según la pantalla actual"""
        should_play = self.should_play_main_music()
        
        if should_play and not self.main_music_playing:
            self.play_main_music()
        elif not should_play and self.main_music_playing:
            self.stop_main_music()
    
    def run(self):
        """Loop principal del sistema"""
        running = True
        
        print("🎮 Starting Gaming Modern OS v2.1...")
        print(f"🎯 Game launcher: {'Advanced' if self.game_launcher else 'Simple'}")
        print(f"⚙️ Settings: {'Advanced' if self.settings_manager else 'Limited'}")
        print(f"🎵 Background music: {'Ready' if self.music_initialized else 'Disabled'}")
        
        while running:
            # Eventos
            running = self.handle_events()
            
            # Lógica
            if self.current_state == "boot":
                self.update_boot_sequence()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.game_launcher.update()
            elif self.current_state == "settings" and self.settings_manager:
                self.settings_manager.update()
            
            # Actualizar estado de música
            self.update_music_state()
            
            # Render
            if self.current_state == "boot":
                self.draw_boot_screen()
            elif self.current_state == "main_menu":
                self.draw_main_interface()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.screen.fill(self.colors["bg_primary"])
                self.game_launcher.draw()
            elif self.current_state == "settings" and self.settings_manager:
                self.settings_manager.draw()
            elif self.current_state == "system_info":
                self.draw_system_info()
            
            # Update
            self.animation_time += 1
            
            # Aplicar límite de FPS
            fps_limit = self.config.get("fps_limit", 60)
            if fps_limit > 0:
                self.clock.tick(fps_limit)
            else:
                self.clock.tick()  # Sin límite
            
            pygame.display.flip()
        
        # Detener música al salir
        self.stop_main_music()
        
        # Guardar configuración al salir
        self.save_config()
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    print("🎮 Initializing Gaming Modern OS v2.1...")
    
    # Crear estructura de directorios
    os.makedirs("games/builtin", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("core", exist_ok=True)
    os.makedirs("assets/sounds/main", exist_ok=True)  # Crear directorio de audio
    
    # Archivos __init__.py
    for module_dir in ["ui", "core"]:
        init_file = Path(module_dir) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Gaming Modern OS Module\n")
    
    # Verificar dependencias
    missing_modules = []
    
    # Verificar settings_manager
    settings_path = Path("ui/settings_manager.py")
    if not settings_path.exists():
        missing_modules.append("ui/settings_manager.py")
        print("⚠️ settings_manager.py no encontrado - creando archivo básico...")
        
        # Crear archivo settings_manager básico si no existe
        with open(settings_path, 'w') as f:
            f.write('"""Settings Manager placeholder"""\nclass SettingsManager:\n    def __init__(self, *args, **kwargs):\n        pass\n    def handle_input(self, event):\n        return None\n    def update(self):\n        pass\n    def draw(self):\n        pass\n')
    
    # Verificar archivo de música
    music_path = Path("assets/sounds/main/main.mp3")
    if not music_path.exists():
        print("🎵 Para habilitar música de fondo:")
        print(f"   Coloca tu archivo MP3 en: {music_path}")
        print("   El archivo debe llamarse 'main.mp3'")
    
    if missing_modules:
        print(f"📋 Módulos faltantes detectados: {', '.join(missing_modules)}")
        print("💡 Se crearán archivos básicos automáticamente")
    
    # Iniciar sistema
    try:
        gaming_os = GamingModernOS()
        gaming_os.run()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()