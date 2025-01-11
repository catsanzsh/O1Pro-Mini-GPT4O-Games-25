import pygame
import sys
import math
import array

# -----------------------------------------------------------------------------
# GLOBAL CONSTANTS
# -----------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
GRAY      = (150, 150, 150)
SKY_BLUE  = (135, 206, 235)
GREEN     = (34, 139, 34)
GOLD      = (255, 215, 0)
RED       = (255, 0, 0)

# Game States
STATE_MAIN_MENU   = "MAIN_MENU"
STATE_FILE_SELECT = "FILE_SELECT"
STATE_CONFIG_MENU = "CONFIG_MENU"
STATE_GAMEPLAY    = "GAMEPLAY"
STATE_EXIT        = "EXIT"

# -----------------------------------------------------------------------------
# UTILITY - TONE GENERATION
# -----------------------------------------------------------------------------
def generate_tone(freq=440, duration=1.0, volume=4096, sample_rate=44100):
    """
    Generate a sine-wave audio buffer of specified frequency (freq),
    duration (seconds), volume (amplitude), and sample_rate.
    Returns a pygame.mixer.Sound object.
    """
    n_samples = int(sample_rate * duration)
    buf = array.array('h')  # 'h' = signed 16-bit
    for i in range(n_samples):
        # Simple sine wave at given frequency
        sample_val = int(volume * math.sin(2.0 * math.pi * freq * i / sample_rate))
        buf.append(sample_val)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

# -----------------------------------------------------------------------------
# CONFIG CLASS
# -----------------------------------------------------------------------------
class Config:
    def __init__(self, sound_volume=0.5, player_speed=5):
        self.sound_volume = sound_volume  # Range: 0.0 to 1.0
        self.player_speed = player_speed  # Integer value

# -----------------------------------------------------------------------------
# PLAYER CLASS
# -----------------------------------------------------------------------------
class Player:
    def __init__(self, x, y, speed=5, jump_speed=15, color=RED, radius=20):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.score = 0
        self.speed = speed
        self.jump_speed = jump_speed

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        # Left / Right Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = -self.jump_speed
            self.on_ground = False

    def apply_gravity(self, gravity=0.8):
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y = 10

    def move(self, platforms):
        self.x += self.vel_x
        self.y += self.vel_y

        # Screen boundaries
        if self.x - self.radius < 0:
            self.x = self.radius
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
        if self.y - self.radius < 0:
            self.y = self.radius
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vel_y = 0
            self.on_ground = True

        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if (self.x + self.radius > platform.x and
                self.x - self.radius < platform.x + platform.width and
                self.y + self.radius > platform.y and
                self.y - self.radius < platform.y + platform.height):
                # Check if above the platform
                if self.vel_y > 0 and self.y - self.radius < platform.y:
                    self.y = platform.y - self.radius
                    self.vel_y = 0
                    self.on_ground = True

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# -----------------------------------------------------------------------------
# PLATFORM CLASS
# -----------------------------------------------------------------------------
class Platform:
    def __init__(self, x, y, width, height, color=GREEN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.x, self.y, self.width, self.height))

# -----------------------------------------------------------------------------
# COLLECTIBLE CLASS
# -----------------------------------------------------------------------------
class Collectible:
    def __init__(self, x, y, radius=10, color=GOLD):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.collected = False

    def draw(self, surface):
        if not self.collected:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, player):
        if not self.collected:
            distance = math.hypot(self.x - player.x, self.y - player.y)
            if distance < self.radius + player.radius:
                self.collected = True
                player.score += 1

