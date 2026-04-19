import pygame
import random
import sys
import asyncio

# Initialize pygame
pygame.init()

# Game Constants
WIDTH = 400
HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
RED = (255, 69, 0)

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Verdana", 48, bold=True)
small_font = pygame.font.SysFont("Verdana", 24, bold=True)

class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.radius = 16

    def jump(self):
        self.velocity = self.jump_strength

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity

    def draw(self):
        # Draw Bird Body
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        # Draw Eye
        pygame.draw.circle(screen, WHITE, (int(self.x) + 6, int(self.y) - 6), 6)
        pygame.draw.circle(screen, BLACK, (int(self.x) + 6, int(self.y) - 6), 6, 1)
        pygame.draw.circle(screen, BLACK, (int(self.x) + 8, int(self.y) - 6), 2)
        # Draw Beak
        pygame.draw.polygon(screen, RED, [(self.x + 10, self.y), (self.x + 24, self.y + 4), (self.x + 10, self.y + 8)])
        pygame.draw.polygon(screen, BLACK, [(self.x + 10, self.y), (self.x + 24, self.y + 4), (self.x + 10, self.y + 8)], 1)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.gap = 160
        self.width = 60
        self.top_height = random.randint(50, HEIGHT - self.gap - 100) # Give ground safe space
        self.bottom_y = self.top_height + self.gap
        self.velocity = -4
        self.passed = False

    def update(self):
        self.x += self.velocity

    def draw(self):
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, BLACK, (self.x, 0, self.width, self.top_height), 2)
        # Top pipe cap
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.top_height - 20, self.width + 10, 20))
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.top_height - 20, self.width + 10, 20), 2)

        # Bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y))
        pygame.draw.rect(screen, BLACK, (self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y), 2)
        # Bottom pipe cap
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.bottom_y, self.width + 10, 20))
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.bottom_y, self.width + 10, 20), 2)

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y)
        return top_rect, bottom_rect

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    # Outline for text
    outline_img = font.render(text, True, BLACK)
    outline_rect = outline_img.get_rect(center=(x+2, y+2))
    screen.blit(outline_img, outline_rect)
    screen.blit(img, rect)

async def main():
    bird = Bird()
    pipes = [Pipe()]
    score = 0
    state = "START" # START, PLAYING, GAME_OVER

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state == "START":
                        state = "PLAYING"
                        bird.jump()
                    elif state == "PLAYING":
                        bird.jump()
                    elif state == "GAME_OVER":
                        state = "START"
                        bird = Bird()
                        pipes = [Pipe()]
                        score = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if state == "START":
                        state = "PLAYING"
                        bird.jump()
                    elif state == "PLAYING":
                        bird.jump()
                    elif state == "GAME_OVER":
                        state = "START"
                        bird = Bird()
                        pipes = [Pipe()]
                        score = 0

        screen.fill(SKY_BLUE)
        
        if state == "START":
            bird.draw()
            # Draw ground
            pygame.draw.rect(screen, (222, 184, 135), (0, HEIGHT - 50, WIDTH, 50))
            pygame.draw.line(screen, (139, 69, 19), (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 4)

            draw_text("FLAPPY BIRD", font, WHITE, WIDTH // 2, HEIGHT // 2 - 80)
            draw_text("Press SPACE or Click", small_font, WHITE, WIDTH // 2, HEIGHT // 2 + 30)
            draw_text("to Start", small_font, WHITE, WIDTH // 2, HEIGHT // 2 + 60)

        elif state == "PLAYING":
            bird.update()
            bird.draw()

            # Pipe logic
            if pipes[-1].x < WIDTH - 200:
                pipes.append(Pipe())

            for pipe in pipes:
                pipe.update()
                pipe.draw()

                # Collision
                top_rect, bottom_rect = pipe.get_rects()
                bird_rect = bird.get_rect()
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                    state = "GAME_OVER"

                # Score logic
                if pipe.x + pipe.width < bird.x and not pipe.passed:
                    pipe.passed = True
                    score += 1

            # Boundaries (hitting ground or ceiling)
            if bird.y + bird.radius > HEIGHT - 50 or bird.y - bird.radius < 0:
                state = "GAME_OVER"

            # Remove off-screen pipes
            pipes = [pipe for pipe in pipes if pipe.x + pipe.width > -50]

            # Draw ground
            pygame.draw.rect(screen, (222, 184, 135), (0, HEIGHT - 50, WIDTH, 50))
            pygame.draw.line(screen, (139, 69, 19), (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 4)

            draw_text(str(score), font, WHITE, WIDTH // 2, 50)

        elif state == "GAME_OVER":
            for pipe in pipes:
                pipe.draw()
            
            # Draw ground
            pygame.draw.rect(screen, (222, 184, 135), (0, HEIGHT - 50, WIDTH, 50))
            pygame.draw.line(screen, (139, 69, 19), (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 4)

            bird.draw()
            draw_text("GAME OVER!", font, RED, WIDTH // 2, HEIGHT // 2 - 80)
            draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text("Press SPACE to Restart", small_font, WHITE, WIDTH // 2, HEIGHT // 2 + 60)

        pygame.display.flip()
        
        # Required for Pygbag (Web compatibility)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
