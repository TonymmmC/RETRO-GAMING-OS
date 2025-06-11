#!/usr/bin/env python3
"""
Retro Gaming OS - Boot Loader Principal
Sistema operativo retro gaming que arranca directo a interfaz nostálgica
"""

import pygame
import sys
import os
import time
import json
from pathlib import Path

# Importar módulos del sistema
try:
    from ui.game_launcher import GameLauncher
except ImportError:
    # Fallback si no existe el módulo
    GameLauncher = None

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

class RetroGameOS:
    def __init__(self):
        # Configuración por defecto
        self.config = {
            "theme": "green_phosphor",
            "resolution": [800, 600],
            "fullscreen": False,
            "sound_enabled": True,
            "boot_animation": True,
            "scan_lines": True,
            "games_directory": "./games/",
            "last_played": []
        }
        
        # Cargar configuración si existe
        self.load_config()
        
        # Configurar pantalla
        self.screen = pygame.display.set_mode(self.config["resolution"])
        pygame.display.set_caption("Retro Gaming OS v1.0")
        
        # Colores tema retro
        self.colors = {
            "green_phosphor": (0, 255, 0),
            "black": (0, 0, 0),
            "dark_green": (0, 128, 0),
            "gray": (128, 128, 128),
            "white": (255, 255, 255),
            "amber": (255, 191, 0)
        }
        
        # Fuentes
        self.fonts = {
            "large": pygame.font.Font(None, 36),
            "medium": pygame.font.Font(None, 24),
            "small": pygame.font.Font(None, 16)
        }
        
        # Referencias antiguas para compatibilidad
        self.font_large = self.fonts["large"]
        self.font_medium = self.fonts["medium"]
        self.font_small = self.fonts["small"]
        
        # Estados del sistema
        self.current_state = "boot"
        self.boot_progress = 0
        self.boot_messages = [
            "INITIALIZING RETRO OS...",
            "LOADING GAME ENGINES...",
            "SCANNING ROM DIRECTORY...",
            "PREPARING LAUNCH INTERFACE...",
            "SYSTEM READY!"
        ]
        self.boot_message_index = 0
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
        # Variables de animación
        self.cursor_blink = 0
        self.scan_line_offset = 0
        
        # Inicializar Game Launcher
        self.game_launcher = None
        if GameLauncher:
            self.game_launcher = GameLauncher(self.screen, self.colors, self.fonts)
        
    def load_config(self):
        """Cargar configuración desde archivo JSON"""
        config_path = Path("config/settings.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self):
        """Guardar configuración actual"""
        config_path = Path("config")
        config_path.mkdir(exist_ok=True)
        
        try:
            with open(config_path / "settings.json", 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def play_beep(self, frequency=800, duration=100):
        """Reproducir sonido beep retro"""
        if not self.config["sound_enabled"]:
            return
        
        # Generar un tono simple
        sample_rate = 22050
        frames = int(duration * sample_rate / 1000)
        arr = []
        for i in range(frames):
            wave = 4096 * (frequency * 2 * 3.14159 * i / sample_rate) % (2 * 3.14159)
            arr.append([int(32767 * 0.1 * (wave - 3.14159) / 3.14159)] * 2)
        
        sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
        sound.play()
    
    def draw_scanlines(self):
        """Dibujar efecto de líneas de escaneo CRT"""
        if not self.config["scan_lines"]:
            return
            
        height = self.screen.get_height()
        width = self.screen.get_width()
        
        for y in range(0, height, 3):
            pygame.draw.line(self.screen, (0, 0, 0, 50), (0, y), (width, y))
    
    def draw_crt_border(self):
        """Dibujar borde estilo CRT"""
        width, height = self.screen.get_size()
        border_color = self.colors["dark_green"]
        
        # Bordes
        pygame.draw.rect(self.screen, border_color, (0, 0, width, 10))
        pygame.draw.rect(self.screen, border_color, (0, height-10, width, 10))
        pygame.draw.rect(self.screen, border_color, (0, 0, 10, height))
        pygame.draw.rect(self.screen, border_color, (width-10, 0, 10, height))
    
    def draw_boot_screen(self):
        """Dibujar pantalla de arranque"""
        self.screen.fill(self.colors["black"])
        
        # Logo ASCII
        logo_lines = [
            "██████╗ ███████╗████████╗██████╗  ██████╗     ██████╗ ███████╗",
            "██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗   ██╔═══██╗██╔════╝",
            "██████╔╝█████╗     ██║   ██████╔╝██║   ██║   ██║   ██║███████╗",
            "██╔══██╗██╔══╝     ██║   ██╔══██╗██║   ██║   ██║   ██║╚════██║",
            "██║  ██║███████╗   ██║   ██║  ██║╚██████╔╝   ╚██████╔╝███████║",
            "╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝     ╚═════╝ ╚══════╝"
        ]
        
        # Dibujar logo
        start_y = 150
        for i, line in enumerate(logo_lines):
            text = self.font_small.render(line, True, self.colors["green_phosphor"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, start_y + i * 20))
        
        # Mensaje de arranque
        if self.boot_message_index < len(self.boot_messages):
            message = self.boot_messages[self.boot_message_index]
            text = self.font_medium.render(message, True, self.colors["green_phosphor"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 350))
        
        # Barra de progreso
        progress_width = 400
        progress_height = 20
        progress_x = (self.screen.get_width() - progress_width) // 2
        progress_y = 400
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, self.colors["dark_green"], 
                        (progress_x, progress_y, progress_width, progress_height))
        
        # Progreso actual
        fill_width = int((self.boot_progress / 100) * progress_width)
        pygame.draw.rect(self.screen, self.colors["green_phosphor"], 
                        (progress_x, progress_y, fill_width, progress_height))
        
        # Porcentaje
        percent_text = f"{int(self.boot_progress)}%"
        text = self.font_medium.render(percent_text, True, self.colors["green_phosphor"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 430))
        
        # Cursor parpadeante
        if self.cursor_blink < 30:
            cursor_text = self.font_medium.render("_", True, self.colors["green_phosphor"])
            self.screen.blit(cursor_text, (x + text.get_width() + 10, 430))
    
    def draw_main_interface(self):
        """Dibujar interfaz principal del sistema"""
        self.screen.fill(self.colors["black"])
        
        # Título
        title = "RETRO GAMING OS - MAIN MENU"
        text = self.font_large.render(title, True, self.colors["green_phosphor"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 50))
        
        # Opciones del menú
        menu_options = [
            "1. GAME LAUNCHER",
            "2. FILE BROWSER", 
            "3. TERMINAL",
            "4. SETTINGS",
            "5. SHUTDOWN"
        ]
        
        start_y = 200
        for i, option in enumerate(menu_options):
            text = self.font_medium.render(option, True, self.colors["green_phosphor"])
            self.screen.blit(text, (100, start_y + i * 40))
        
        # Información del sistema
        info_lines = [
            f"SYSTEM TIME: {time.strftime('%H:%M:%S')}",
            f"GAMES FOUND: 0",  # TODO: Contar juegos reales
            f"LAST PLAYED: NONE",
            "",
            "PRESS NUMBER KEY TO SELECT OPTION",
            "ESC TO EXIT"
        ]
        
        info_y = 400
        for i, line in enumerate(info_lines):
            color = self.colors["amber"] if line.startswith("PRESS") or line.startswith("ESC") else self.colors["gray"]
            text = self.font_small.render(line, True, color)
            self.screen.blit(text, (100, info_y + i * 20))
    
    def update_boot_sequence(self):
        """Actualizar secuencia de arranque"""
        # Incrementar progreso
        self.boot_progress += 1.5
        
        # Cambiar mensaje cada 20% de progreso
        message_threshold = (self.boot_message_index + 1) * 20
        if self.boot_progress >= message_threshold and self.boot_message_index < len(self.boot_messages) - 1:
            self.boot_message_index += 1
            self.play_beep(frequency=1000, duration=50)
        
        # Completar boot
        if self.boot_progress >= 100:
            self.current_state = "main_menu"
            self.play_beep(frequency=1200, duration=200)
    
    def handle_events(self):
        """Manejar eventos de input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif self.current_state == "main_menu":
                    if event.key == pygame.K_1:
                        if self.game_launcher:
                            self.current_state = "game_launcher"
                            self.play_beep()
                        else:
                            print("Game Launcher not available")
                    elif event.key == pygame.K_2:
                        print("Opening File Browser...")
                        self.play_beep()
                    elif event.key == pygame.K_3:
                        print("Opening Terminal...")
                        self.play_beep()
                    elif event.key == pygame.K_4:
                        print("Opening Settings...")
                        self.play_beep()
                    elif event.key == pygame.K_5:
                        print("Shutting down...")
                        self.play_beep()
                        return False
                
                elif self.current_state == "game_launcher":
                    if self.game_launcher:
                        result = self.game_launcher.handle_input(event)
                        
                        if result == "back":
                            self.current_state = "main_menu"
                            self.play_beep()
                        elif result == "beep":
                            self.play_beep()
                        elif result == "error":
                            self.play_beep(400, 200)
                        elif isinstance(result, tuple) and result[0] == "launch_game":
                            game = result[1]
                            print(f"Launching game: {game['title']}")
                            
                            # Intentar lanzar el juego
                            if self.game_launcher.launch_game(game):
                                print(f"Game {game['title']} completed successfully")
                            else:
                                print(f"Failed to launch game: {game['title']}")
                            
                            self.play_beep(800, 100)
        
        return True
    
    def run(self):
        """Loop principal del sistema"""
        running = True
        
        while running:
            # Manejar eventos
            running = self.handle_events()
            
            # Actualizar estado
            if self.current_state == "boot":
                self.update_boot_sequence()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.game_launcher.update()
            
            # Dibujar pantalla según estado
            if self.current_state == "boot":
                self.draw_boot_screen()
            elif self.current_state == "main_menu":
                self.draw_main_interface()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.screen.fill(self.colors["black"])
                self.game_launcher.draw()
            
            # Efectos visuales
            if self.config["scan_lines"]:
                self.draw_scanlines()
            
            self.draw_crt_border()
            
            # Actualizar animaciones
            self.cursor_blink = (self.cursor_blink + 1) % 60
            self.scan_line_offset = (self.scan_line_offset + 1) % 3
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        # Guardar configuración al salir
        self.save_config()
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    print("🎮 Iniciando Retro Gaming OS...")
    
    # Crear directorios necesarios
    os.makedirs("games/builtin", exist_ok=True)
    os.makedirs("games/roms", exist_ok=True)
    os.makedirs("games/emulators", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("assets/fonts", exist_ok=True)
    os.makedirs("assets/sounds", exist_ok=True)
    
    # Iniciar sistema
    retro_os = RetroGameOS()
    retro_os.run()

if __name__ == "__main__":
    main()