# -----------------------------------------------------------------------------
# MAIN GAME CLASS (STATE MACHINE)
# -----------------------------------------------------------------------------
class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Create main window
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BOINGYS Adventure")

        # Create clock
        self.clock = pygame.time.Clock()

        # Font resources
        self.font          = pygame.font.SysFont(None, 36)
        self.menu_font     = pygame.font.SysFont(None, 72)
        self.instruct_font = pygame.font.SysFont(None, 36)

        # Config & initial state
        self.config = Config()
        self.state  = STATE_MAIN_MENU

        # OST/music variables
        self.ost_sounds    = self.create_ost()
        self.current_note  = 0
        self.note_duration = 0.3
        self.note_timer    = 0
        self.ost_channel   = pygame.mixer.Channel(0)

        # Game objects
        self.player = Player(100, HEIGHT - 100, speed=self.config.player_speed)
        self.platforms = [
            Platform(0, HEIGHT - 40, WIDTH, 40),
            Platform(200, HEIGHT - 150, 200, 20),
            Platform(500, HEIGHT - 250, 200, 20),
            Platform(300, HEIGHT - 350, 200, 20),
        ]
        self.collectibles = [
            Collectible(250, HEIGHT - 170),
            Collectible(550, HEIGHT - 270),
            Collectible(350, HEIGHT - 370),
        ]

    # -------------------------------------------------------------------------
    # OST GENERATION
    # -------------------------------------------------------------------------
    def create_ost(self):
        # Simple scale: A4, B4, C5, D5, E5, F5, G5
        melody  = [440, 494, 523, 587, 659, 698, 784]
        volume  = 3000
        duration = 0.3  # seconds per note

        melody_sounds = []
        for freq in melody:
            sound = generate_tone(freq=freq, duration=duration, volume=volume)
            melody_sounds.append(sound)
        return melody_sounds

    def play_ost(self, dt):
        """
        Loops through the set of notes for a simple melody.
        """
        self.note_timer += dt
        if self.note_timer >= self.note_duration:
            self.note_timer = 0
            self.current_note = (self.current_note + 1) % len(self.ost_sounds)
            self.ost_channel.play(self.ost_sounds[self.current_note])

    # -------------------------------------------------------------------------
    # STATE MACHINE: MAIN LOOP
    # -------------------------------------------------------------------------
    def run(self):
        """
        Main loop for the entire game. Keeps running until state == STATE_EXIT.
        """
        # Start playing the first note in the background
        self.ost_channel.set_volume(self.config.sound_volume)
        self.ost_channel.play(self.ost_sounds[self.current_note], loops=-1)

        while self.state != STATE_EXIT:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            self.screen.fill(SKY_BLUE)

            # State-based logic
            if self.state == STATE_MAIN_MENU:
                self.main_menu(dt)

            elif self.state == STATE_FILE_SELECT:
                self.file_select_menu(dt)

            elif self.state == STATE_CONFIG_MENU:
                self.config_menu(dt)

            elif self.state == STATE_GAMEPLAY:
                self.gameplay(dt)

            pygame.display.flip()

        # Graceful shutdown
        pygame.quit()
        sys.exit()

    # -------------------------------------------------------------------------
    # UNIVERSAL MENU HELPER
    # -------------------------------------------------------------------------
    def run_menu(self, title, options, on_select_callback):
        """
        Displays a generic vertical menu with a given title and list of options.
        :param title: (str) The menu title displayed near the top of the screen
        :param options: (list[str]) The selectable options (strings)
        :param on_select_callback: (function) Called with the string of the chosen option
        """
        selected_option = 0

        while True:
            dt_menu = self.clock.tick(FPS) / 1000.0
            self.play_ost(dt_menu)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = STATE_EXIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        chosen = options[selected_option]
                        # Let the caller decide how to handle it
                        if on_select_callback(chosen):
                            return  # Some menus cause a state change

            # Render the menu screen
            self.screen.fill(SKY_BLUE)
            title_text = self.menu_font.render(title, True, BLACK)
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

            # Draw each option
            for idx, option in enumerate(options):
                if idx == selected_option:
                    color = WHITE
                    underline = True
                else:
                    color = GRAY
                    underline = False

                menu_item = self.instruct_font.render(option, True, color)
                x_pos = WIDTH // 2 - menu_item.get_width() // 2
                y_pos = HEIGHT // 2 + idx * 50
                self.screen.blit(menu_item, (x_pos, y_pos))
                if underline:
                    pygame.draw.line(
                        self.screen,
                        color,
                        (x_pos, y_pos + menu_item.get_height() + 2),
                        (x_pos + menu_item.get_width(), y_pos + menu_item.get_height() + 2),
                        2
                    )

            pygame.display.flip()

    # -------------------------------------------------------------------------
    # MENU: MAIN MENU
    # -------------------------------------------------------------------------
    def main_menu(self, dt):
        def on_select(chosen_option):
            if chosen_option == "Start Game":
                self.state = STATE_GAMEPLAY
                return True
            elif chosen_option == "File Select":
                self.state = STATE_FILE_SELECT
                return True
            elif chosen_option == "Config":
                self.state = STATE_CONFIG_MENU
                return True
            elif chosen_option == "Exit":
                self.state = STATE_EXIT
                return True
            return False

        menu_options = ["Start Game", "File Select", "Config", "Exit"]
        self.run_menu("BOINGYS Adventure", menu_options, on_select)

    # -------------------------------------------------------------------------
    # MENU: FILE SELECT
    # -------------------------------------------------------------------------
    def file_select_menu(self, dt):
        def on_select(chosen_option):
            if chosen_option == "Back":
                self.state = STATE_MAIN_MENU
                return True
            else:
                self.display_message(f"Selected {chosen_option}")
                # Remain in file select after showing message
                # (Alternatively, you might want to load the level and start gameplay here)
            return False

        file_options = ["Level 1", "Level 2", "Level 3", "Back"]
        self.run_menu("File Select", file_options, on_select)

    # -------------------------------------------------------------------------
    # MENU: CONFIG MENU
    # -------------------------------------------------------------------------
    def config_menu(self, dt):
        """
        We have a special case: adjusting volume & speed with LEFT/RIGHT keys.
        We'll still use run_menu for the layout, but handle LEFT/RIGHT in on_select.
        """
        def on_select(chosen_option):
            if chosen_option == "Back":
                self.state = STATE_MAIN_MENU
                return True
            return False

        config_options = ["Sound Volume", "Player Speed", "Back"]

        # We do an inner loop that uses run_menu, but we also check for arrow keys
        selected_option = 0

        while True:
            dt_menu = self.clock.tick(FPS) / 1000.0
            self.play_ost(dt_menu)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = STATE_EXIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(config_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(config_options)
                    elif event.key == pygame.K_LEFT:
                        if config_options[selected_option] == "Sound Volume":
                            self.config.sound_volume = max(0.0, self.config.sound_volume - 0.1)
                            self.ost_channel.set_volume(self.config.sound_volume)
                        elif config_options[selected_option] == "Player Speed":
                            self.config.player_speed = max(1, self.config.player_speed - 1)
                            self.player.speed = self.config.player_speed
                    elif event.key == pygame.K_RIGHT:
                        if config_options[selected_option] == "Sound Volume":
                            self.config.sound_volume = min(1.0, self.config.sound_volume + 0.1)
                            self.ost_channel.set_volume(self.config.sound_volume)
                        elif config_options[selected_option] == "Player Speed":
                            self.config.player_speed = min(10, self.config.player_speed + 1)
                            self.player.speed = self.config.player_speed
                    elif event.key == pygame.K_RETURN:
                        chosen = config_options[selected_option]
                        if on_select(chosen):
                            return

            # Render our config screen
            self.screen.fill(SKY_BLUE)
            title_text = self.menu_font.render("Config", True, BLACK)
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

            for idx, option in enumerate(config_options):
                if idx == selected_option:
                    color = WHITE
                else:
                    color = GRAY

                if option == "Sound Volume":
                    text_disp = f"{option}: {self.config.sound_volume:.1f}"
                elif option == "Player Speed":
                    text_disp = f"{option}: {self.config.player_speed}"
                else:
                    text_disp = option

                option_text = self.instruct_font.render(text_disp, True, color)
                x_pos = WIDTH // 2 - option_text.get_width() // 2
                y_pos = HEIGHT // 2 + idx * 50
                self.screen.blit(option_text, (x_pos, y_pos))

            pygame.display.flip()

    # -------------------------------------------------------------------------
    # FUNCTION: DISPLAY A SIMPLE MESSAGE
    # -------------------------------------------------------------------------
    def display_message(self, message):
        showing = True
        while showing:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = STATE_EXIT
                    return
                elif event.type == pygame.KEYDOWN:
                    showing = False

            self.screen.fill(SKY_BLUE)
            msg_text = self.instruct_font.render(message, True, BLACK)
            self.screen.blit(
                msg_text, 
                (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT // 2)
            )
            pygame.display.flip()

    # -------------------------------------------------------------------------
    # GAME STATE: GAMEPLAY
    # -------------------------------------------------------------------------
    def gameplay(self, dt):
        """
        The main gameplay loop for Boingy's Adventure.
        We'll exit if the user closes the window or presses ESC, or we can 
        eventually add a pause/escape back to main menu if desired.
        """
        while self.state == STATE_GAMEPLAY:
            dt_game = self.clock.tick(FPS) / 1000.0
            self.play_ost(dt_game)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = STATE_EXIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_MAIN_MENU
                        return

            # Handle player input
            self.player.handle_keys()

            # Apply gravity
            self.player.apply_gravity()

            # Move player
            self.player.move(self.platforms)

            # Check collectible collisions
            for c in self.collectibles:
                c.check_collision(self.player)

            # Drawing
            self.screen.fill(SKY_BLUE)

            # Draw platforms
            for platform in self.platforms:
                platform.draw(self.screen)

            # Draw collectibles
            for c in self.collectibles:
                c.draw(self.screen)

            # Draw player
            self.player.draw(self.screen)

            # Draw score
            score_text = self.font.render(f"Score: {self.player.score}", True, BLACK)
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()

# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    game = Game()
    game.run()
