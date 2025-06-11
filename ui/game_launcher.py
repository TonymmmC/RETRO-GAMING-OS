#!/usr/bin/env python3
"""
Gaming Modern OS - Boot Loader Principal
Sistema operativo moderno para juegos que arranca directo a una interfaz pulcra y eficiente.
"""

import pygame
import sys
import os
import time
import json
from pathlib import Path

# Importar módulos del sistema
try:
    # Intenta importar el lanzador de juegos avanzado
    from ui.game_launcher import GameLauncher
except ImportError:
    # Fallback si no existe el módulo GameLauncher
    GameLauncher = None
    print("⚠️ Advertencia: ui.game_launcher no encontrado. Usando lanzador simple.")

# Inicializar Pygame y sus módulos
pygame.init()
pygame.mixer.init()

class GamingModernOS:
    """
    Clase principal para el sistema operativo Gaming Modern OS.
    Gestiona la inicialización, la lógica del sistema, la interfaz de usuario
    y los efectos visuales.
    """
    def __init__(self):
        # Configuración por defecto del sistema
        self.config = {
            "theme": "modern_blue",         # Tema de color predeterminado (azul moderno)
            "resolution": [800, 600],       # Resolución de la ventana
            "fullscreen": False,            # Modo pantalla completa
            "sound_enabled": True,          # Sonido habilitado
            "boot_animation": True,         # Animación de arranque
            "scan_lines": False,            # Efecto de líneas de escaneo CRT (desactivado por defecto para tema moderno)
            "games_directory": "./games/",  # Directorio base para los juegos
            "last_played": []               # Historial de juegos recientes
        }
        
        # Cargar configuración desde el archivo si existe, sobrescribiendo los valores por defecto
        self.load_config()
        
        # Configurar la pantalla principal de Pygame
        self.screen = pygame.display.set_mode(self.config["resolution"])
        pygame.display.set_caption("Gaming Modern OS v1.0") # Título de la ventana moderno
        
        # Definición de colores para el tema moderno
        self.colors = {
            "primary_accent": (60, 160, 255),    # Azul vibrante principal
            "secondary_accent": (30, 90, 150),   # Azul secundario más oscuro
            "background_dark": (20, 20, 25),     # Fondo oscuro casi negro
            "background_light": (240, 240, 245), # Gris muy claro para elementos de UI
            "text_primary": (255, 255, 255),     # Blanco puro para texto principal
            "text_secondary": (180, 180, 190),   # Gris claro para texto secundario
            "highlight": (255, 210, 70),         # Amarillo dorado para resaltado
            "error": (255, 70, 70)               # Rojo para mensajes de error
        }
        
        # Definición de fuentes con diferentes tamaños
        self.fonts = {
            "title": pygame.font.Font(None, 48),   # Fuente grande para títulos
            "large": pygame.font.Font(None, 36),   # Fuente grande para títulos de sección
            "medium": pygame.font.Font(None, 28),  # Fuente mediana para opciones de menú
            "small": pygame.font.Font(None, 20)    # Fuente pequeña para información detallada
        }
        
        # Referencias a las fuentes para un uso más directo
        self.font_title = self.fonts["title"]
        self.font_large = self.fonts["large"]
        self.font_medium = self.fonts["medium"]
        self.font_small = self.fonts["small"]
        
        # Estados internos del sistema
        self.current_state = "boot"             # Estado inicial: arranque
        self.boot_progress = 0                  # Progreso de la animación de arranque (0-100)
        self.boot_messages = [                  # Mensajes mostrados durante el arranque
            "INICIANDO SISTEMA...",
            "CARGANDO MÓDULOS DE JUEGO...",
            "VERIFICANDO INTEGRIDAD...",
            "PREPARANDO INTERFAZ DE USUARIO...",
            "SISTEMA OPERATIVO LISTO!"
        ]
        self.boot_message_index = 0             # Índice del mensaje de arranque actual
        self.boot_start_time = time.time()      # Tiempo de inicio de la secuencia de arranque
        
        # Clock para controlar los FPS del juego
        self.clock = pygame.time.Clock()
        
        # Variables para animaciones visuales
        self.selection_blink = 0                # Contador para el efecto de parpadeo de selección
        
        # Inicialización del lanzador de juegos (avanzado o simple)
        self.game_launcher = None
        self.selected_option = 0                # Opción actualmente seleccionada en el menú
        
        if GameLauncher:
            # Si GameLauncher está disponible, inicializa la versión avanzada
            self.game_launcher = GameLauncher(self.screen, self.colors, self.fonts)
        else:
            # Si no, usa el lanzador simple y escanea solo los juegos permitidos
            self.games = self.scan_games_simple()
        
    def load_config(self):
        """Carga la configuración del sistema desde un archivo JSON."""
        config_path = Path("config/settings.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error cargando configuración: {e}")
    
    def save_config(self):
        """Guarda la configuración actual del sistema en un archivo JSON."""
        config_path = Path("config")
        config_path.mkdir(exist_ok=True) # Asegura que el directorio 'config' existe
        
        try:
            with open(config_path / "settings.json", 'w') as f:
                json.dump(self.config, f, indent=2) # Guarda con formato legible
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def scan_games_simple(self):
        """
        Escanenado de juegos para el lanzador simple.
        Solo incluye los juegos 'snake', 'tetris', 'pong' y 'breakout'.
        """
        allowed_games = ["snake", "tetris", "pong", "breakout"]
        games_found = []
        builtin_dir = Path("games/builtin") # Directorio donde se esperan los juegos
        
        if builtin_dir.exists():
            for game_name in allowed_games:
                file_path = builtin_dir / f"{game_name}.py"
                if file_path.exists():
                    # Align titles with the new modern names for consistency
                    title_map = {
                        "snake": "SNAKE GAME",
                        "tetris": "TETRIS MODERN",
                        "pong": "PONG GAME",
                        "breakout": "BREAKOUT GAME"
                    }
                    games_found.append({
                        "title": title_map.get(game_name, game_name.upper().replace("_", " ")),
                        "filename": file_path.name,
                        "path": str(file_path)
                    })
        return games_found
    
    def play_click_sound(self, frequency=1500, duration=50):
        """
        Reproduce un sonido de "click" moderno.
        Controlado por la configuración de sonido.
        """
        if not self.config["sound_enabled"]:
            return
        
        try:
            sample_rate = 22050 # Frecuencia de muestreo
            frames = int(duration * sample_rate / 1000) # Número de frames para la duración
            arr = []
            # Genera una onda senoidal para un sonido de click suave
            for i in range(frames):
                t = float(i) / sample_rate
                amplitude = 0.1 * math.exp(-t * 8) # Suave decaimiento
                wave = math.sin(2 * math.pi * frequency * t) * amplitude
                arr.append([int(32767 * wave)] * 2) # Estéreo
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except Exception as e:
            # Captura cualquier error en la reproducción del sonido
            print(f"Error al reproducir sonido: {e}")
            pass
    
    def draw_rounded_rect(self, surface, color, rect, radius=10, width=0):
        """Dibuja un rectángulo con bordes redondeados."""
        pygame.draw.rect(surface, color, rect, border_radius=radius, width=width)

    def draw_shadow_rect(self, surface, rect, radius=10, shadow_offset=5, shadow_color=(0, 0, 0, 80)):
        """Dibuja un rectángulo con una sombra suave."""
        shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self.draw_rounded_rect(shadow_surface, shadow_color, (0, 0, rect.width, rect.height), radius)
        surface.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

    def draw_boot_screen(self):
        """Dibuja la pantalla de arranque del sistema operativo con un diseño moderno."""
        self.screen.fill(self.colors["background_dark"]) # Fondo oscuro
        
        # Título principal del OS
        title_text = self.font_title.render("GAMING MODERN OS", True, self.colors["primary_accent"])
        title_x = (self.screen.get_width() - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, 150))
        
        # Mensaje de arranque actual
        if self.boot_message_index < len(self.boot_messages):
            message = self.boot_messages[self.boot_message_index]
            message_render = self.font_medium.render(message, True, self.colors["text_secondary"])
            message_x = (self.screen.get_width() - message_render.get_width()) // 2
            self.screen.blit(message_render, (message_x, 300))
        
        # Barra de progreso moderna
        progress_width = 400
        progress_height = 25
        progress_x = (self.screen.get_width() - progress_width) // 2
        progress_y = 350
        
        # Fondo de la barra de progreso con sombra
        progress_bg_rect = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
        self.draw_shadow_rect(self.screen, progress_bg_rect, radius=8, shadow_offset=3)
        self.draw_rounded_rect(self.screen, self.colors["secondary_accent"], progress_bg_rect, 8)
        
        # Progreso actual
        fill_width = int((self.boot_progress / 100) * progress_width)
        progress_fill_rect = pygame.Rect(progress_x, progress_y, fill_width, progress_height)
        self.draw_rounded_rect(self.screen, self.colors["primary_accent"], progress_fill_rect, 8)
        
        # Porcentaje
        percent_text = f"{int(self.boot_progress)}%"
        percent_render = self.font_medium.render(percent_text, True, self.colors["text_primary"])
        percent_x = (self.screen.get_width() - percent_render.get_width()) // 2
        self.screen.blit(percent_render, (percent_x, progress_y + progress_height + 15))
    
    def draw_main_interface(self):
        """Dibuja la interfaz principal del sistema (menú principal)."""
        self.screen.fill(self.colors["background_dark"]) # Fondo oscuro
        
        # Título del menú principal
        title_text = self.font_large.render("MENÚ PRINCIPAL", True, self.colors["text_primary"])
        title_x = (self.screen.get_width() - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, 50))
        
        # Opciones del menú
        # Define las opciones del menú para el lanzador avanzado
        menu_options_advanced = [
            "1. LANZADOR DE JUEGOS",
            "2. CONFIGURACIÓN",
            "3. APAGAR SISTEMA"
        ]
        # Define las opciones del menú para el lanzador simple (si GameLauncher no está disponible)
        menu_options_simple = [
            "1. JUEGO DE SNAKE", 
            "2. JUEGO DE TETRIS", 
            "3. JUEGO DE PONG",
            "4. JUEGO DE BREAKOUT",
            "5. SALIR"
        ]

        current_menu_options = menu_options_advanced if self.game_launcher else menu_options_simple
        max_options = len(current_menu_options)
        
        start_y = 150
        for i, option_text in enumerate(current_menu_options):
            is_selected = (i == self.selected_option)
            
            # Resalta la opción seleccionada con un color de acento y posible animación de pulso
            if is_selected:
                # Animación de pulso para la selección
                pulse_factor = (pygame.time.get_ticks() % 1000) / 1000.0
                pulse_intensity = 0.5 * (1 + math.sin(pulse_factor * 2 * math.pi * 2)) 
                
                current_color = (
                    int(self.colors["highlight"][0] * (0.7 + 0.3 * pulse_intensity)),
                    int(self.colors["highlight"][1] * (0.7 + 0.3 * pulse_intensity)),
                    int(self.colors["highlight"][2] * (0.7 + 0.3 * pulse_intensity))
                )
            else:
                current_color = self.colors["text_secondary"]
            
            # Dibuja la opción del menú
            option_render = self.font_medium.render(option_text, True, current_color)
            self.screen.blit(option_render, (100, start_y + i * 50))
        
        # Información adicional del sistema
        info_lines = [
            f"HORA DEL SISTEMA: {time.strftime('%H:%M:%S')}",
            f"JUEGOS ENCONTRADOS: {len(self.game_launcher.games) if hasattr(self.game_launcher, 'games') and self.game_launcher.games else len(self.games)}",
            f"ÚLTIMO JUGADO: NINGUNO",
            "",
            "CONTROLES:",
            "FLECHAS ARRIBA/ABAJO: Navegar • ENTER: Seleccionar • ESC: Salir"
        ]
        
        info_y = self.screen.get_height() - 180
        for i, line in enumerate(info_lines):
            color_to_use = self.colors["primary_accent"] if line.startswith("CONTROLES") else self.colors["text_secondary"]
            info_render = self.font_small.render(line, True, color_to_use)
            self.screen.blit(info_render, (100, info_y + i * 25))
    
    def draw_simple_game_launcher(self):
        """
        Dibuja la interfaz del lanzador simple de juegos,
        mostrando solo los juegos permitidos.
        """
        self.screen.fill(self.colors["background_dark"]) # Fondo oscuro
        
        # Título del lanzador simple
        title = "LANZADOR DE JUEGOS"
        text = self.font_large.render(title, True, self.colors["primary_accent"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 50))
        
        if not self.games:
            # Mensaje si no se encuentran juegos permitidos
            text = self.font_medium.render("NO SE ENCONTRARON JUEGOS", True, self.colors["text_secondary"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 200))
            
            text = self.font_small.render("Asegúrate de que los archivos .py estén en games/builtin/", True, self.colors["text_secondary"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 230))
        else:
            # Lista los juegos permitidos encontrados
            start_y = 150
            max_display = len(self.games) # Muestra todos los juegos encontrados de la lista permitida
            
            for i in range(max_display):
                game = self.games[i]
                is_selected = (i == self.selected_option)
                
                if is_selected:
                    pulse_factor = (pygame.time.get_ticks() % 1000) / 1000.0
                    pulse_intensity = 0.5 * (1 + math.sin(pulse_factor * 2 * math.pi * 2)) 
                    current_color = (
                        int(self.colors["highlight"][0] * (0.7 + 0.3 * pulse_intensity)),
                        int(self.colors["highlight"][1] * (0.7 + 0.3 * pulse_intensity)),
                        int(self.colors["highlight"][2] * (0.7 + 0.3 * pulse_intensity))
                    )
                else:
                    current_color = self.colors["text_primary"]
                
                prefix = "► " if is_selected else "  " # Indicador de selección
                game_text = f"{prefix}{game['title']}"
                
                text = self.font_medium.render(game_text, True, current_color)
                self.screen.blit(text, (100, start_y + i * 35))
        
        # Controles para el lanzador simple
        controls = "FLECHAS: Navegar • ENTER: Jugar • ESC: Volver"
        controls_render = self.font_small.render(controls, True, self.colors["primary_accent"])
        x = (self.screen.get_width() - controls_render.get_width()) // 2
        self.screen.blit(controls_render, (x, self.screen.get_height() - 50))
    
    def update_boot_sequence(self):
        """Actualiza el progreso de la animación de arranque."""
        elapsed = time.time() - self.boot_start_time
        
        # Calcula el progreso en base a un tiempo total (ej. 3 segundos para completar)
        self.boot_progress = min(100, (elapsed / 3.0) * 100)
        
        # Cambia el mensaje de arranque a intervalos de progreso
        message_threshold = (self.boot_message_index + 1) * (100 / len(self.boot_messages))
        if self.boot_progress >= message_threshold and self.boot_message_index < len(self.boot_messages) - 1:
            self.boot_message_index += 1
            self.play_click_sound(frequency=1000, duration=50) # Sonido al cambiar de mensaje
        
        # Transición al menú principal cuando el arranque está completo
        if self.boot_progress >= 100:
            self.current_state = "main_menu"
            self.play_click_sound(frequency=1800, duration=150) # Sonido de arranque completo
    
    def launch_game(self, game_path):
        """
        Lanza un juego externo utilizando un subproceso de Python.
        Permite que el juego se ejecute y luego el OS retome el control.
        """
        try:
            import subprocess
            # Usa sys.executable para garantizar que se usa el intérprete Python actual
            print(f"Lanzando juego: {game_path}")
            # Minimiza la ventana actual antes de lanzar el juego si no está en pantalla completa
            if not self.config["fullscreen"]:
                pygame.display.iconify() 

            result = subprocess.run([sys.executable, game_path], 
                                    capture_output=True, text=True)
            
            # Restaura la ventana después de que el juego termine
            if not self.config["fullscreen"]:
                pygame.display.set_mode(self.config["resolution"]) # Recrea la ventana

            # Manejo de la salida del subproceso (errores o mensajes)
            if result.returncode != 0:
                print(f"Error en el juego (código de retorno {result.returncode}):")
                print("--- SALIDA ESTÁNDAR (STDOUT) ---")
                print(result.stdout)
                print("--- ERRORES (STDERR) ---")
                print(result.stderr)
            else:
                print(f"Juego '{game_path}' ejecutado exitosamente.")
                print("--- SALIDA ESTÁNDAR (STDOUT) ---")
                print(result.stdout)
            
            return True
        except FileNotFoundError:
            print(f"Error: Intérprete de Python no encontrado o ruta del juego incorrecta: {game_path}")
            return False
        except Exception as e:
            print(f"Fallo al lanzar el juego '{game_path}': {e}")
            return False
    
    def handle_events(self):
        """Maneja todos los eventos de entrada del usuario (teclado, cierre de ventana)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Cierra la aplicación si el usuario cierra la ventana
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "main_menu":
                        return False # Sale del sistema desde el menú principal
                    elif self.current_state == "game_launcher" or self.current_state == "simple_launcher":
                        # Vuelve al menú principal desde los lanzadores
                        self.current_state = "main_menu"
                        self.selected_option = 0
                        self.play_click_sound()
                
                elif self.current_state == "main_menu":
                    # Determine the maximum number of options based on whether GameLauncher is available
                    max_options = 3 if self.game_launcher else 5
                    
                    # Handle number key selection
                    if event.key >= pygame.K_1 and event.key <= pygame.K_1 + max_options -1:
                        self.selected_option = event.key - pygame.K_1
                        
                        if self.game_launcher:
                            if self.selected_option == 0: # LANZADOR DE JUEGOS
                                self.current_state = "game_launcher"
                                self.selected_option = 0
                            elif self.selected_option == 1: # CONFIGURACIÓN
                                print("Abriendo Configuración (Aún no implementado)...")
                            elif self.selected_option == 2: # APAGAR SISTEMA
                                print("Apagando sistema...")
                                return False
                        else: # Simple launcher mode
                            if self.selected_option == 0: # SNAKE GAME
                                game_to_launch = next((game for game in self.games if game['title'] == "SNAKE GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 1: # TETRIS MODERN
                                game_to_launch = next((game for game in self.games if game['title'] == "TETRIS MODERN"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 2: # PONG GAME
                                game_to_launch = next((game for game in self.games if game['title'] == "PONG GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 3: # BREAKOUT GAME
                                game_to_launch = next((game for game in self.games if game['title'] == "BREAKOUT GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 4: # SALIR
                                print("Saliendo del sistema...")
                                return False
                        self.play_click_sound()
                        
                    # Universal arrow navigation for main menu (both modes)
                    elif event.key == pygame.K_UP:
                        self.selected_option = max(0, self.selected_option - 1)
                        self.play_click_sound(frequency=600, duration=50)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = min(max_options - 1, self.selected_option + 1)
                        self.play_click_sound(frequency=600, duration=50)
                    elif event.key == pygame.K_RETURN:
                        # Simulate number key press for selected option with ENTER
                        if self.game_launcher:
                            if self.selected_option == 0: # GAME LAUNCHER
                                self.current_state = "game_launcher"
                                self.selected_option = 0
                            elif self.selected_option == 1: # SETTINGS
                                print("Abriendo Configuración (Aún no implementado)...")
                            elif self.selected_option == 2: # SHUTDOWN
                                print("Apagando sistema...")
                                return False
                        else: # Simple mode
                            if self.selected_option == 0: # SNAKE GAME
                                game_to_launch = next((game for game in self.games if game['title'] == "SNAKE GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 1: # TETRIS MODERN
                                game_to_launch = next((game for game in self.games if game['title'] == "TETRIS MODERN"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 2: # PONG GAME
                                game_to_launch = next((game for game in self.games if game['title'] == "PONG GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 3: # BREAKOUT GAME
                                game_to_launch = next((game for game in self.games if game['title'] == "BREAKOUT GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 4: # EXIT
                                print("Saliendo del sistema...")
                                return False
                        self.play_click_sound()
                
                elif self.current_state == "game_launcher":
                    # Handle advanced launcher input
                    if self.game_launcher:
                        result = self.game_launcher.handle_input(event)
                        if result == "back": # If advanced launcher indicates "back"
                            self.current_state = "main_menu"
                            self.selected_option = 0
                            self.play_click_sound()
                        elif result == "beep": # If advanced launcher needs a sound
                            self.play_click_sound()
                        elif result == "error": # If advanced launcher reports an error
                            self.play_click_sound(frequency=400, duration=200)
                        elif isinstance(result, tuple) and result[0] == "launch_game":
                            game = result[1]
                            print(f"Intentando lanzar juego desde GameLauncher: {game['title']}")
                            # The actual launch logic should be within GameLauncher.handle_input
                            # or a dedicated function in GameLauncher to execute the game.
                            self.play_click_sound(frequency=800, duration=100)
                
                elif self.current_state == "simple_launcher":
                    # Handle simple launcher input
                    if event.key == pygame.K_UP:
                        if hasattr(self, 'games') and self.games:
                            self.selected_option = max(0, self.selected_option - 1)
                            self.play_click_sound(frequency=600, duration=50)
                    elif event.key == pygame.K_DOWN:
                        if hasattr(self, 'games') and self.games:
                            self.selected_option = min(len(self.games) - 1, self.selected_option + 1)
                            self.play_click_sound(frequency=600, duration=50)
                    elif event.key == pygame.K_RETURN:
                        if hasattr(self, 'games') and self.games and 0 <= self.selected_option < len(self.games):
                            game = self.games[self.selected_option]
                            print(f"Lanzando juego desde el lanzador simple: {game['title']}")
                            self.launch_game(game["path"])
                            self.play_click_sound()
        return True
    
    def run(self):
        """Bucle principal de ejecución del sistema operativo."""
        running = True
        
        print("🎮 Iniciando Gaming Modern OS...")
        print(f"🎯 Lanzador de juegos: {'Avanzado' if self.game_launcher else 'Simple'}")
        
        while running:
            # Procesar eventos de usuario
            running = self.handle_events()
            
            # Actualizar la lógica del sistema según el estado actual
            if self.current_state == "boot":
                self.update_boot_sequence()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.game_launcher.update() # Actualiza el estado interno del lanzador avanzado
            
            # Dibujar la pantalla correspondiente al estado actual
            if self.current_state == "boot":
                self.draw_boot_screen()
            elif self.current_state == "main_menu":
                self.draw_main_interface()
            elif self.current_state == "game_launcher" and self.game_launcher:
                self.screen.fill(self.colors["background_dark"]) # Limpia la pantalla para el lanzador
                self.game_launcher.draw() # Dibuja la interfaz del lanzador avanzado
            elif self.current_state == "simple_launcher":
                self.draw_simple_game_launcher() # Dibuja la interfaz del lanzador simple
            
            # Aplicar efectos visuales generales (scanlines ahora están desactivados por defecto)
            if self.config["scan_lines"]:
                # This part is intentionally left for user to enable scanlines if desired,
                # but by default it's off for a modern aesthetic.
                pass 
            
            # No hay borde CRT en el tema moderno
            
            # Actualizar contadores para animaciones
            self.selection_blink = (self.selection_blink + 1) % 60 # Controla el parpadeo de selección
            
            # Actualizar la pantalla completa
            pygame.display.flip()
            self.clock.tick(60) # Limita a 60 FPS
        
        # Guarda la configuración antes de salir
        self.save_config()
        pygame.quit() # Desinicializa Pygame
        sys.exit() # Sale de la aplicación

def main():
    """Función principal para inicializar y ejecutar el Gaming Modern OS."""
    print("🎮 Iniciando Gaming Modern OS...")
    
    # Crear directorios necesarios para la estructura del sistema
    os.makedirs("games/builtin", exist_ok=True)
    os.makedirs("games/roms", exist_ok=True)
    os.makedirs("games/emulators", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("assets/fonts", exist_ok=True)
    os.makedirs("assets/sounds", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("core", exist_ok=True)
    
    # Asegurar que los directorios de módulos tengan __init__.py
    for module_dir in ["ui", "core"]:
        init_file = Path(module_dir) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Gaming Modern OS Module\n")
    
    # Crea archivos dummy para los juegos permitidos si no existen.
    # Esto es útil para probar el menú y el lanzador sin necesidad de los juegos completos.
    dummy_games_content = {
        "snake.py": "# Dummy Snake Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Snake Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Snake Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':\n    run_game()\n",
        "tetris.py": "# Dummy Tetris Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Tetris Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Tetris Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':\n    run_game()\n",
        "pong.py": "# Dummy Pong Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Pong Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Pong Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':\n    run_game()\n",
        "breakout.py": "# Dummy Breakout Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Breakout Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Breakout Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':,run_game()\n"
    }

    builtin_games_dir = Path("games/builtin")
    for filename, content in dummy_games_content.items():
        file_path = builtin_games_dir / filename
        if not file_path.exists():
            file_path.write_text(content)
            print(f"Archivo de juego dummy creado: {file_path}")

    # Iniciar el sistema operativo moderno
    gaming_modern_os = GamingModernOS()
    gaming_modern_os.run()

if __name__ == "__main__":
    main()