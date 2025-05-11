import tkinter as tk
from tkinter import messagebox
import json
import random

# Load questions from JSON file
with open("sustainability_trivia_questions.json", "r") as f:
    QUESTIONS = json.load(f)

class TriviaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sustainability Trivia Game")
        self.root.geometry("550x420")
        self.running = False
        self.time_mode = False  # Default: Normal Mode
        self.total_time = 60
        self.score = 0
        self.create_mode_select_screen()

    def create_mode_select_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Sustainability Trivia Game", font=("Helvetica", 18)).pack(pady=20)
        tk.Label(self.root, text="Choose Game Mode", font=("Helvetica", 14)).pack(pady=10)
        tk.Button(self.root, text="Normal Mode (No Timer)", font=("Helvetica", 14),
                  command=lambda: self.select_difficulty(False)).pack(pady=10)
        tk.Button(self.root, text="Time Challenge Mode (60 sec)", font=("Helvetica", 14),
                  command=lambda: self.select_difficulty(True)).pack(pady=10)

    def select_difficulty(self, time_mode):
        self.time_mode = time_mode
        self.clear_screen()
        tk.Label(self.root, text="Choose Difficulty", font=("Helvetica", 16)).pack(pady=20)
        for level in ["Beginner", "Intermediate", "Advanced"]:
            tk.Button(self.root, text=level, width=20, font=("Helvetica", 14),
                      command=lambda lvl=level.lower(): self.start_game(lvl)).pack(pady=10)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.questions = QUESTIONS[difficulty]
        random.shuffle(self.questions)
        self.current = 0
        self.score = 0
        self.time_left = self.total_time
        self.running = True
        self.show_question()
        if self.time_mode:
            self.update_timer()

    def show_question(self):
        self.clear_screen()
        if not self.running or self.current >= len(self.questions):
            self.end_game()
            return

        q_data = self.questions[self.current]
        self.correct_answer = q_data["correct"]
        options = q_data["options"]
        random.shuffle(options)

        tk.Label(self.root, text=f"Q{self.current + 1}: {q_data['question']}", wraplength=500, font=("Helvetica", 14)).pack(pady=20)

        for option in options:
            btn = tk.Button(self.root, text=option, width=40, font=("Helvetica", 12),
                            command=lambda opt=option: self.check_answer(opt))
            btn.pack(pady=5)

        if self.time_mode:
            self.label_timer = tk.Label(self.root, text=f"Time Left: {self.time_left} sec", font=("Helvetica", 12))
            self.label_timer.pack(pady=10)

        # Live score display
        self.label_score = tk.Label(self.root, text=f"Score: {self.score}", font=("Helvetica", 12))
        self.label_score.pack(pady=5)

    def update_timer(self):
        if self.running:
            if self.time_left > 0:
                self.time_left -= 1
                if hasattr(self, "label_timer"):
                    self.label_timer.config(text=f"Time Left: {self.time_left} sec")
                self.root.after(1000, self.update_timer)
            else:
                self.running = False
                self.end_game()

    def check_answer(self, selected):
        if selected == self.correct_answer:
            self.score += 1
        self.current += 1
        if self.running:
            self.show_question()

    def end_game(self):
        self.clear_screen()
        if self.time_mode:
            tk.Label(self.root, text="Time's Up!", font=("Helvetica", 18)).pack(pady=20)
        else:
            tk.Label(self.root, text="You've completed the quiz!", font=("Helvetica", 18)).pack(pady=20)
        tk.Label(self.root, text=f"Your Score: {self.score}/{self.current}", font=("Helvetica", 16)).pack(pady=10)
        tk.Button(self.root, text="Main Menu", font=("Helvetica", 14), command=self.create_mode_select_screen).pack(pady=10)
        tk.Button(self.root, text="Exit", font=("Helvetica", 14), command=self.root.quit).pack(pady=5)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = TriviaGame(root)
    root.mainloop()
