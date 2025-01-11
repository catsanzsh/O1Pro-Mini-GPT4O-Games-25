import tkinter as tk
import random

# Game constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GRID_SIZE = 20  # Size of each grid cell
SNAKE_SPEED = 100  # Movement speed in milliseconds

# Colors (Original or simple color scheme)
BACKGROUND_COLOR = "black"
SNAKE_COLOR = "green"
FOOD_COLOR = "red"
SCORE_COLOR = "white"
GAME_OVER_COLOR = "red"

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BACKGROUND_COLOR)
        self.canvas.pack()

        # Initialize game variables
        self.snake = [(GRID_SIZE * 3, GRID_SIZE * 3)]  # Initial position of the snake
        self.direction = "Right"  # Initial direction
        self.food_position = self.spawn_food()
        self.running = True
        self.score = 0

        # Bind key events for controlling the snake
        self.root.bind("<Up>", self.change_direction)
        self.root.bind("<Down>", self.change_direction)
        self.root.bind("<Left>", self.change_direction)
        self.root.bind("<Right>", self.change_direction)

        # Bind keys for restart and quit on game over
        self.root.bind("r", self.restart_game)
        self.root.bind("q", lambda _: self.root.destroy())

        # Start the game loop
        self.update_game()

    def spawn_food(self):
        """Spawn food at a random location not occupied by the snake."""
        while True:
            x = random.randint(0, (WINDOW_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
            y = random.randint(0, (WINDOW_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
            if (x, y) not in self.snake:
                return x, y

    def change_direction(self, event):
        """Change the snake's direction based on user input."""
        if event.keysym == "Up" and self.direction != "Down":
            self.direction = "Up"
        elif event.keysym == "Down" and self.direction != "Up":
            self.direction = "Down"
        elif event.keysym == "Left" and self.direction != "Right":
            self.direction = "Left"
        elif event.keysym == "Right" and self.direction != "Left":
            self.direction = "Right"

    def update_game(self):
        """Update the game state and redraw the canvas."""
        if not self.running:
            self.end_game()
            return

        # Move the snake
        head_x, head_y = self.snake[0]
        if self.direction == "Up":
            head_y -= GRID_SIZE
        elif self.direction == "Down":
            head_y += GRID_SIZE
        elif self.direction == "Left":
            head_x -= GRID_SIZE
        elif self.direction == "Right":
            head_x += GRID_SIZE

        # Check for collisions
        new_head = (head_x, head_y)
        if (head_x < 0 or head_x >= WINDOW_WIDTH or
            head_y < 0 or head_y >= WINDOW_HEIGHT or
            new_head in self.snake):
            self.running = False
            self.root.bell()  # Beep on game over
            self.end_game()
            return

        # Add new head to the snake
        self.snake.insert(0, new_head)

        # Check if the snake eats the food
        if new_head == self.food_position:
            self.root.bell()  # Beep on eating food
            self.food_position = self.spawn_food()
            self.score += 1
        else:
            self.snake.pop()  # Remove the tail if no food is eaten

        # Redraw the canvas
        self.canvas.delete(tk.ALL)
        self.draw_snake()
        self.draw_food()
        self.draw_score()

        # Schedule the next update
        self.root.after(SNAKE_SPEED, self.update_game)

    def draw_snake(self):
        """Draw the snake on the canvas."""
        for segment in self.snake:
            x, y = segment
            self.canvas.create_rectangle(
                x, y, x + GRID_SIZE, y + GRID_SIZE,
                fill=SNAKE_COLOR, outline=""
            )

    def draw_food(self):
        """Draw the food on the canvas."""
        x, y = self.food_position
        self.canvas.create_oval(
            x, y, x + GRID_SIZE, y + GRID_SIZE,
            fill=FOOD_COLOR, outline=""
        )

    def draw_score(self):
        """Display the current score on the canvas."""
        self.canvas.create_text(
            50, 10,
            text=f"Score: {self.score}",
            fill=SCORE_COLOR,
            anchor="nw",
            font=("Arial", 14)
        )

    def end_game(self):
        """Display the game over screen."""
        self.canvas.delete(tk.ALL)
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30,
            text="GAME OVER",
            fill=GAME_OVER_COLOR,
            font=("Arial", 24)
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
            text=f"Score: {self.score}",
            fill=SCORE_COLOR,
            font=("Arial", 16)
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30,
            text="Press R to Restart or Q to Quit",
            fill=SCORE_COLOR,
            font=("Arial", 14)
        )

    def restart_game(self, event):
        """Restart the game."""
        self.snake = [(GRID_SIZE * 3, GRID_SIZE * 3)]
        self.direction = "Right"
        self.food_position = self.spawn_food()
        self.running = True
        self.score = 0
        self.canvas.delete(tk.ALL)
        self.update_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
