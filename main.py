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
    # Intenta importar el lanzador de juegos avanzado
    from ui.game_launcher import GameLauncher
except ImportError:
    # Fallback si no existe el módulo GameLauncher
    GameLauncher = None
    print("⚠️ Advertencia: ui.game_launcher no encontrado. Usando lanzador simple.")

# Inicializar Pygame y sus módulos
pygame.init()
pygame.mixer.init()

class RetroGameOS:
    """
    Clase principal para el sistema operativo Retro Gaming.
    Gestiona la inicialización, la lógica del juego, la interfaz de usuario
    y los efectos visuales retro.
    """
    def __init__(self):
        # Configuración por defecto del sistema
        self.config = {
            "theme": "green_phosphor",      # Tema de color predeterminado
            "resolution": [800, 600],       # Resolución de la ventana
            "fullscreen": False,            # Modo pantalla completa
            "sound_enabled": True,          # Sonido habilitado
            "boot_animation": True,         # Animación de arranque
            "scan_lines": True,             # Efecto de líneas de escaneo CRT
            "games_directory": "./games/",  # Directorio base para los juegos
            "last_played": []               # Historial de juegos recientes
        }
        
        # Cargar configuración desde el archivo si existe, sobrescribiendo los valores por defecto
        self.load_config()
        
        # Configurar la pantalla principal de Pygame
        self.screen = pygame.display.set_mode(self.config["resolution"])
        pygame.display.set_caption("Retro Gaming OS v1.0") # Título de la ventana
        
        # Definición de colores para los temas retro
        self.colors = {
            "green_phosphor": (0, 255, 0),    # Verde brillante para texto principal
            "black": (0, 0, 0),               # Fondo negro
            "dark_green": (0, 128, 0),        # Verde oscuro para elementos de UI
            "gray": (128, 128, 128),          # Gris para texto secundario
            "white": (255, 255, 255),         # Blanco (uso limitado)
            "amber": (255, 191, 0)            # Ámbar para resaltado y cursores
        }
        
        # Definición de fuentes con diferentes tamaños
        self.fonts = {
            "large": pygame.font.Font(None, 36),   # Fuente grande para títulos
            "medium": pygame.font.Font(None, 24),  # Fuente mediana para opciones de menú
            "small": pygame.font.Font(None, 16)    # Fuente pequeña para información detallada
        }
        
        # Referencias antiguas a las fuentes para compatibilidad (opcional, pero mantenido)
        self.font_large = self.fonts["large"]
        self.font_medium = self.fonts["medium"]
        self.font_small = self.fonts["small"]
        
        # Estados internos del sistema
        self.current_state = "boot"             # Estado inicial: arranque
        self.boot_progress = 0                  # Progreso de la animación de arranque (0-100)
        self.boot_messages = [                  # Mensajes mostrados durante el arranque
            "INICIANDO RETRO OS...",
            "CARGANDO MOTORES DE JUEGO...",
            "ESCANENADO DIRECTORIO DE ROMS...",
            "PREPARANDO INTERFAZ DE INICIO...",
            "SISTEMA LISTO!"
        ]
        self.boot_message_index = 0             # Índice del mensaje de arranque actual
        self.boot_start_time = time.time()      # Tiempo de inicio de la secuencia de arranque
        
        # Clock para controlar los FPS del juego
        self.clock = pygame.time.Clock()
        
        # Variables para animaciones visuales
        self.cursor_blink = 0                   # Contador para el efecto de parpadeo del cursor
        self.scan_line_offset = 0               # Desplazamiento para el efecto de líneas de escaneo
        
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
                    games_found.append({
                        "title": game_name.upper().replace("_", " "), # Formato del título
                        "filename": file_path.name,
                        "path": str(file_path)
                    })
        return games_found
    
    def play_beep(self, frequency=800, duration=100):
        """
        Reproduce un sonido de "beep" retro.
        Controlado por la configuración de sonido.
        """
        if not self.config["sound_enabled"]:
            return
        
        try:
            sample_rate = 22050 # Frecuencia de muestreo
            frames = int(duration * sample_rate / 1000) # Número de frames para la duración
            arr = []
            # Genera una onda cuadrada para un sonido retro simple
            for i in range(frames):
                wave = 4096 * (frequency * 2 * 3.14159 * i / sample_rate) % (2 * 3.14159)
                arr.append([int(32767 * 0.1 * (wave - 3.14159) / 3.14159)] * 2)
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except:
            # Captura cualquier error en la reproducción del sonido
            pass
    
    def draw_scanlines(self):
        """Dibuja un efecto de líneas de escaneo tipo CRT en la pantalla."""
        if not self.config["scan_lines"]:
            return
            
        height = self.screen.get_height()
        width = self.screen.get_width()
        
        # Dibuja líneas negras semi-transparentes para simular un monitor CRT
        for y in range(0, height, 3): # Dibuja una línea cada 3 píxeles
            pygame.draw.line(self.screen, (0, 0, 0, 50), (0, y), (width, y))
    
    def draw_crt_border(self):
        """Dibuja un borde simple para simular un marco de monitor CRT."""
        width, height = self.screen.get_size()
        border_color = self.colors["dark_green"] # Color del borde
        
        # Dibuja los cuatro rectángulos que forman el borde
        pygame.draw.rect(self.screen, border_color, (0, 0, width, 10))
        pygame.draw.rect(self.screen, border_color, (0, height-10, width, 10))
        pygame.draw.rect(self.screen, border_color, (0, 0, 10, height))
        pygame.draw.rect(self.screen, border_color, (width-10, 0, 10, height))
    
    def draw_boot_screen(self):
        """Dibuja la pantalla de arranque del sistema operativo."""
        self.screen.fill(self.colors["black"]) # Fondo negro
        
        # Logo ASCII para un toque retro
        logo_lines = [
            "██████╗ ███████╗████████╗██████╗   ██████╗      ██████╗ ███████╗",
            "██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗    ██╔═══██╗██╔════╝",
            "██████╔╝█████╗    ██║   ██████╔╝██║   ██║    ██║   ██║███████╗",
            "██╔══██╗██╔══╝    ██║   ██╔══██╗██║   ██║    ██║   ██║╚════██║",
            "██║  ██║███████╗  ██║   ██║  ██║╚██████╔╝    ╚██████╔╝███████║",
            "╚═╝  ╚═╝╚══════╝  ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═════╝ ╚══════╝"
        ]
        
        # Dibuja cada línea del logo
        start_y = 150
        for i, line in enumerate(logo_lines):
            text = self.font_small.render(line, True, self.colors["green_phosphor"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, start_y + i * 20))
        
        # Muestra el mensaje de arranque actual
        if self.boot_message_index < len(self.boot_messages):
            message = self.boot_messages[self.boot_message_index]
            text = self.font_medium.render(message, True, self.colors["green_phosphor"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 350))
        
        # Dibuja la barra de progreso
        progress_width = 400
        progress_height = 20
        progress_x = (self.screen.get_width() - progress_width) // 2
        progress_y = 400
        
        # Fondo de la barra de progreso
        pygame.draw.rect(self.screen, self.colors["dark_green"], 
                         (progress_x, progress_y, progress_width, progress_height))
        
        # Progreso actual de la barra
        fill_width = int((self.boot_progress / 100) * progress_width)
        pygame.draw.rect(self.screen, self.colors["green_phosphor"], 
                         (progress_x, progress_y, fill_width, progress_height))
        
        # Porcentaje de progreso
        percent_text = f"{int(self.boot_progress)}%"
        text = self.font_medium.render(percent_text, True, self.colors["green_phosphor"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 430))
        
        # Cursor parpadeante para simular una terminal
        if self.cursor_blink < 30: # El cursor parpadea cada 30 frames
            cursor_text = self.font_medium.render("_", True, self.colors["green_phosphor"])
            self.screen.blit(cursor_text, (x + text.get_width() + 10, 430))
    
    def draw_main_interface(self):
        """Dibuja la interfaz principal del sistema (menú principal)."""
        self.screen.fill(self.colors["black"]) # Fondo negro
        
        # Título del menú principal
        title = "RETRO GAMING OS - MENÚ PRINCIPAL"
        text = self.font_large.render(title, True, self.colors["green_phosphor"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 50))
        
        # Opciones del menú, varían si el lanzador avanzado está disponible
        if self.game_launcher:
            # Menú para el lanzador avanzado
            menu_options = [
                "1. LANZADOR DE JUEGOS",
                "2. CONFIGURACIÓN",
                "3. APAGAR SISTEMA"
            ]
            
            start_y = 200
            for i, option in enumerate(menu_options):
                # Resalta la opción seleccionada con color ámbar
                color = self.colors["amber"] if i == self.selected_option else self.colors["green_phosphor"]
                text = self.font_medium.render(option, True, color)
                self.screen.blit(text, (100, start_y + i * 40))
            
            # Información adicional del sistema
            info_lines = [
                f"HORA DEL SISTEMA: {time.strftime('%H:%M:%S')}",
                f"JUEGOS ENCONTRADOS: {len(self.game_launcher.games) if hasattr(self.game_launcher, 'games') and self.game_launcher.games else 0}",
                f"ÚLTIMO JUGADO: NINGUNO", # Marcador de posición, no implementado
                "",
                "PRESIONA TECLA NUMÉRICA PARA SELECCIONAR",
                "FLECHAS: Navegar • ENTER: Seleccionar • ESC: Salir"
            ]
            
            info_y = 400
            for i, line in enumerate(info_lines):
                # Colores específicos para mensajes de control
                color = self.colors["amber"] if line.startswith("PRESIONA") or line.startswith("FLECHAS") else self.colors["gray"]
                text = self.font_small.render(line, True, color)
                self.screen.blit(text, (100, info_y + i * 20))
        else:
            # Menú para el lanzador simple (solo los juegos específicos)
            menu_options = [
                "1. JUEGO DE SNAKE", 
                "2. JUEGO DE TETRIS", 
                "3. JUEGO DE PONG",
                "4. JUEGO DE BREAKOUT",
                "5. SALIR"
            ]
            
            start_y = 200
            for i, option in enumerate(menu_options):
                color = self.colors["amber"] if i == self.selected_option else self.colors["green_phosphor"]
                text = self.font_medium.render(option, True, color)
                self.screen.blit(text, (100, start_y + i * 40))
            
            # Información simple para el lanzador simple
            info_lines = [
                "PRESIONA TECLA NUMÉRICA PARA SELECCIONAR",
                "O USA FLECHAS + ENTER",
                "ESC PARA SALIR"
            ]
            
            info_y = 400
            for i, line in enumerate(info_lines):
                text = self.font_small.render(line, True, self.colors["gray"])
                x = (self.screen.get_width() - text.get_width()) // 2
                self.screen.blit(text, (x, info_y + i * 20))
    
    def draw_simple_game_launcher(self):
        """
        Dibuja la interfaz del lanzador simple de juegos,
        mostrando solo los juegos permitidos.
        """
        self.screen.fill(self.colors["black"]) # Fondo negro
        
        # Título del lanzador simple
        title = "LANZADOR DE JUEGOS SIMPLE"
        text = self.font_large.render(title, True, self.colors["green_phosphor"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 50))
        
        if not self.games:
            # Mensaje si no se encuentran juegos permitidos
            text = self.font_medium.render("NO SE ENCONTRARON JUEGOS", True, self.colors["gray"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 200))
            
            text = self.font_small.render("Esperado: snake.py, tetris.py, pong.py, breakout.py", True, self.colors["gray"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 230))
        else:
            # Lista los juegos permitidos encontrados
            start_y = 150
            max_display = len(self.games) # Muestra todos los juegos encontrados de la lista permitida
            
            for i in range(max_display):
                game = self.games[i]
                color = self.colors["amber"] if i == self.selected_option else self.colors["green_phosphor"]
                prefix = "► " if i == self.selected_option else "  " # Indicador de selección
                game_text = f"{prefix}{game['title']}"
                
                text = self.font_medium.render(game_text, True, color)
                self.screen.blit(text, (100, start_y + i * 30))
        
        # Controles para el lanzador simple
        controls = "FLECHAS: Navegar • ENTER: Jugar • ESC: Volver"
        text = self.font_small.render(controls, True, self.colors["amber"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, self.screen.get_height() - 50))
    
    def update_boot_sequence(self):
        """Actualiza el progreso de la animación de arranque."""
        elapsed = time.time() - self.boot_start_time
        
        # Calcula el progreso en base a un tiempo total (ej. 3 segundos para completar)
        self.boot_progress = min(100, (elapsed / 3.0) * 100)
        
        # Cambia el mensaje de arranque a intervalos de progreso
        message_threshold = (self.boot_message_index + 1) * (100 / len(self.boot_messages))
        if self.boot_progress >= message_threshold and self.boot_message_index < len(self.boot_messages) - 1:
            self.boot_message_index += 1
            self.play_beep(frequency=1000, duration=50) # Sonido al cambiar de mensaje
        
        # Transición al menú principal cuando el arranque está completo
        if self.boot_progress >= 100:
            self.current_state = "main_menu"
            self.play_beep(frequency=1200, duration=200) # Sonido de arranque completo
    
    def launch_game(self, game_path):
        """
        Lanza un juego externo utilizando un subproceso de Python.
        Permite que el juego se ejecute y luego el OS retro retome el control.
        """
        try:
            import subprocess
            # Usa sys.executable para garantizar que se usa el intérprete Python actual
            print(f"Lanzando juego: {game_path}")
            result = subprocess.run([sys.executable, game_path], 
                                    capture_output=True, text=True)
            
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
                        self.play_beep()
                
                elif self.current_state == "main_menu":
                    if self.game_launcher:
                        # Lógica de navegación y selección para el menú principal (con GameLauncher)
                        max_options = 3 # "Lanzador de Juegos", "Configuración", "Apagar Sistema"
                        if event.key == pygame.K_1: # Lanzador de Juegos
                            self.current_state = "game_launcher"
                            self.selected_option = 0
                            self.play_beep()
                        elif event.key == pygame.K_2: # Configuración
                            print("Abriendo Configuración (Aún no implementado)...")
                            self.play_beep()
                        elif event.key == pygame.K_3: # Apagar Sistema
                            print("Apagando sistema...")
                            self.play_beep()
                            return False
                    else:
                        # Lógica de navegación y selección para el menú principal (sin GameLauncher)
                        # Opciones: Snake, Tetris, Pong, Breakout, Salir
                        max_options = 5 
                        
                        # Manejo de selección directa por número
                        if event.key == pygame.K_1: # Snake
                            game_to_launch = next((game for game in self.games if game['title'] == "SNAKE GAME"), None)
                            if game_to_launch: self.launch_game(game_to_launch["path"])
                            self.play_beep()
                        elif event.key == pygame.K_2: # Tetris
                            game_to_launch = next((game for game in self.games if game['title'] == "TETRIS MODERN"), None) # Nota: el título puede variar
                            if game_to_launch: self.launch_game(game_to_launch["path"])
                            self.play_beep()
                        elif event.key == pygame.K_3: # Pong
                            game_to_launch = next((game for game in self.games if game['title'] == "PONG GAME"), None)
                            if game_to_launch: self.launch_game(game_to_launch["path"])
                            self.play_beep()
                        elif event.key == pygame.K_4: # Breakout
                            game_to_launch = next((game for game in self.games if game['title'] == "BREAKOUT GAME"), None)
                            if game_to_launch: self.launch_game(game_to_launch["path"])
                            self.play_beep()
                        elif event.key == pygame.K_5: # Salir
                            print("Saliendo del sistema...")
                            self.play_beep()
                            return False
                        
                    # Navegación universal con flechas para el menú principal (ambos modos)
                    if event.key == pygame.K_UP:
                        self.selected_option = max(0, self.selected_option - 1)
                        self.play_beep(600, 50)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = min(max_options - 1, self.selected_option + 1)
                        self.play_beep(600, 50)
                    elif event.key == pygame.K_RETURN:
                        # Simula la pulsación numérica para la opción seleccionada con ENTER
                        if self.game_launcher:
                            if self.selected_option == 0: # LANZADOR DE JUEGOS
                                self.current_state = "game_launcher"
                                self.selected_option = 0
                            elif self.selected_option == 1: # CONFIGURACIÓN
                                print("Abriendo Configuración (Aún no implementado)...")
                            elif self.selected_option == 2: # APAGAR SISTEMA
                                print("Apagando sistema...")
                                return False
                        else: # Modo simple
                            if self.selected_option == 0: # SNAKE
                                game_to_launch = next((game for game in self.games if game['title'] == "SNAKE GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 1: # TETRIS
                                game_to_launch = next((game for game in self.games if game['title'] == "TETRIS MODERN"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 2: # PONG
                                game_to_launch = next((game for game in self.games if game['title'] == "PONG GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 3: # BREAKOUT
                                game_to_launch = next((game for game in self.games if game['title'] == "BREAKOUT GAME"), None)
                                if game_to_launch: self.launch_game(game_to_launch["path"])
                            elif self.selected_option == 4: # SALIR
                                print("Saliendo del sistema...")
                                return False
                        self.play_beep()
                
                elif self.current_state == "game_launcher":
                    # Manejo de entrada para el lanzador avanzado (si está activo)
                    if self.game_launcher:
                        result = self.game_launcher.handle_input(event)
                        if result == "back": # Si el lanzador avanzado indica "volver"
                            self.current_state = "main_menu"
                            self.selected_option = 0
                            self.play_beep()
                        elif result == "beep": # Si el lanzador avanzado necesita un sonido
                            self.play_beep()
                        elif result == "error": # Si el lanzador avanzado reporta un error
                            self.play_beep(400, 200)
                        elif isinstance(result, tuple) and result[0] == "launch_game":
                            game = result[1]
                            print(f"Intentando lanzar juego desde GameLauncher: {game['title']}")
                            # La lógica de lanzamiento real debería estar dentro de GameLauncher.handle_input
                            # o una función dedicada en GameLauncher para ejecutar el juego.
                            self.play_beep(800, 100)
                
                elif self.current_state == "simple_launcher":
                    # Manejo de entrada para el lanzador simple
                    if event.key == pygame.K_UP:
                        if hasattr(self, 'games') and self.games:
                            self.selected_option = max(0, self.selected_option - 1)
                            self.play_beep(600, 50)
                    elif event.key == pygame.K_DOWN:
                        if hasattr(self, 'games') and self.games:
                            self.selected_option = min(len(self.games) - 1, self.selected_option + 1)
                            self.play_beep(600, 50)
                    elif event.key == pygame.K_RETURN:
                        if hasattr(self, 'games') and self.games and 0 <= self.selected_option < len(self.games):
                            game = self.games[self.selected_option]
                            print(f"Lanzando juego desde el lanzador simple: {game['title']}")
                            self.launch_game(game["path"])
                            self.play_beep()
        return True
    
    def run(self):
        """Bucle principal de ejecución del sistema operativo."""
        running = True
        
        print("🎮 Iniciando Retro Gaming OS...")
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
                self.screen.fill(self.colors["black"]) # Limpia la pantalla para el lanzador
                self.game_launcher.draw() # Dibuja la interfaz del lanzador avanzado
            elif self.current_state == "simple_launcher":
                self.draw_simple_game_launcher() # Dibuja la interfaz del lanzador simple
            
            # Aplicar efectos visuales generales
            if self.config["scan_lines"]:
                self.draw_scanlines()
            
            self.draw_crt_border() # Dibuja el borde CRT
            
            # Actualizar contadores para animaciones
            self.cursor_blink = (self.cursor_blink + 1) % 60 # Controla el parpadeo
            self.scan_line_offset = (self.scan_line_offset + 1) % 3 # Controla el desplazamiento de scanlines
            
            # Actualizar la pantalla completa
            pygame.display.flip()
            self.clock.tick(60) # Limita a 60 FPS
        
        # Guarda la configuración antes de salir
        self.save_config()
        pygame.quit() # Desinicializa Pygame
        sys.exit() # Sale de la aplicación

def main():
    """Función principal para inicializar y ejecutar el Retro Gaming OS."""
    print("🎮 Iniciando Retro Gaming OS...")
    
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
            init_file.write_text("# Retro Gaming OS Module\n")
    
    # Crea archivos dummy para los juegos permitidos si no existen.
    # Esto es útil para probar el menú y el lanzador sin necesidad de los juegos completos.
    dummy_games_content = {
        "snake.py": "# Dummy Snake Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Snake Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Snake Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':\n    run_game()\n",
        "tetris.py": "# Dummy Tetris Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Tetris Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Tetris Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':\n    run_game()\n",
        "pong.py": "# Dummy Pong Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Pong Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Pong Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':\n    run_game()\n",
        "breakout.py": "# Dummy Breakout Game\nimport pygame, sys\n\npygame.init()\nscreen = pygame.display.set_mode((400, 300))\npygame.display.set_caption('Breakout Game')\nfont = pygame.font.Font(None, 36)\n\ndef run_game():\n    running = True\n    while running:\n        for event in pygame.event.get():\n            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):\n                running = False\n        screen.fill((0, 0, 0))\n        text = font.render('Breakout Game Running', True, (255, 255, 255))\n        screen.blit(text, (50, 100))\n        pygame.display.flip()\n        pygame.time.Clock().tick(30)\n    pygame.quit()\n    sys.exit()\n\nif __name__ == '__main__':\n    run_game()\n"
    }

    builtin_games_dir = Path("games/builtin")
    for filename, content in dummy_games_content.items():
        file_path = builtin_games_dir / filename
        if not file_path.exists():
            file_path.write_text(content)
            print(f"Archivo de juego dummy creado: {file_path}")

    # Iniciar el sistema operativo retro
    retro_os = RetroGameOS()
    retro_os.run()

if __name__ == "__main__":
    main()