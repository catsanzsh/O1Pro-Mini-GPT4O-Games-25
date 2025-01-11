import pygame
import random

# --------------------------------------------------------
# Configuration & Global Constants
# --------------------------------------------------------
SCREEN_WIDTH = 800  # Make it wider so we can place two grids side-by-side
SCREEN_HEIGHT = 600
GRID_SIZE = 20  # Each cell is 20x20 pixels

# For single-player or left grid in Versus mode
GRID_WIDTH = 10
GRID_HEIGHT = 20

FPS = 60
INITIAL_DROP_SPEED = FPS // 2  # Capsule drop every half second initially

# Colors
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY   = (100, 100, 100)

# Virus Count by level
LEVEL_VIRUS_COUNTS = {
    1: 10,
    2: 15,
    3: 20,
    4: 25,
    5: 30
}
MAX_LEVEL = 5

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dr. Mario 64 Inspired Clone")
clock = pygame.time.Clock()

# --------------------------------------------------------
# Block, Virus, and Grid Classes
# --------------------------------------------------------
class Block:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, surface, origin_x=0, origin_y=0):
        """
        origin_x, origin_y allow us to offset drawing 
        (useful in Versus mode where each grid is offset)
        """
        px = origin_x + self.x * GRID_SIZE
        py = origin_y + self.y * GRID_SIZE
        pygame.draw.rect(surface, self.color, (px, py, GRID_SIZE, GRID_SIZE))

class Virus(Block):
    """A specialized Block that we can later expand if needed."""
    pass

class Grid:
    """Manages the playfield, storing blocks and viruses."""
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.virus_count = 0

    def add_block(self, block):
        """Add a single block (or virus) to the grid if valid."""
        if 0 <= block.y < self.height and 0 <= block.x < self.width:
            self.grid[block.y][block.x] = block

    def remove_matches(self):
        """
        Remove horizontal/vertical matches of 4 or more same-colored pieces
        Returns the number of matched blocks removed. We'll use this for scoring.
        """
        removed_count = 0
        blocks_to_remove = set()

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] is not None:
                    color = self.grid[y][x].color

                    # Horizontal check
                    if x <= self.width - 4:
                        run_length = 1
                        for i in range(1, 4):
                            if self.grid[y][x + i] and self.grid[y][x + i].color == color:
                                run_length += 1
                            else:
                                break
                        if run_length == 4:
                            for i in range(4):
                                blocks_to_remove.add((x + i, y))

                    # Vertical check
                    if y <= self.height - 4:
                        run_length = 1
                        for i in range(1, 4):
                            if self.grid[y + i][x] and self.grid[y + i][x].color == color:
                                run_length += 1
                            else:
                                break
                        if run_length == 4:
                            for i in range(4):
                                blocks_to_remove.add((x, y + i))

        # Remove blocks
        for (rx, ry) in blocks_to_remove:
            if isinstance(self.grid[ry][rx], Virus):
                # Decrease virus count if a virus is removed
                self.virus_count -= 1
            self.grid[ry][rx] = None

        removed_count = len(blocks_to_remove)
        return removed_count

    def apply_gravity(self):
        """
        Let any floating blocks fall down until they land on another block
        or the bottom of the grid.
        """
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                if self.grid[y][x] is None:
                    temp_y = y - 1
                    while temp_y >= 0 and self.grid[y][x] is None:
                        if self.grid[temp_y][x] is not None:
                            self.grid[y][x] = self.grid[temp_y][x]
                            self.grid[temp_y][x] = None
                        temp_y -= 1

    def draw(self, surface, origin_x=0, origin_y=0):
        # Draw grid background (e.g., gray squares)
        for row_index in range(self.height):
            for col_index in range(self.width):
                rect_x = origin_x + col_index * GRID_SIZE
                rect_y = origin_y + row_index * GRID_SIZE
                pygame.draw.rect(surface, GRAY, 
                                 (rect_x, rect_y, GRID_SIZE, GRID_SIZE), 1)

        # Draw blocks
        for row in self.grid:
            for block in row:
                if block is not None:
                    block.draw(surface, origin_x, origin_y)

