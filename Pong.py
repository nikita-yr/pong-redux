import pygame
import sys
import random
import math

pygame.init()

# Automatically detect screen resolution
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Margins
TOP_MARGIN = int(HEIGHT * 0.1) + 3  # 10% of screen height + 3 pixels
LINE_MARGIN = int(WIDTH * 0.03)  # 3% of screen width

# Ball class
class Ball:
    def __init__(self):
        self.size = int(WIDTH * 0.02)  # Ball size
        self.base_speed = 300  # Base speed in pixels per second
        self.rect = pygame.Rect(WIDTH // 2 - self.size // 2, HEIGHT // 2 - self.size // 2, self.size, self.size)
        self.speed_x = random.choice([-self.base_speed, self.base_speed])
        self.speed_y = random.choice([-self.base_speed, self.base_speed])
        self.hit_count = 0  # Paddle hit counter

        self.wobble_intensity = 100  # Maximum wobble effect (pixels per second)
        self.wobble_decay = 0.9  # Wobble decay factor
        self.wobble_x = 0  # Current wobble component on X axis
        self.wobble_y = 0  # Current wobble component on Y axis

    def move(self, delta_time):
        max_wobble = self.wobble_intensity * (1 + self.hit_count * 0.1)  # Increase wobble effect with speed
        self.wobble_x += random.uniform(-max_wobble, max_wobble) * delta_time
        self.wobble_y += random.uniform(-max_wobble, max_wobble) * delta_time
        self.wobble_x *= self.wobble_decay
        self.wobble_y *= self.wobble_decay

        self.rect.x += (self.speed_x + self.wobble_x) * delta_time
        self.rect.y += (self.speed_y + self.wobble_y) * delta_time

        # Bounce off the game area borders
        if self.rect.top <= game_area.top or self.rect.bottom >= game_area.bottom:
            self.speed_y *= -1

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = random.choice([-self.base_speed, self.base_speed])
        self.speed_y = random.choice([-self.base_speed, self.base_speed])
        self.hit_count = 0
        self.wobble_x = 0
        self.wobble_y = 0

    def increase_speed(self):
        self.hit_count += 1
        if self.hit_count == 1:
            increase_factor = 1.65
        elif self.hit_count == 2:
            increase_factor = 1.15
        else:
            increase_factor = 1.05
        self.speed_x *= increase_factor
        self.speed_y *= increase_factor

# Paddle class
class Paddle:
    def __init__(self, x, is_ai=False):
        self.width = int(WIDTH * 0.005)
        self.height = int((HEIGHT - TOP_MARGIN - LINE_MARGIN) * 0.16)
        self.rect = pygame.Rect(x, HEIGHT // 2 - self.height // 2 - int(HEIGHT * 0.005), self.width, self.height)
        self.speed = int(HEIGHT * 0.02)
        self.is_ai = is_ai

        self.move_direction = 1
        self.move_timer = random.randint(60, 180)
        self.move_count = 0
        self.target_y = self.rect.centery
        self.random_radius = 50

    def move_with_ai(self, ball, delta_time):
        if ball.rect.centerx > self.rect.centerx:
            target_y = ball.rect.centery
            move_amount = target_y - self.rect.centery
            if abs(move_amount) > self.speed:
                move_amount = self.speed if move_amount > 0 else -self.speed
            self.rect.y += move_amount
        else:
            if self.move_count < self.move_timer:
                move_amount = self.move_direction * self.speed
                if abs(self.rect.centery - self.target_y) < self.random_radius:
                    self.rect.y += move_amount
                self.move_count += 1
            else:
                self.move_direction = random.choice([1, -1])
                self.target_y = random.randint(game_area.top + self.height, game_area.bottom - self.height)
                self.move_timer = random.randint(60, 180)
                self.move_count = 0

        if self.rect.top < game_area.top:
            self.rect.top = game_area.top
        if self.rect.bottom > game_area.bottom:
            self.rect.bottom = game_area.bottom

    def move_with_mouse(self, mouse_y):
        target_y = mouse_y - self.rect.height // 2
        move_amount = target_y - self.rect.y
        if abs(move_amount) > self.speed:
            move_amount = self.speed if move_amount > 0 else -self.speed
        self.rect.y += move_amount
        if self.rect.top < game_area.top:
            self.rect.top = game_area.top
        if self.rect.bottom > game_area.bottom:
            self.rect.bottom = game_area.bottom

# Game area
game_area = pygame.Rect(
    LINE_MARGIN,
    TOP_MARGIN,  # New margin shifted 3 pixels down
    WIDTH - LINE_MARGIN * 2,
    HEIGHT - TOP_MARGIN - LINE_MARGIN + 38
)

# Main function
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)

    ball = Ball()
    left_paddle = Paddle(game_area.left + 30, is_ai=True)
    right_paddle = Paddle(game_area.right - 40)

    player_score = 0
    opponent_score = 0

    # Load font
    font_size = int(WIDTH * 0.05)
    font_path = pygame.font.match_font("arialbold")
    font = pygame.font.Font(font_path, font_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        delta_time = clock.get_time() / 1000  # Time between frames in seconds

        ball.move(delta_time)
        left_paddle.move_with_ai(ball, delta_time)
        mouse_y = pygame.mouse.get_pos()[1]
        right_paddle.move_with_mouse(mouse_y)

        if ball.rect.colliderect(left_paddle.rect):
            ball.speed_x = abs(ball.speed_x)
            ball.speed_y += (ball.rect.centery - left_paddle.rect.centery) // 10
            ball.increase_speed()

        if ball.rect.colliderect(right_paddle.rect):
            ball.speed_x = -abs(ball.speed_x)
            ball.speed_y += (ball.rect.centery - right_paddle.rect.centery) // 10
            ball.increase_speed()

        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, game_area, 2)
        pygame.draw.rect(screen, WHITE, ball.rect)
        pygame.draw.rect(screen, WHITE, left_paddle.rect)
        pygame.draw.rect(screen, WHITE, right_paddle.rect)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
