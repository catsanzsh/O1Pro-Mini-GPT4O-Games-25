import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Paddle dimensions
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 10

# Ball dimensions
BALL_SIZE = 10

# Brick dimensions
BRICK_WIDTH = 40
BRICK_HEIGHT = 15

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brick Breaker")

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 60

# Paddle class
class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 5

    def move(self, direction):
        if direction == "LEFT" and self.x > 0:
            self.x -= self.speed
        if direction == "RIGHT" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

# Ball class
class Ball:
    def __init__(self):
        self.size = BALL_SIZE
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed_x = random.choice([-4, 4])
        self.speed_y = -4

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off walls
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.size:
            self.speed_x *= -1
        if self.y <= 0:
            self.speed_y *= -1

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))

# Brick class
class Brick:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.destroyed = False

    def draw(self):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Create bricks
def create_bricks():
    bricks = []
    colors = [RED, GREEN, BLUE, YELLOW]
    for row in range(5):
        for col in range(SCREEN_WIDTH // BRICK_WIDTH):
            brick_x = col * BRICK_WIDTH
            brick_y = row * BRICK_HEIGHT
            color = colors[row % len(colors)]
            bricks.append(Brick(brick_x, brick_y, color))
    return bricks

# Main game loop
def main():
    running = True

    # Create paddle, ball, and bricks
    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move("LEFT")
        if keys[pygame.K_RIGHT]:
            paddle.move("RIGHT")

        # Move ball
        ball.move()

        # Ball collision with paddle
        if (paddle.y <= ball.y + ball.size <= paddle.y + paddle.height and
                paddle.x <= ball.x <= paddle.x + paddle.width):
            ball.speed_y *= -1

        # Ball collision with bricks
        for brick in bricks:
            if not brick.destroyed:
                if (brick.x <= ball.x <= brick.x + brick.width and
                        brick.y <= ball.y <= brick.y + brick.height):
                    ball.speed_y *= -1
                    brick.destroyed = True

        # Ball falls below screen
        if ball.y > SCREEN_HEIGHT:
            running = False  # Game over

        # Draw everything
        paddle.draw()
        ball.draw()
        for brick in bricks:
            brick.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