# --------------------------------------------------------
# Capsule Class
# --------------------------------------------------------
class Capsule:
    """Represents the falling pair of blocks."""
    def __init__(self, x, y, grid_width, grid_height):
        colors = [RED, GREEN, BLUE, YELLOW]
        self.blocks = [
            Block(x, y, random.choice(colors)),
            Block(x + 1, y, random.choice(colors))
        ]
        self.locked = False
        self.grid_width = grid_width
        self.grid_height = grid_height

    def move(self, dx, dy, grid):
        if self.locked:
            return
        new_positions = [(b.x + dx, b.y + dy) for b in self.blocks]

        if all(
            0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
            (grid.grid[ny][nx] is None or (nx, ny) in [(bl.x, bl.y) for bl in self.blocks])
            for (nx, ny) in new_positions
        ):
            for block, (nx, ny) in zip(self.blocks, new_positions):
                block.x = nx
                block.y = ny

    def rotate(self, grid):
        if self.locked:
            return
        pivot = self.blocks[0]
        pivot_x, pivot_y = pivot.x, pivot.y

        new_positions = []
        for block in self.blocks:
            rel_x = block.x - pivot_x
            rel_y = block.y - pivot_y
            # 90-degree rotation: (x, y) -> (-y, x)
            new_x = pivot_x - rel_y
            new_y = pivot_y + rel_x
            new_positions.append((new_x, new_y))

        # Check collision
        if all(
            0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
            (grid.grid[ny][nx] is None or (nx, ny) in [(b.x, b.y) for b in self.blocks])
            for (nx, ny) in new_positions
        ):
            for block, (nx, ny) in zip(self.blocks, new_positions):
                block.x = nx
                block.y = ny

    def drop(self, grid):
        if self.locked:
            return
        new_positions = [(b.x, b.y + 1) for b in self.blocks]
        can_move = True
        for (nx, ny), block in zip(new_positions, self.blocks):
            if ny >= self.grid_height:
                can_move = False
                break
            if grid.grid[ny][nx] is not None and (nx, ny) not in [(b.x, b.y) for b in self.blocks]:
                can_move = False
                break

        if can_move:
            for block, (nx, ny) in zip(self.blocks, new_positions):
                block.x = nx
                block.y = ny
        else:
            self.locked = True
            for block in self.blocks:
                grid.add_block(block)

    def draw(self, surface, origin_x=0, origin_y=0):
        for block in self.blocks:
            block.draw(surface, origin_x, origin_y)

