#!/usr/bin/env python3
"""
Setup script para Retro Gaming OS
Crea la estructura de directorios y archivos necesarios
"""

import os
import json
from pathlib import Path

def create_directory_structure():
    """Crear estructura de directorios"""
    directories = [
        "core",
        "ui", 
        "games/builtin",
        "games/roms",
        "games/emulators",
        "assets/fonts",
        "assets/sounds", 
        "assets/graphics",
        "assets/themes",
        "config"
    ]
    
    print("🎮 Creando estructura de directorios...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Creado: {directory}/")

def create_init_files():
    """Crear archivos __init__.py"""
    init_locations = ["core", "ui"]
    
    print("\n📦 Creando archivos __init__.py...")
    for location in init_locations:
        init_path = Path(location) / "__init__.py"
        if not init_path.exists():
            init_path.write_text("# Retro Gaming OS Module\n")
            print(f"✓ Creado: {init_path}")

def create_game_launcher_file():
    """Crear archivo game_launcher.py en ui/"""
    launcher_code = '''"""
Game Launcher - Lanzador de juegos retro con interfaz grid
"""

import pygame
import os
import json
import subprocess
import time
from pathlib import Path

class GameLauncher:
    def __init__(self, screen, colors, fonts):
        self.screen = screen
        self.colors = colors
        self.fonts = fonts
        
        # Estado del launcher
        self.selected_game = 0
        self.scroll_offset = 0
        self.games_per_row = 4
        self.games_per_page = 12
        
        # Lista de juegos
        self.games = []
        self.categories = ["ALL", "ARCADE", "RPG", "PUZZLE", "ACTION", "CLASSIC"]
        self.current_category = "ALL"
        
        # Variables de animación
        self.selection_animation = 0
        self.title_scroll = 0
        
        # Cargar base de datos de juegos
        self.load_game_database()
        self.scan_games_directory()
    
    def load_game_database(self):
        """Cargar base de datos de juegos"""
        db_path = Path("config/game_database.json")
        
        # Base de datos por defecto
        default_games = [
            {
                "title": "SNAKE RETRO",
                "filename": "snake.py",
                "category": "CLASSIC",
                "description": "Classic snake game with retro twist",
                "builtin": True,
                "playable": True
            },
            {
                "title": "RETRO PONG",
                "filename": "pong.py", 
                "category": "ARCADE",
                "description": "Two-player pong game",
                "builtin": True,
                "playable": True
            }
        ]
        
        if db_path.exists():
            try:
                with open(db_path, 'r') as f:
                    self.games = json.load(f)
            except:
                self.games = default_games
        else:
            self.games = default_games
            self.save_game_database()
    
    def save_game_database(self):
        """Guardar base de datos de juegos"""
        db_path = Path("config/game_database.json")
        try:
            with open(db_path, 'w') as f:
                json.dump(self.games, f, indent=2)
        except Exception as e:
            print(f"Error saving game database: {e}")
    
    def scan_games_directory(self):
        """Escanear directorio de juegos"""
        games_dir = Path("games/builtin")
        if games_dir.exists():
            for file in games_dir.glob("*.py"):
                if not any(g["filename"] == file.name for g in self.games):
                    self.games.append({
                        "title": file.stem.upper().replace("_", " "),
                        "filename": file.name,
                        "category": "CLASSIC",
                        "description": "Discovered game",
                        "builtin": True,
                        "playable": file.exists()
                    })
    
    def get_filtered_games(self):
        """Obtener juegos filtrados por categoría"""
        if self.current_category == "ALL":
            return self.games
        return [g for g in self.games if g["category"] == self.current_category]
    
    def draw(self):
        """Dibujar el launcher completo"""
        # Título principal
        title = "GAME LAUNCHER"
        text = self.fonts["large"].render(title, True, self.colors["green_phosphor"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 20))
        
        # Mensaje simple si no hay juegos
        filtered_games = self.get_filtered_games()
        if not filtered_games:
            text = self.fonts["medium"].render("NO GAMES FOUND", True, self.colors["gray"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 200))
        else:
            # Lista simple de juegos
            start_y = 100
            for i, game in enumerate(filtered_games[:10]):  # Mostrar máximo 10
                color = self.colors["green_phosphor"] if i == self.selected_game else self.colors["gray"]
                prefix = "► " if i == self.selected_game else "  "
                game_text = f"{prefix}{game['title']}"
                
                text = self.fonts["medium"].render(game_text, True, color)
                self.screen.blit(text, (100, start_y + i * 30))
        
        # Controles
        controls = "ARROWS: Navigate • ENTER: Play • ESC: Back"
        text = self.fonts["small"].render(controls, True, self.colors["amber"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 500))
    
    def handle_input(self, event):
        """Manejar input del usuario"""
        filtered_games = self.get_filtered_games()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key == pygame.K_UP:
                if self.selected_game > 0:
                    self.selected_game -= 1
                return "beep"
            elif event.key == pygame.K_DOWN:
                if self.selected_game < len(filtered_games) - 1:
                    self.selected_game += 1
                return "beep"
            elif event.key == pygame.K_RETURN:
                if 0 <= self.selected_game < len(filtered_games):
                    game = filtered_games[self.selected_game]
                    if game["playable"]:
                        return ("launch_game", game)
                return "error"
        
        return None
    
    def launch_game(self, game):
        """Lanzar un juego específico"""
        if game["builtin"]:
            game_path = Path("games/builtin") / game["filename"]
            if game_path.exists():
                try:
                    result = subprocess.run(["python", str(game_path)], 
                                          capture_output=True, text=True)
                    return result.returncode == 0
                except Exception as e:
                    print(f"Failed to launch game: {e}")
                    return False
        return False
    
    def update(self):
        """Actualizar animaciones"""
        self.selection_animation = (self.selection_animation + 1) % 120
'''
    
    launcher_path = Path("ui/game_launcher.py")
    if not launcher_path.exists():
        launcher_path.write_text(launcher_code)
        print(f"✓ Creado: {launcher_path}")

