import pygame
import sys
import random
import math
import time


class PlantTree:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Set screen dimensions and layout
        self.WIDTH, self.HEIGHT = 600, 800 
        self.GRID_SIZE = 10
        self.CELL_SIZE =  self.WIDTH // self.GRID_SIZE

        # Colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.BLUE = (0, 0, 255)  
        self.BLACK = (0, 0, 0)  
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Plant the Tree First!!!")
        self.font = pygame.font.Font(None, 30)

        # Game state variables
        self.p1_x, self.p1_y = 0, 0
        self.p2_x, self.p2_y = self.GRID_SIZE-1, self.GRID_SIZE-1
        self.p1_score = 0
        self.p2_score = 0
        self.currentP = 1
        self.game_over = False
        self.drop_positions = []
        self.planted_positions = []
        self.house_positions = []
        self.original_drop_positions = []
        self.game_mode = "Human_vs_Human"  #default mode
        self.current_level = "medium" # default  ai difficulty

        # Load images
        self.load_images()
        self.new_game()  # Initialize game state

    def load_images(self):
        self.player2_img = pygame.image.load("farmer.png")
        self.player2_img = pygame.transform.scale(self.player2_img, (self.CELL_SIZE, self.CELL_SIZE))
        self.player_img = pygame.transform.flip(self.player2_img, True, False)
        self.plant_img = pygame.image.load("plant.png")
        self.plant_img = pygame.transform.scale(self.plant_img, (self.CELL_SIZE, self.CELL_SIZE))
        self.house_img = pygame.image.load("house.png")
        self.house_img = pygame.transform.scale(self.house_img, (self.CELL_SIZE, self.CELL_SIZE))


    def reset_game(self):
        self.p1_x, self.p1_y = 0, 0
        self.p2_x, self.p2_y = self.GRID_SIZE-1, self.GRID_SIZE-1
        self.p1_score = 0
        self.p2_score = 0
        self.currentP = 1
        self.game_over = False
        self.winner = None
        self.drop_positions = self.original_drop_positions.copy()
        self.planted_positions = []

    def new_game(self):
        """Start a new game"""
        # Fixed house positions
        self.house_positions = [
            (3,0), (4,0), (5,0), (6,0),
            (1,1), (3,1), (4,1), (5,1), (6,1), (8,1),
            (1,2), (8,2),
            (4,3), (5,3),
            (0,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (9,4),
            (0,5), (4,5), (5,5), (9,5),
            (0,7), (3,7), (6,7), (9,7),
            (0,8), (2,8), (3,8), (6,8), (7,8), (9,8),
            (0,9), (4,9), (5,9)
        ]

        # Generate new random unique drop positions
        self.drop_positions = []
        for _ in range (15):
            x = random.randint(1, self.GRID_SIZE - 2)
            y = random.randint(1, self.GRID_SIZE - 2)
            pos = (x, y)
            if pos not in self.drop_positions and pos not in self.house_positions:
                self.drop_positions.append(pos)

        self.original_drop_positions = self.drop_positions.copy()
        self.planted_positions = []

        # Reset player positions and scores
        self.reset_game()
        pygame.display.flip()

    def get_valid_moves(self, player):
        """Get all valid moves for a player"""
        if player == 1:
            x, y = self.p1_x, self.p1_y
        else:
            x, y = self.p2_x, self.p2_y
        
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4-directional movement
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE:
                if (nx, ny) not in self.house_positions:
                    if player == 1 and (nx, ny) != (self.p2_x, self.p2_y):
                        moves.append((nx, ny))
                    elif player == 2 and (nx, ny) != (self.p1_x, self.p1_y):
                        moves.append((nx, ny))
        return moves

    def evaluate_state(self):
        """Evaluate the current game state for the AI player (player 2)"""
        """AI code"""
        score = self.p2_score - self.p1_score
        
        if self.drop_positions:
            # Calculate closest distance to a drop position for each player
            min_dist_p1 = min([abs(self.p1_x - x) + abs(self.p1_y - y) for (x, y) in self.drop_positions], default=0)
            min_dist_p2 = min([abs(self.p2_x - x) + abs(self.p2_y - y) for (x, y) in self.drop_positions], default=0)
            
            # Reward for being closer to drops than opponent
            score += (min_dist_p1 - min_dist_p2) * 0.2  # Weight this factor
        
        return score
    
    def minimax(self, depth, alpha, beta, maximizing_player, start_time, time_limit=1.0):
        """Minimax algorithm with alpha-beta pruning"""
        """AI code"""
        # Check if we've reached max depth or game is over
        if depth == 0 or not self.drop_positions or time.time() - start_time > time_limit:
            return self.evaluate_state(), None
        
        valid_moves = self.get_valid_moves(2 if maximizing_player else 1)
        
        if not valid_moves:  # No valid moves
            return self.evaluate_state(), None
        
        best_move = None
        
        if maximizing_player:  # player AI
            max_eval = -math.inf
            for move in valid_moves:
                # Save current state
                old_p2_pos = (self.p2_x, self.p2_y)
                old_drops = self.drop_positions.copy()
                old_planted = self.planted_positions.copy()
                old_p2_score = self.p2_score
                
                # Make the move
                self.p2_x, self.p2_y = move
                if move in self.drop_positions:
                    self.drop_positions.remove(move)
                    self.planted_positions.append(move)
                    self.p2_score += 5
                
                # Recursive call
                current_eval, _ = self.minimax(depth - 1, alpha, beta, False, start_time, time_limit)
                
                # Undo the move
                self.p2_x, self.p2_y = old_p2_pos
                self.drop_positions = old_drops.copy()
                self.planted_positions = old_planted.copy()
                self.p2_score = old_p2_score
                
                # Update max evaluation
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = move
                
                # Alpha-beta pruning
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
                    
            return max_eval, best_move
        
        else:  # Human player
            min_eval = math.inf
            for move in valid_moves:
                # Save current state
                old_p1_pos = (self.p1_x, self.p1_y)
                old_drops = self.drop_positions.copy()
                old_planted = self.planted_positions.copy()
                old_p1_score = self.p1_score
                
                # Make the move
                self.p1_x, self.p1_y = move
                if move in self.drop_positions:
                    self.drop_positions.remove(move)
                    self.planted_positions.append(move)
                    self.p1_score += 5
                
                # Recursive call
                current_eval, _ = self.minimax(depth - 1, alpha, beta, True, start_time, time_limit)
                
                # Undo the move
                self.p1_x, self.p1_y = old_p1_pos
                self.drop_positions = old_drops.copy()
                self.planted_positions = old_planted.copy()
                self.p1_score = old_p1_score
                
                # Update min evaluation
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_move = move
                
                # Alpha-beta pruning
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
                    
            return min_eval, best_move


    def make_ai_move(self):
        """Make a random move for the AI player"""

        levels = {
            "easy" : 3,
            "medium": 6,
            "hard": 9
            }
        
       
        depth = levels[self.current_level]

         # Run minimax with alpha-beta pruning
        start_time = time.time()
        _, best_move = self.minimax(depth, -math.inf, math.inf, True, start_time)

        # get valid moves
        valid_moves = self.get_valid_moves(self.currentP)
        if valid_moves:
            move = random.choice(valid_moves)
            if self.currentP == 1:
                self.p1_x, self.p1_y = move
            else:
                self.p2_x, self.p2_y = best_move # if not player 1 use minimax move
               
            
            # Check for planting
            if (move in self.drop_positions) and self.currentP == 1:
                self.drop_positions.remove(move)
                self.planted_positions.append(move)
                self.p1_score += 5    
            elif ((best_move in self.drop_positions)) and self.currentP == 2:
                self.drop_positions.remove(best_move)
                self.planted_positions.append(best_move)    
                self.p2_score += 5
            
            self.currentP = 3 - self.currentP  # Switch players
        

    def end_game(self):
        """ Check if the game is over """
        if len(self.drop_positions) == 0 and not self.game_over:
            self.game_over = True
            if self.p1_score > self.p2_score:
                self.winner = 1
            elif self.p2_score > self.p1_score:
                self.winner = 2
            else:
                self.winner = 0 


    def run(self):
        """Run the game"""
        clock = pygame.time.Clock()
        ai_move_delay = 500  # milliseconds between AI moves
        last_ai_move_time = 0

        while True:
            current_time = pygame.time.get_ticks()
            
            self.end_game()

            # Handle AI moves 
            if not self.game_over and (
                (self.game_mode == "Human_vs_AI" and self.currentP == 2) or 
                (self.game_mode == "AI_vs_AI")
            ):
                if current_time - last_ai_move_time > ai_move_delay:
                    self.make_ai_move()
                    last_ai_move_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Handle human moves
                if not self.game_over and (
                    (self.game_mode == "Human_vs_Human") or
                    (self.game_mode == "Human_vs_AI" and self.currentP == 1)
                ):
                    # Move player 1 with arrow keys
                    if event.type == pygame.KEYDOWN and self.currentP == 1:
                        new_x, new_y = self.p1_x, self.p1_y
                        if event.key == pygame.K_UP and self.p1_y > 0:
                            new_y -= 1
                        elif event.key == pygame.K_DOWN and self.p1_y < self.GRID_SIZE - 1:
                            new_y += 1
                        elif event.key == pygame.K_LEFT and self.p1_x > 0:
                            new_x -= 1
                        elif event.key == pygame.K_RIGHT and self.p1_x < self.GRID_SIZE - 1:
                            new_x += 1

                        # Check if new position is valid
                        if (new_x, new_y) not in self.house_positions and (new_x, new_y) != (self.p2_x, self.p2_y):
                            self.p1_x, self.p1_y = new_x, new_y
                            self.currentP = 2  # Switch to player 2/AI

                            # Check for planting
                            if (self.p1_x, self.p1_y) in self.drop_positions:
                                self.drop_positions.remove((self.p1_x, self.p1_y))
                                self.planted_positions.append((self.p1_x, self.p1_y))
                                self.p1_score += 5

                    # Move player 2 with WASD keys 
                    if event.type == pygame.KEYDOWN and self.currentP == 2 and self.game_mode == "Human_vs_Human":
                        new_x, new_y = self.p2_x, self.p2_y
                        if event.key == pygame.K_w and self.p2_y > 0:
                            new_y -= 1
                        elif event.key == pygame.K_s and self.p2_y < self.GRID_SIZE - 1:
                            new_y += 1
                        elif event.key == pygame.K_a and self.p2_x > 0:
                            new_x -= 1
                        elif event.key == pygame.K_d and self.p2_x < self.GRID_SIZE - 1:
                            new_x += 1

                        # Check if new position is valid
                        if (new_x, new_y) not in self.house_positions and (new_x, new_y) != (self.p1_x, self.p1_y):
                            self.p2_x, self.p2_y = new_x, new_y
                            self.currentP = 1  # Switch to player 1

                            # Check for planting
                            if (self.p2_x, self.p2_y) in self.drop_positions:
                                self.drop_positions.remove((self.p2_x, self.p2_y))
                                self.planted_positions.append((self.p2_x, self.p2_y))
                                self.p2_score += 5

                # Handle mouse clicks for buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Check "New Game" button
                    if 50 <= mouse_x <= 200 and self.HEIGHT - 80 <= mouse_y <= self.HEIGHT - 40:
                        self.new_game()
                    # Check "Play Again" button
                    if 300 <= mouse_x <= 450 and self.HEIGHT - 80 <= mouse_y <= self.HEIGHT - 40:
                        self.reset_game()
                    # Check game mode buttons
                    if 50 <= mouse_x <= 200 and self.HEIGHT - 120 <= mouse_y <= self.HEIGHT - 90:
                        self.game_mode = "Human_vs_Human"
                        self.new_game()
                    if 200 <= mouse_x <= 350 and self.HEIGHT - 120 <= mouse_y <= self.HEIGHT - 90:
                        self.game_mode = "Human_vs_AI"
                        self.new_game()
                    if 350 <= mouse_x <= 500 and self.HEIGHT - 120 <= mouse_y <= self.HEIGHT - 90:
                        self.game_mode = "AI_vs_AI"
                        self.new_game()
                     # Check difficulty selection buttons
                    if 150 <= mouse_x <= 230 and self.HEIGHT - 45 <= mouse_y <= self.HEIGHT - 15:
                        self.current_level = "easy"
                    elif 240 <= mouse_x <= 340 and self.HEIGHT - 45 <= mouse_y <= self.HEIGHT - 15:
                        self.current_level = "medium"
                    elif 350 <= mouse_x <= 430 and self.HEIGHT - 45 <= mouse_y <= self.HEIGHT - 15:
                        self.current_level= "hard"

            self.display()
            clock.tick(60) 

    def display(self):
        """Display the grid-environment"""
        # Fill screen with white
        self.screen.fill(self.WHITE)

        # Draw grid
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                rect = pygame.Rect(col * self.CELL_SIZE, row * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(self.screen, self.GRAY, rect, 1)

        # Draw drop zones
        for tx, ty in self.drop_positions:
            drop_zones = pygame.Rect(tx * self.CELL_SIZE + self.CELL_SIZE // 4, 
                                   ty * self.CELL_SIZE + self.CELL_SIZE // 4,
                                   self.CELL_SIZE // 2, self.CELL_SIZE // 2)
            pygame.draw.rect(self.screen, self.BLUE, drop_zones)

        # Draw plants
        for px, py in self.planted_positions:
            self.screen.blit(self.plant_img, (px * self.CELL_SIZE, py * self.CELL_SIZE))

        # Draw houses
        for hx, hy in self.house_positions:
            self.screen.blit(self.house_img, (hx * self.CELL_SIZE, hy * self.CELL_SIZE))
        

        # Draw the farmers
        if self.player_img:
            self.screen.blit(self.player_img, (self.p1_x * self.CELL_SIZE, self.p1_y * self.CELL_SIZE))
            self.screen.blit(self.player2_img, (self.p2_x * self.CELL_SIZE, self.p2_y * self.CELL_SIZE))
   
        # Draw buttons
        # Game mode buttons
        pygame.draw.rect(self.screen, (200, 200, 200), (50, self.HEIGHT - 120, 150, 30))
        pygame.draw.rect(self.screen, (200, 200, 200), (200, self.HEIGHT - 120, 150, 30))
        pygame.draw.rect(self.screen, (200, 200, 200), (350, self.HEIGHT - 120, 150, 30))
        
        mode1_text = self.font.render("P vs P", True, self.BLACK)
        mode2_text = self.font.render("P vs AI", True, self.BLACK)
        mode3_text = self.font.render("AI vs AI", True, self.BLACK)

        self.screen.blit(mode1_text, (75, self.HEIGHT - 115))
        self.screen.blit(mode2_text, (225, self.HEIGHT - 115))
        self.screen.blit(mode3_text, (375, self.HEIGHT - 115))

        # "New Game" button
        pygame.draw.rect(self.screen, self.GREEN, (50, self.HEIGHT - 80, 150, 40))
        new_game_text = self.font.render("New Game", True, self.BLACK)
        self.screen.blit(new_game_text, (75, self.HEIGHT - 70))

        # "Play Again" button
        pygame.draw.rect(self.screen, self.RED, (300, self.HEIGHT - 80, 150, 40))
        play_again_text = self.font.render("Play Again", True, self.BLACK)
        self.screen.blit(play_again_text, (325, self.HEIGHT - 70))

        # Display the scores
        score_text = self.font.render(f"Player 1: {self.p1_score}  Player 2: {self.p2_score}", True, self.BLACK)
        self.screen.blit(score_text, (10,self.HEIGHT - 200 ))
        
        # Display current player
        current_text = self.font.render(f"Current: Player {self.currentP}", True, 
                                      (0, 0, 255) if self.currentP == 1 else (255, 0, 0))
        self.screen.blit(current_text, (10, self.HEIGHT - 175))
        
        # Display game mode
        mode_text = self.font.render(f"Mode: {self.game_mode.replace('_', ' ')}", True, self.BLACK)
        self.screen.blit(mode_text, (10, self.HEIGHT - 150))

        diff_text = self.font.render("AI Difficulty:", True, self.BLACK)
        self.screen.blit(diff_text, (10, self.HEIGHT - 30))
        
        # Easy button
        easy_color = (100, 255, 100) if self.current_level == "easy" else (200, 200, 200)
        pygame.draw.rect(self.screen, easy_color, (150, self.HEIGHT - 35, 80, 30))
        easy_text = self.font.render("Easy", True, self.BLACK)
        self.screen.blit(easy_text, (160, self.HEIGHT - 30))
        
        # Medium button
        medium_color = (255, 255, 100) if self.current_level == "medium" else (200, 200, 200)
        pygame.draw.rect(self.screen, medium_color, (240, self.HEIGHT - 35, 100, 30))
        medium_text = self.font.render("Medium", True, self.BLACK)
        self.screen.blit(medium_text, (250, self.HEIGHT - 30))
        
        # Hard button
        hard_color = (255, 100, 100) if self.current_level == "hard" else (200, 200, 200)
        pygame.draw.rect(self.screen, hard_color, (350, self.HEIGHT - 35, 80, 30))
        hard_text = self.font.render("Hard", True, self.BLACK)
        self.screen.blit(hard_text, (360, self.HEIGHT - 30))

        if self.game_over:
            # Display game over message
            if self.winner == 0:
                message = "Game Over: It's a tie!"
            else:
                message = f"Game Over: Player {self.winner} wins!"

            text = self.font.render(message, True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.WIDTH//2 + 100, self.GRID_SIZE * self.CELL_SIZE + 50))
            self.screen.blit(text, text_rect)

        # Update display
        pygame.display.flip()

if __name__ == "__main__":
    game = PlantTree()
    game.run()