import pygame
import sys
import math
import array

# -----------------------------------------------------------------------------
# Utility function to generate a raw sound buffer for a given frequency.
# -----------------------------------------------------------------------------
def generate_tone(freq=440, duration=0.1, volume=4096, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    buf = array.array('h')  # 'h' = signed 16-bit
    for i in range(n_samples):
        sample_val = int(volume * math.sin(2.0 * math.pi * freq * i / sample_rate))
        buf.append(sample_val)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

# -----------------------------------------------------------------------------
# Main menu
# -----------------------------------------------------------------------------
def main_menu():
    pygame.init()
    pygame.mixer.init()
    WIDTH, HEIGHT = 800, 600
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("$[C] Team Flames - Main Menu")
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    # Menu options
    menu_options = ["Start Game", "Credits", "Exit"]
    selected_option = 0
    running = True

    while running:
        window.fill((0, 0, 0))  # Black background

        # Draw menu options
        for i, option in enumerate(menu_options):
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            text = font.render(option, True, color)
            window.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if menu_options[selected_option] == "Start Game":
                        main_game()
                    elif menu_options[selected_option] == "Credits":
                        show_credits(window, font, small_font, clock)
                    elif menu_options[selected_option] == "Exit":
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()
        clock.tick(60)

# -----------------------------------------------------------------------------
# Show credits
# -----------------------------------------------------------------------------
def show_credits(window, font, small_font, clock):
    credits_text = [
        "$[C] Team Flames",
        "Developed by: Your Name",
        "Powered by: Pygame",
        "Music: Procedural Beeps",
        "Press ESC to return to the main menu",
    ]
    running = True

    while running:
        window.fill((0, 0, 0))  # Black background
        for i, line in enumerate(credits_text):
            text = small_font.render(line, True, (255, 255, 255))
            window.blit(text, (400 - text.get_width() // 2, 150 + i * 40))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Return to menu
                    return

        pygame.display.flip()
        clock.tick(60)

# -----------------------------------------------------------------------------
# Main Pong game
# -----------------------------------------------------------------------------
def main_game():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    WIDTH, HEIGHT = 800, 600
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("$[C] Team Flames - ChatGPT/CatLLM 20XX [C]")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    PADDLE_WIDTH = 10
    PADDLE_HEIGHT = 100
    PADDLE_SPEED = 5
    BALL_SIZE = 10
    BALL_SPEED_X = 4
    BALL_SPEED_Y = 4

    left_paddle_x, left_paddle_y = 10, HEIGHT // 2 - PADDLE_HEIGHT // 2
    right_paddle_x, right_paddle_y = WIDTH - PADDLE_WIDTH - 10, HEIGHT // 2 - PADDLE_HEIGHT // 2
    ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2

    left_score = 0
    right_score = 0

    font = pygame.font.SysFont(None, 36)

    beep_sound = generate_tone(freq=600, duration=0.07)  # beep
    boop_sound = generate_tone(freq=220, duration=0.15)  # boop

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            left_paddle_y -= PADDLE_SPEED
        if keys[pygame.K_s]:
            left_paddle_y += PADDLE_SPEED
        if keys[pygame.K_UP]:
            right_paddle_y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            right_paddle_y += PADDLE_SPEED

        left_paddle_y = max(0, min(HEIGHT - PADDLE_HEIGHT, left_paddle_y))
        right_paddle_y = max(0, min(HEIGHT - PADDLE_HEIGHT, right_paddle_y))

        ball_x += BALL_SPEED_X
        ball_y += BALL_SPEED_Y

        if ball_y <= 0 or ball_y + BALL_SIZE >= HEIGHT:
            BALL_SPEED_Y *= -1
            beep_sound.play()

        if (ball_x <= left_paddle_x + PADDLE_WIDTH and
            left_paddle_y <= ball_y <= left_paddle_y + PADDLE_HEIGHT) or \
           (ball_x + BALL_SIZE >= right_paddle_x and
            right_paddle_y <= ball_y <= right_paddle_y + PADDLE_HEIGHT):
            BALL_SPEED_X *= -1
            beep_sound.play()

        if ball_x < 0:
            right_score += 1
            boop_sound.play()
            ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2

        if ball_x > WIDTH:
            left_score += 1
            boop_sound.play()
            ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2

        window.fill(BLACK)
        pygame.draw.rect(window, WHITE, (left_paddle_x, left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(window, WHITE, (right_paddle_x, right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(window, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))

        score_text = font.render(f"{left_score} : {right_score}", True, WHITE)
        window.blit(score_text, (WIDTH // 2 - 20, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# -----------------------------------------------------------------------------
# Run the program
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main_menu()
    import pygame
    import sys
    import math
    import array

    # -----------------------------------------------------------------------------
    # Utility function to generate a raw sound buffer for a given frequency.
    # -----------------------------------------------------------------------------
    def generate_tone(freq=440, duration=0.1, volume=4096, sample_rate=44100):
        n_samples = int(sample_rate * duration)
        buf = array.array('h')  # 'h' = signed 16-bit
        for i in range(n_samples):
            sample_val = int(volume * math.sin(2.0 * math.pi * freq * i / sample_rate))
            buf.append(sample_val)
        sound = pygame.mixer.Sound(buffer=buf)
        return sound

    # -----------------------------------------------------------------------------
    # Main menu
    # -----------------------------------------------------------------------------
    def main_menu():
        pygame.init()
        pygame.mixer.init()
        WIDTH, HEIGHT = 800, 600
        window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("$[C] Team Flames - Main Menu")
        font = pygame.font.SysFont(None, 48)
        small_font = pygame.font.SysFont(None, 36)
        clock = pygame.time.Clock()

        # Menu options
        menu_options = ["Start Game", "Credits", "Exit"]
        selected_option = 0
        running = True

        while running:
            window.fill((0, 0, 0))  # Black background

            # Draw menu options
            for i, option in enumerate(menu_options):
                color = (255, 255, 255) if i == selected_option else (150, 150, 150)
                text = font.render(option, True, color)
                window.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if menu_options[selected_option] == "Start Game":
                            main_game()
                        elif menu_options[selected_option] == "Credits":
                            show_credits(window, font, small_font, clock)
                        elif menu_options[selected_option] == "Exit":
                            pygame.quit()
                            sys.exit()

            pygame.display.flip()
            clock.tick(60)

    # -----------------------------------------------------------------------------
    # Show credits
    # -----------------------------------------------------------------------------
    def show_credits(window, font, small_font, clock):
        credits_text = [
            "$[C] Team Flames",
            "Developed by: @[C] Flames ",
            "Powered by: Pygame",
            "Music: Procedural Beeps",
            "Press ESC to return to the main menu",
        ]
        running = True

        while running:
            window.fill((0, 0, 0))  # Black background
            for i, line in enumerate(credits_text):
                text = small_font.render(line, True, (255, 255, 255))
                window.blit(text, (400 - text.get_width() // 2, 150 + i * 40))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Return to menu
                        return

            pygame.display.flip()
            clock.tick(60)

    # -----------------------------------------------------------------------------
    # Main Pong game
    # -----------------------------------------------------------------------------
    def main_game():
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        WIDTH, HEIGHT = 800, 600
        window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("$[C] Team Flames - Game")

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)

        PADDLE_WIDTH = 10
        PADDLE_HEIGHT = 100
        PADDLE_SPEED = 5
        BALL_SIZE = 10
        BALL_SPEED_X = 4
        BALL_SPEED_Y = 4

        left_paddle_x, left_paddle_y = 10, HEIGHT // 2 - PADDLE_HEIGHT // 2
        right_paddle_x, right_paddle_y = WIDTH - PADDLE_WIDTH - 10, HEIGHT // 2 - PADDLE_HEIGHT // 2
        ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2

        left_score = 0
        right_score = 0

        font = pygame.font.SysFont(None, 36)

        beep_sound = generate_tone(freq=600, duration=0.07)  # beep
        boop_sound = generate_tone(freq=220, duration=0.15)  # boop

        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                left_paddle_y -= PADDLE_SPEED
            if keys[pygame.K_s]:
                left_paddle_y += PADDLE_SPEED
            if keys[pygame.K_UP]:
                right_paddle_y -= PADDLE_SPEED
            if keys[pygame.K_DOWN]:
                right_paddle_y += PADDLE_SPEED

            left_paddle_y = max(0, min(HEIGHT - PADDLE_HEIGHT, left_paddle_y))
            right_paddle_y = max(0, min(HEIGHT - PADDLE_HEIGHT, right_paddle_y))

            ball_x += BALL_SPEED_X
            ball_y += BALL_SPEED_Y

            if ball_y <= 0 or ball_y + BALL_SIZE >= HEIGHT:
                BALL_SPEED_Y *= -1
                beep_sound.play()

            if (ball_x <= left_paddle_x + PADDLE_WIDTH and
                left_paddle_y <= ball_y <= left_paddle_y + PADDLE_HEIGHT) or \
               (ball_x + BALL_SIZE >= right_paddle_x and
                right_paddle_y <= ball_y <= right_paddle_y + PADDLE_HEIGHT):
                BALL_SPEED_X *= -1
                beep_sound.play()

            if ball_x < 0:
                right_score += 1
                boop_sound.play()
                ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2

            if ball_x > WIDTH:
                left_score += 1
                boop_sound.play()
                ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2

            window.fill(BLACK)
            pygame.draw.rect(window, WHITE, (left_paddle_x, left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.rect(window, WHITE, (right_paddle_x, right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.rect(window, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))

            score_text = font.render(f"{left_score} : {right_score}", True, WHITE)
            window.blit(score_text, (WIDTH // 2 - 20, 20))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # -----------------------------------------------------------------------------
    # Run the program
    # -----------------------------------------------------------------------------
    if __name__ == "__main__":
        main_menu()