def create_config_files():
    """Crear archivos de configuración"""
    print("\n⚙️ Creando archivos de configuración...")
    
    # settings.json
    settings = {
        "theme": "green_phosphor",
        "resolution": [800, 600],
        "fullscreen": False,
        "sound_enabled": True,
        "boot_animation": True,
        "scan_lines": True,
        "games_directory": "./games/",
        "last_played": []
    }
    
    settings_path = Path("config/settings.json")
    if not settings_path.exists():
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        print(f"✓ Creado: {settings_path}")
    
    # game_database.json
    game_db = [
        {
            "title": "SNAKE RETRO",
            "filename": "snake.py",
            "category": "CLASSIC",
            "description": "Classic snake game with retro twist",
            "builtin": True,
            "playable": True
        },
        {
            "title": "RETRO PONG",
            "filename": "pong.py", 
            "category": "ARCADE",
            "description": "Two-player pong game",
            "builtin": True,
            "playable": True
        }
    ]
    
    db_path = Path("config/game_database.json")
    if not db_path.exists():
        with open(db_path, 'w') as f:
            json.dump(game_db, f, indent=2)
        print(f"✓ Creado: {db_path}")

def create_readme():
    """Crear archivo README"""
    readme_content = """# 🎮 Retro Gaming OS

Sistema operativo retro gaming creado en Python con Pygame.

## 🚀 Instalación y Uso

1. Instalar dependencias:
```bash
pip install pygame
```

2. Ejecutar el setup (opcional):
```bash
python setup.py
```

3. Iniciar el sistema:
```bash
python main.py
```

## 🎯 Características

- ✅ Boot sequence animado
- ✅ Interfaz retro con efectos CRT
- ✅ Game Launcher funcional
- ✅ Juegos integrados (Snake, Pong)
- ✅ Sonidos retro
- ✅ Configuración persistente

## 🕹️ Controles

### Sistema Principal
- **Números 1-5**: Seleccionar opción del menú
- **ESC**: Salir/Volver

### Game Launcher
- **Flechas**: Navegar
- **Enter**: Lanzar juego
- **ESC**: Volver al menú

### Snake
- **Flechas**: Mover serpiente
- **Espacio**: Pausar/Reiniciar
- **ESC**: Salir

### Pong
- **W/S**: Jugador 1
- **↑/↓**: Jugador 2 (si AI desactivada)
- **A**: Toggle AI
- **Espacio**: Pausar/Jugar
- **R**: Reiniciar

## 📁 Estructura

```
retro-gaming-os/
├── main.py              # Boot loader principal
├── setup.py             # Script de configuración
├── core/                # Módulos del sistema
├── ui/                  # Interfaces de usuario
│   └── game_launcher.py # Lanzador de juegos
├── games/               # Directorio de juegos
│   └── builtin/         # Juegos integrados
│       ├── snake.py     # Snake retro
│       └── pong.py      # Pong retro
├── config/              # Archivos de configuración
└── assets/              # Recursos (fuentes, sonidos, etc.)
```

## 🎨 Temas

El sistema usa una paleta de colores retro:
- Verde fósforo (#00FF00)
- Ámbar (#FFBF00) 
- Negro (#000000)
- Gris (#808080)

## 🔧 Desarrollo

Para agregar nuevos juegos:

1. Crear archivo .py en `games/builtin/`
2. El juego debe ser ejecutable independientemente
3. Se detectará automáticamente en el siguiente arranque

## 📝 TODO

- [ ] Terminal funcional
- [ ] File browser
- [ ] Más juegos integrados
- [ ] Soporte para emuladores
- [ ] Sistema de configuración avanzado
- [ ] Efectos visuales mejorados

¡Disfruta de la experiencia retro! 🕹️
"""
    
    readme_path = Path("README.md")
    if not readme_path.exists():
        readme_path.write_text(readme_content)
        print(f"✓ Creado: {readme_path}")

def main():
    """Función principal del setup"""
    print("🎮 RETRO GAMING OS - SETUP")
    print("=" * 40)
    
    create_directory_structure()
    create_init_files()
    create_game_launcher_file()
    create_config_files()
    create_readme()
    
    print("\n🎉 Setup completado!")
    print("\nPara iniciar el sistema:")
    print("python main.py")
    print("\nAsegúrate de tener los juegos en games/builtin/:")
    print("- snake.py")
    print("- pong.py")

if __name__ == "__main__":
    main()