# --------------------------------------------------------
# Single Player Dr. Mario Game Class (with improved chain scoring)
# --------------------------------------------------------
class DrMarioGame:
    def __init__(self, x_offset=0, y_offset=0, 
                 grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT, 
                 initial_level=1, player_name="Player"):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.grid_width = grid_width
        self.grid_height = grid_height

        self.grid = Grid(width=self.grid_width, height=self.grid_height)
        self.level = initial_level
        self.score = 0
        self.capsule = None
        self.drop_timer = 0
        self.drop_speed = INITIAL_DROP_SPEED
        self.running = True
        self.player_name = player_name

    def start_level(self, level):
        self.level = level
        self.grid = Grid(width=self.grid_width, height=self.grid_height)
        self.score = 0
        self.drop_speed = max(FPS // (2 + level // 2), 5)
        virus_count = LEVEL_VIRUS_COUNTS.get(level, 10)
        self.grid.virus_count = virus_count

        # Place viruses randomly in lower rows
        available_positions = [
            (x, y) for y in range(3, self.grid_height)
            for x in range(self.grid_width)
        ]
        random.shuffle(available_positions)
        for i in range(virus_count):
            vx, vy = available_positions[i]
            virus_color = random.choice([RED, GREEN, BLUE, YELLOW])
            self.grid.add_block(Virus(vx, vy, virus_color))

        self.spawn_next_capsule()

    def spawn_next_capsule(self):
        self.capsule = Capsule(self.grid_width // 2 - 1, 0, 
                               self.grid_width, self.grid_height)
        # If it collides, game over
        for block in self.capsule.blocks:
            if self.grid.grid[block.y][block.x] is not None:
                self.running = False  # Topped out

    def handle_input(self, keymap):
        """
        keymap is a dict telling which keys correspond to left, right, rotate, drop, etc.
        This allows us to pass unique controls for 2 players in Versus mode.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                # In a real app, you might want to handle a global exit.

        # Key states
        pressed = pygame.key.get_pressed()
        if pressed[keymap["left"]]:
            self.capsule.move(-1, 0, self.grid)
        if pressed[keymap["right"]]:
            self.capsule.move(1, 0, self.grid)
        if pressed[keymap["down"]]:
            self.capsule.drop(self.grid)
        if pressed[keymap["rotate"]]:
            self.capsule.rotate(self.grid)

    def update(self):
        if not self.running:
            return

        self.drop_timer += 1
        if self.drop_timer >= self.drop_speed:
            self.capsule.drop(self.grid)
            self.drop_timer = 0

        if self.capsule.locked:
            # Attempt chain combos
            chain_count = 0
            while True:
                removed = self.grid.remove_matches()
                if removed > 0:
                    chain_count += 1
                    self.grid.apply_gravity()
                else:
                    break

            # Score example: (blocks_removed) + chain bonus
            # We can do something like 100 points for first chain, 200 for second, etc.
            if chain_count > 0:
                # Just a simple chain bonus for demonstration
                chain_bonus = 100 * chain_count
                self.score += chain_bonus

            # Check virus condition
            if self.grid.virus_count <= 0:
                # Next level or done
                if self.level < MAX_LEVEL:
                    self.start_level(self.level + 1)
                else:
                    # Completed all levels
                    self.running = False
                    return

            # Spawn next capsule
            self.spawn_next_capsule()

    def draw(self, surface):
        # Draw the grid and capsule
        self.grid.draw(surface, self.x_offset, self.y_offset)
        if self.capsule:
            self.capsule.draw(surface, self.x_offset, self.y_offset)

        # UI text
        font = pygame.font.SysFont(None, 24)
        info_text = f"{self.player_name} | Lvl: {self.level} Score: {self.score} Viruses: {self.grid.virus_count}"
        text_surf = font.render(info_text, True, WHITE)
        surface.blit(text_surf, (self.x_offset + 10, self.y_offset + 10))

    def is_game_over(self):
        # If the grid was topped out, or viruses cleared at max level
        return not self.running

    def run_single_player(self):
        """A simple single-player loop to show usage."""
        self.start_level(self.level)
        keymap = {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "down": pygame.K_DOWN,
            "rotate": pygame.K_UP
        }

        while self.running:
            self.handle_input(keymap)
            self.update()

            screen.fill(BLACK)
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

        # Game Over or Victory
        self.show_game_over()

    def show_game_over(self):
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 48)
        if self.grid.virus_count <= 0 and self.level >= MAX_LEVEL:
            msg = f"{self.player_name} beat the game!"
        else:
            msg = f"{self.player_name} - GAME OVER"

        text_surf = font.render(msg, True, WHITE)
        rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text_surf, rect)
        pygame.display.flip()
        pygame.time.wait(3000)

# --------------------------------------------------------
# Versus Dr. Mario Game (2-Player)
# --------------------------------------------------------
class VersusDrMarioGame:
    """
    This class manages two DrMarioGame instances side by side.
    Each has its own controls, grid, score, viruses, etc.
    The first to clear viruses wins, or if someone tops out, they lose.
    """
    def __init__(self):
        # Each grid is 10 wide, 20 tall. We'll place them side by side.
        self.player1 = DrMarioGame(
            x_offset=50, y_offset=50,
            grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT,
            initial_level=1, player_name="Player 1"
        )
        self.player2 = DrMarioGame(
            x_offset=400, y_offset=50,  # offset to draw on the right
            grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT,
            initial_level=1, player_name="Player 2"
        )

        # Define separate controls
        self.keymap1 = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "down": pygame.K_s,
            "rotate": pygame.K_w
        }
        self.keymap2 = {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "down": pygame.K_DOWN,
            "rotate": pygame.K_UP
        }

        self.running = True

    def run_versus_mode(self):
        """Main loop for 2-player battle."""
        self.player1.start_level(1)
        self.player2.start_level(1)

        while self.running:
            # Gather events once, pass to both
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Player1 input
            pressed = pygame.key.get_pressed()
            if pressed[self.keymap1["left"]]:
                self.player1.capsule.move(-1, 0, self.player1.grid)
            if pressed[self.keymap1["right"]]:
                self.player1.capsule.move(1, 0, self.player1.grid)
            if pressed[self.keymap1["down"]]:
                self.player1.capsule.drop(self.player1.grid)
            if pressed[self.keymap1["rotate"]]:
                self.player1.capsule.rotate(self.player1.grid)

            # Player2 input
            if pressed[self.keymap2["left"]]:
                self.player2.capsule.move(-1, 0, self.player2.grid)
            if pressed[self.keymap2["right"]]:
                self.player2.capsule.move(1, 0, self.player2.grid)
            if pressed[self.keymap2["down"]]:
                self.player2.capsule.drop(self.player2.grid)
            if pressed[self.keymap2["rotate"]]:
                self.player2.capsule.rotate(self.player2.grid)

            # Update both
            self.player1.update()
            self.player2.update()

            # Check if either is done
            if self.player1.is_game_over() or self.player2.is_game_over():
                self.running = False
                break

            # Render
            screen.fill(BLACK)
            self.player1.draw(screen)
            self.player2.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

        # Determine winner
        self.show_winner()

    def show_winner(self):
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 48)

        p1_cleared = (self.player1.grid.virus_count <= 0 and self.player1.level >= MAX_LEVEL)
        p2_cleared = (self.player2.grid.virus_count <= 0 and self.player2.level >= MAX_LEVEL)

        if p1_cleared and not p2_cleared:
            msg = "Player 1 Wins!"
        elif p2_cleared and not p1_cleared:
            msg = "Player 2 Wins!"
        elif p1_cleared and p2_cleared:
            msg = "Both Cleared! It's a tie!"
        else:
            # If nobody cleared all viruses, decide who lost by top-out
            # In a full logic, you might check who topped out first.
            # For now, we just do a simple check:
            if self.player1.is_game_over() and not self.player2.is_game_over():
                msg = "Player 2 Wins (P1 Topped Out)!"
            elif self.player2.is_game_over() and not self.player1.is_game_over():
                msg = "Player 1 Wins (P2 Topped Out)!"
            else:
                msg = "Both Topped Out! It's a tie!"

        text_surf = font.render(msg, True, WHITE)
        rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text_surf, rect)
        pygame.display.flip()
        pygame.time.wait(3000)

# --------------------------------------------------------
# Main Entry Point
# --------------------------------------------------------
def main():
    # Choose between single-player or versus
    # For demonstration, we’ll do a quick menu:
    running = True
    mode = None

    while running and mode is None:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 48)
        text1 = font.render("Press 1 for Single Player", True, WHITE)
        text2 = font.render("Press 2 for Versus Mode", True, WHITE)
        screen.blit(text1, (200, 200))
        screen.blit(text2, (200, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 1
                elif event.key == pygame.K_2:
                    mode = 2

        clock.tick(FPS)

    if mode == 1:
        # Single-player
        game = DrMarioGame(player_name="SinglePlayer")
        game.run_single_player()
    elif mode == 2:
        # Versus
        versus_game = VersusDrMarioGame()
        versus_game.run_versus_mode()

    pygame.quit()

if __name__ == "__main__":
    main()
