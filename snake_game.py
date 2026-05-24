import tkinter as tk
import random

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        
        self.canvas = tk.Canvas(root, width=400, height=400, bg="#2c3e50")
        self.canvas.pack()
        
        # Working restart button
        self.restart_btn = tk.Button(root, text="Restart Game", font=("Helvetica", 11, "bold"), 
                                     bg="#e74c3c", fg="white", activebackground="#c0392b", activeforeground="white",
                                     command=self.restart)
        self.restart_btn.pack(pady=10)
        
        self.root.bind("<Key>", self.change_direction)
        self.start_game()

    def start_game(self):
        self.snake = [(20, 40), (20, 20), (20, 0)]
        self.direction = "Right"
        self.food = self.create_food()
        self.score = 0
        self.running = True
        self.canvas.delete("all")
        self.play()

    def restart(self):
        self.running = False  # Safely halt any existing loop
        self.root.after(150, self.start_game)  # Re-initialize game state cleanly

    def create_food(self):
        while True:
            pos = (random.randint(0, 19) * 20, random.randint(0, 19) * 20)
            if pos not in self.snake:
                return pos

    def change_direction(self, event):
        opp = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if event.keysym in opp and event.keysym != opp[self.direction]:
            self.direction = event.keysym

    def play(self):
        if not self.running:
            return
            
        x, y = self.snake[0]
        moves = {"Up": (0, -20), "Down": (0, 20), "Left": (-20, 0), "Right": (20, 0)}
        dx, dy = moves[self.direction]
        new_head = (x + dx, y + dy)

        # Collision detection (borders and self-collision)
        if (new_head[0] < 0 or new_head[0] >= 400 or new_head[1] < 0 or new_head[1] >= 400 or new_head in self.snake):
            self.canvas.create_text(200, 200, text=f"GAME OVER\nScore: {self.score}", fill="#ecf0f1", font=("Helvetica", 20, "bold"), justify="center")
            self.running = False
            return

        self.snake.insert(0, new_head)
        
        # Check food consumption
        if new_head == self.food:
            self.score += 1
            self.food = self.create_food()
        else:
            self.snake.pop()

        self.canvas.delete("all")
        # Draw Food
        self.canvas.create_oval(self.food[0]+2, self.food[1]+2, self.food[0]+18, self.food[1]+18, fill="#e74c3c", outline="")
        # Draw Snake
        for seg in self.snake:
            self.canvas.create_rectangle(seg[0]+1, seg[1]+1, seg[0]+19, seg[1]+19, fill="#2ecc71", outline="")
        
        self.root.after(100, self.play)

if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
