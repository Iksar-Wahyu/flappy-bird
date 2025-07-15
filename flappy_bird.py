import pygame
import sys
import random
from connect import Scores

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Game settings
FPS = 60
clock = pygame.time.Clock()

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Game variables
GRAVITY = 0.5
FLAP_STRENGTH = -10
PIPE_WIDTH = 250
PIPE_HEIGHT = 400
PIPE_GAP = 200
PIPE_SPEED = 3

# Load font
font = pygame.font.Font(None, 36)

# Load images
bird_image = pygame.image.load('./asset/image/bird.png')
bird_image = pygame.transform.scale(bird_image, (30, 30))

pipe_top_image = pygame.image.load('./asset/image/pipe_top.png')
pipe_bottom_image = pygame.image.load('./asset/image/pipe_bottom.png')
pipe_top_image = pygame.transform.scale(pipe_top_image, (PIPE_WIDTH, PIPE_HEIGHT))
pipe_bottom_image = pygame.transform.scale(pipe_bottom_image, (PIPE_WIDTH, PIPE_HEIGHT))

background_image = pygame.image.load('./asset/image/nyoba1.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load music
pygame.mixer.music.load('./asset/sound/background_music.mp3')
pygame.mixer.music.play(-1)

# Database connection
db_connection = Scores()

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.y = max(0, min(self.y, SCREEN_HEIGHT))  # Keep the bird within the screen bounds

    def draw(self):
        bird_rect = bird_image.get_rect(center=(self.x, int(self.y)))
        screen.blit(bird_image, bird_rect)

    def get_position(self):
        return self.x, self.y

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)

    def move(self):
        self.x -= PIPE_SPEED

    def draw(self):
        pipe_top_rect = pipe_top_image.get_rect(bottomleft=(self.x, self.height))
        pipe_bottom_rect = pipe_bottom_image.get_rect(topleft=(self.x, self.height + PIPE_GAP))
        screen.blit(pipe_top_image, pipe_top_rect)
        screen.blit(pipe_bottom_image, pipe_bottom_rect)

    def is_collision(self, bird):
        bird_x, bird_y = bird.get_position()
        if self.x < bird_x < self.x + PIPE_WIDTH:
            if bird_y < self.height or bird_y > self.height + PIPE_GAP:
                return True
        return False

def draw_text_box(input_text):
    pygame.draw.rect(screen, GRAY, (150, 300, 300, 50))  # Background for the text box
    pygame.draw.rect(screen, WHITE, (150, 300, 300, 50), 3)  # Border
    text_surface = font.render(input_text, True, BLACK)
    screen.blit(text_surface, (160, 310))

def fade_screen():
    """Create a fade-out and fade-in transition."""
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)
    
    # Fade-out
    for alpha in range(0, 255, 10):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(25)
    
    # Clear the screen for the new game
    screen.fill(BLACK)
    pygame.display.update()
    pygame.time.delay(300)  # Slight pause before the fade-in
    
    # Fade-in
    for alpha in range(255, 0, -10):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)

def get_player_rank_and_leaderboard(player_name, player_score):
    """Retrieve the player's rank and leaderboard."""
    leaderboard = db_connection.get_top_scores(limit=10)  # Get the top 10 scores
    leaderboard_with_rank = []

    # Find rank of current player
    player_rank = None
    for index, (name, score) in enumerate(leaderboard):
        leaderboard_with_rank.append((index + 1, name, score))
        if name == player_name and score == player_score:
            player_rank = index + 1

    return player_rank, leaderboard_with_rank

def draw_leaderboard(player_rank, leaderboard):
    """Draw the leaderboard on the screen."""
    y_start = 150  # Starting Y position for the leaderboard
    header = font.render("Leaderboard", True, BLACK)
    screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, y_start - 50))

    for rank, name, score in leaderboard:
        color = BLACK if rank != player_rank else (0, 128, 0)  # Highlight current player's rank in green
        leaderboard_text = font.render(f"{rank}. {name}: {score}", True, color)
        screen.blit(leaderboard_text, (SCREEN_WIDTH // 2 - leaderboard_text.get_width() // 2, y_start))
        y_start += 30

def main():
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + 200)]
    score = 0
    game_state = "GAME_ACTIVE"  # GAME_ACTIVE, INPUT_NAME, DISPLAY_LEADERBOARD
    player_name = ""
    leaderboard_data = []
    player_rank = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_state == "GAME_ACTIVE":
                    if event.key == pygame.K_SPACE:
                        bird.flap()
                elif game_state == "INPUT_NAME":
                    if event.key == pygame.K_RETURN and player_name.strip():
                        # Save score and retrieve leaderboard
                        if db_connection:
                            db_connection.add_score(player_name, score)
                            player_rank, leaderboard_data = get_player_rank_and_leaderboard(player_name, score)
                        game_state = "DISPLAY_LEADERBOARD"
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        # Add typed character to player_name
                        if len(player_name) < 20:  # Limit the name length to 20 characters
                            player_name += event.unicode
                elif game_state == "DISPLAY_LEADERBOARD":
                    if event.key == pygame.K_RETURN:
                        # Restart the game
                        bird = Bird()
                        pipes = [Pipe(SCREEN_WIDTH + 200)]
                        score = 0
                        game_state = "GAME_ACTIVE"
                        player_name = ""
                        leaderboard_data = []
                        player_rank = None

        screen.blit(background_image, (0, 0))

        if game_state == "GAME_ACTIVE":
            bird.move()
            bird.draw()

            if pipes[-1].x < SCREEN_WIDTH - PIPE_WIDTH - 125:
                pipes.append(Pipe(SCREEN_WIDTH))

            for pipe in pipes:
                pipe.move()
                pipe.draw()

                if pipe.is_collision(bird) or bird.y == SCREEN_HEIGHT:
                    game_state = "INPUT_NAME"
                    if db_connection:  # Fetch leaderboard immediately
                        leaderboard_data = db_connection.get_top_scores(limit=10)

            pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]

            for pipe in pipes:
                if pipe.x + PIPE_WIDTH // 2 < bird.x and not hasattr(pipe, 'scored'):
                    score += 1
                    pipe.scored = True

            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))

        elif game_state == "INPUT_NAME":
            # Display "Game Over" message and score
            game_over_text = font.render("Game Over!", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
            score_text = font.render(f"Final Score: {score}", True, BLACK)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))

            # Display the text box for name input
            draw_text_box(player_name)

        elif game_state == "DISPLAY_LEADERBOARD":
            draw_leaderboard(player_rank, leaderboard_data)

            # Display instructions for restarting
            restart_text = font.render("Press Enter to Restart", True, BLACK)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 500))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
