import pygame
import sys
import random
import math

pygame.init()

# Automatyczne wykrywanie rozdzielczości ekranu
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
FPS = 60

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Marginesy
TOP_MARGIN = int(HEIGHT * 0.1) + 3  # 10% wysokości ekranu + 3 piksele
LINE_MARGIN = int(WIDTH * 0.03)  # 3% szerokości ekranu

# Klasa dla piłki
class Ball:
    def __init__(self):
        self.size = int(WIDTH * 0.02)  # Rozmiar piłki
        self.base_speed = 300  # Podstawowa prędkość piłki w pikselach na sekundę
        self.rect = pygame.Rect(WIDTH // 2 - self.size // 2, HEIGHT // 2 - self.size // 2, self.size, self.size)
        self.speed_x = random.choice([-self.base_speed, self.base_speed])
        self.speed_y = random.choice([-self.base_speed, self.base_speed])
        self.hit_count = 0  # Licznik uderzeń rakietką

        self.wobble_intensity = 100  # Maksymalne odchylenie drżenia (piksele na sekundę)
        self.wobble_decay = 0.9  # Zanik drżenia
        self.wobble_x = 0  # Bieżący składnik drżenia po osi X
        self.wobble_y = 0  # Bieżący składnik drżenia po osi Y

    def move(self, delta_time):
        max_wobble = self.wobble_intensity * (1 + self.hit_count * 0.1)  # Wzrost efektu drżenia wraz ze wzrostem prędkości
        self.wobble_x += random.uniform(-max_wobble, max_wobble) * delta_time
        self.wobble_y += random.uniform(-max_wobble, max_wobble) * delta_time
        self.wobble_x *= self.wobble_decay
        self.wobble_y *= self.wobble_decay

        self.rect.x += (self.speed_x + self.wobble_x) * delta_time
        self.rect.y += (self.speed_y + self.wobble_y) * delta_time

        # Odbicie od krawędzi pola gry
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


# Klasa dla rakietki
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

# Obszar gry
game_area = pygame.Rect(
    LINE_MARGIN,
    TOP_MARGIN,  # Nowy margines przesunięty o 3 piksele w dół
    WIDTH - LINE_MARGIN * 2,
    HEIGHT - TOP_MARGIN - LINE_MARGIN + 38
)

# Główna funkcja
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

    # Ładowanie czcionki
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

        delta_time = clock.get_time() / 1000  # Czas między klatkami w sekundach

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

        if ball.rect.left <= game_area.left:
            opponent_score += 1
            ball.reset()

        elif ball.rect.right >= game_area.right:
            player_score += 1
            ball.reset()

        screen.fill(BLACK)

        pygame.draw.rect(screen, WHITE, game_area, 2)

        pygame.draw.rect(screen, WHITE, ball.rect)
        pygame.draw.rect(screen, WHITE, left_paddle.rect)
        pygame.draw.rect(screen, WHITE, right_paddle.rect)

        score_text = font.render(f"{player_score} : {opponent_score}", True, WHITE)
        bot_text = font.render("BOT", True, WHITE)
        player_text = font.render("PLAYER", True, WHITE)

        score_x = WIDTH // 2 - score_text.get_width() // 2
        score_y = int(TOP_MARGIN * 0.5)
        bot_x = LINE_MARGIN
        bot_y = int(TOP_MARGIN * 0.5)
        player_x = WIDTH - LINE_MARGIN - player_text.get_width()
        player_y = int(TOP_MARGIN * 0.5)

        screen.blit(score_text, (score_x, score_y))
        screen.blit(bot_text, (bot_x, bot_y))
        screen.blit(player_text, (player_x, player_y))

        for y in range(game_area.top, game_area.bottom, 20):
            pygame.draw.line(screen, WHITE, (WIDTH // 2, y), (WIDTH // 2, y + 10), 2)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
