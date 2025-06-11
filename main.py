#!/usr/bin/env python3
"""
Gaming Modern OS - Boot Loader Principal
Sistema operativo moderno para juegos con diseño limpio y minimalista
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

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

class GamingModernOS:
    """
    Clase principal para el Gaming Modern OS.
    Sistema operativo gaming con diseño moderno y minimalista.
    """
    def __init__(self):
        # Configuración del sistema
        self.config = {
            "theme": "dark",
            "resolution": [1100, 700],  # Aumentado de 900 a 1100 para más anchura
            "fullscreen": False,
            "sound_enabled": True,
            "boot_animation": True,
            "games_directory": "./games/",
            "last_played": []
        }
        
        self.load_config()
        
        # Configurar pantalla
        self.screen = pygame.display.set_mode(self.config["resolution"])
        pygame.display.set_caption("Gaming Modern OS v2.0")
        
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
            "Preparing interface...",
            "System ready!"
        ]
        self.boot_message_index = 0
        self.boot_start_time = time.time()
        
        # Control del juego
        self.clock = pygame.time.Clock()
        self.selected_option = 0
        self.animation_time = 0
        
        # Inicializar lanzador
        self.game_launcher = None
        if GameLauncher:
            self.game_launcher = GameLauncher(self.screen, self.colors, self.fonts)
        else:
            self.games = self.scan_games_simple()
    
    def load_config(self):
        """Carga configuración del sistema"""
        config_path = Path("config/settings.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self):
        """Guarda configuración del sistema"""
        config_path = Path("config")
        config_path.mkdir(exist_ok=True)
        
        try:
            with open(config_path / "settings.json", 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
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
        if not self.config["sound_enabled"]:
            return
        
        try:
            frequencies = {
                "click": 1200,
                "hover": 800,
                "success": 1600,
                "error": 400
            }
            
            frequency = frequencies.get(sound_type, 800)
            duration = 60
            
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            
            for i in range(frames):
                t = float(i) / sample_rate
                # Envelope suave para sonido moderno
                envelope = math.exp(-t * 8)
                wave = math.sin(2 * math.pi * frequency * t) * envelope * 0.1
                arr.append([int(32767 * wave)] * 2)
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except:
            pass
    
    def draw_modern_card(self, surface, rect, elevation=1):
        """Dibuja una card moderna con sombra"""
        # Sombra
        shadow_offset = elevation * 2
        shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, 
                                 rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.colors["shadow"], 
                        (0, 0, rect.width, rect.height), border_radius=12)
        surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Card principal
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
        
        # Hora en header (derecha)
        current_time = time.strftime("%H:%M")
        time_text = self.fonts["body_md"].render(current_time, True, self.colors["text_secondary"])
        time_x = self.screen.get_width() - time_text.get_width() - 30
        self.screen.blit(time_text, (time_x, 30))
        
        # Opciones principales como cards modernas
        if self.game_launcher:
            options = [
                {"title": "Game Library", "subtitle": "Browse and play games", "icon": "🎮"},
                {"title": "Settings", "subtitle": "System preferences", "icon": "⚙️"},
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
                # Pulso suave para selección
                pulse = 0.95 + 0.05 * math.sin(self.animation_time * 0.1)
                card_color = tuple(int(c * pulse) for c in self.colors["bg_surface"])
            else:
                card_color = self.colors["bg_secondary"]
            
            # Dibujar card
            self.draw_modern_card(self.screen, card_rect, elevation=2 if is_selected else 1)
            if is_selected:
                pygame.draw.rect(self.screen, card_color, card_rect, border_radius=12)
                # Borde de acento
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
    
    def update_boot_sequence(self):
        """Actualiza secuencia de arranque"""
        elapsed = time.time() - self.boot_start_time
        self.boot_progress = min(100, (elapsed / 2.5) * 100)
        
        # Cambiar mensajes
        message_threshold = (self.boot_message_index + 1) * (100 / len(self.boot_messages))
        if self.boot_progress >= message_threshold and self.boot_message_index < len(self.boot_messages) - 1:
            self.boot_message_index += 1
            self.play_ui_sound("hover")
        
        # Completar boot
        if self.boot_progress >= 100:
            self.current_state = "main_menu"
            self.play_ui_sound("success")
    
    def launch_game(self, game_path):
        """Lanza un juego"""
        try:
            import subprocess
            print(f"Launching: {game_path}")
            
            # Efecto visual de lanzamiento
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill(self.colors["overlay"])
            self.screen.blit(overlay, (0, 0))
            
            launching_text = self.fonts["heading_md"].render("Launching game...", True, self.colors["text_primary"])
            text_x = (self.screen.get_width() - launching_text.get_width()) // 2
            text_y = (self.screen.get_height() - launching_text.get_height()) // 2
            self.screen.blit(launching_text, (text_x, text_y))
            pygame.display.flip()
            
            time.sleep(0.5)  # Pausa dramática
            
            result = subprocess.run([sys.executable, game_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Game '{game_path}' executed successfully.")
            else:
                print(f"Game error (code {result.returncode}):")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            
            return True
        except Exception as e:
            print(f"Failed to launch game '{game_path}': {e}")
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
                    elif self.current_state == "game_launcher":
                        self.current_state = "main_menu"
                        self.selected_option = 0
                        self.play_ui_sound("click")
                
                elif self.current_state == "main_menu":
                    max_options = 3 if self.game_launcher else 5
                    
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % max_options
                        self.play_ui_sound("hover")
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % max_options
                        self.play_ui_sound("hover")
                    elif event.key == pygame.K_RETURN:
                        self.play_ui_sound("click")
                        
                        if self.game_launcher:
                            if self.selected_option == 0:  # Game Library
                                self.current_state = "game_launcher"
                                self.selected_option = 0
                            elif self.selected_option == 1:  # Settings
                                print("Settings not implemented yet")
                            elif self.selected_option == 2:  # Exit
                                return False
                        else:
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
                    elif result == "beep":
                        self.play_ui_sound("hover")
                    elif result == "error":
                        self.play_ui_sound("error")
        
        return True
    
    def run(self):
        """Loop principal del sistema"""
        running = True
        
        print("🎮 Starting Gaming Modern OS...")
        print(f"🎯 Game launcher: {'Advanced' if self.game_launcher else 'Simple'}")
        
        while running:
            # Eventos
            running = self.handle_events()
            
            # Lógica
            if self.current_state == "boot":
                self.update_boot_sequence()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.game_launcher.update()
            
            # Render
            if self.current_state == "boot":
                self.draw_boot_screen()
            elif self.current_state == "main_menu":
                self.draw_main_interface()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.screen.fill(self.colors["bg_primary"])
                self.game_launcher.draw()
            
            # Update
            self.animation_time += 1
            pygame.display.flip()
            self.clock.tick(60)
        
        self.save_config()
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    print("🎮 Initializing Gaming Modern OS...")
    
    # Crear estructura de directorios
    os.makedirs("games/builtin", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("core", exist_ok=True)
    
    # Archivos __init__.py
    for module_dir in ["ui", "core"]:
        init_file = Path(module_dir) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Gaming Modern OS Module\n")
    
    # Iniciar sistema
    gaming_os = GamingModernOS()
    gaming_os.run()

if __name__ == "__main__":
    main()