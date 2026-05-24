import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(bg="#2c3e50")
        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = []
        
        # Status display indicating whose turn it is
        self.status_label = tk.Label(root, text="Player X's Turn", font=("Helvetica", 14, "bold"), bg="#2c3e50", fg="#ecf0f1")
        self.status_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Create 3x3 board buttons
        for i in range(9):
            btn = tk.Button(root, text="", font=("Helvetica", 20, "bold"), width=5, height=2,
                            bg="#34495e", fg="#ecf0f1", activebackground="#1abc9c", activeforeground="#ecf0f1",
                            command=lambda idx=i: self.make_move(idx))
            btn.grid(row=(i//3)+1, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)

    def make_move(self, idx):
        if self.board[idx] == "":
            self.board[idx] = self.current_player
            color = "#e74c3c" if self.current_player == "X" else "#3498db"
            self.buttons[idx].config(text=self.current_player, fg=color)
            
            if self.check_winner():
                messagebox.showinfo("Victory!", f"Player {self.current_player} wins!")
                self.reset_board()
            elif "" not in self.board:
                messagebox.showinfo("Draw!", "It's a draw!")
                self.reset_board()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.status_label.config(text=f"Player {self.current_player}'s Turn")

    def check_winner(self):
        win_coords = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(self.board[a] == self.board[b] == self.board[c] != "" for a, b, c in win_coords)

    def reset_board(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.status_label.config(text="Player X's Turn")
        for btn in self.buttons:
            btn.config(text="", fg="#ecf0f1")

if __name__ == "__main__":
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()
