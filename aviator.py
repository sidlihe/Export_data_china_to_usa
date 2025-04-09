import pygame
import random
import math
import time
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 177, 76)
RED = (200, 0, 0)
GRAY = (120, 120, 120)
YELLOW = (255, 215, 0)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aviator Crash Game")

# Fonts
FONT = pygame.font.SysFont("Arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 24)
COUNTDOWN_FONT = pygame.font.SysFont("Arial", 32, bold=True)

# Assets
plane_img = pygame.image.load("plane.jpg")
plane_img = pygame.transform.scale(plane_img, (60, 60))

FPS = 60
clock = pygame.time.Clock()

# Button Class
class Button:
    def __init__(self, x, y, w, h, text, amount=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.amount = amount

    def draw(self, surface, active=True):
        color = GREEN if active else GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        txt = SMALL_FONT.render(self.text, True, BLACK)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# Helper Functions
def draw_center_text(text, font, color, y_offset=0):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    win.blit(txt, rect)

def draw_input_box(surface, rect, text, active):
    color = GREEN if active else WHITE
    pygame.draw.rect(surface, color, rect, 2)
    txt_surface = SMALL_FONT.render(text, True, WHITE)
    surface.blit(txt_surface, (rect.x + 5, rect.y + 5))

def calculate_crash_point():
    # 50% chance to crash between 1.00 and 2.00
    if random.random() < 0.5:
        return round(random.uniform(1.00, 2.00), 2)
    # 10% chance to crash at 1.00-1.01
    elif random.random() < 0.1:
        return round(random.uniform(1.00, 1.01), 2)
    # otherwise normal crash
    return round(random.uniform(2.0, 6.0), 2)

# Main Function
def main():
    global crashed
    x, y = 100, HEIGHT // 2
    multiplier = 1.00
    t = 0
    crashed = False
    cashed_out = False
    player_joined = False
    result_text = ""
    crashed_at = None
    countdown_time = 7  # Wait 7 seconds before flight
    countdown_start = time.time()
    crash_point = calculate_crash_point()
    cash_in_amount = ""
    input_active = False
    winnings = 0
    bet_entered = False
    try_next = False

    input_box = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 140, 120, 40)
    cash_out_button = Button(WIDTH // 2 - 60, HEIGHT - 80, 120, 50, "CASH OUT")

    preset_buttons = [
        Button(100, HEIGHT - 140, 80, 40, "₹10", 10),
        Button(200, HEIGHT - 140, 80, 40, "₹50", 50),
        Button(300, HEIGHT - 140, 80, 40, "₹100", 100),
        Button(400, HEIGHT - 140, 80, 40, "₹1000", 1000),
    ]

    run = True
    while run:
        clock.tick(FPS)
        current_time = time.time()
        countdown_left = max(0, int(countdown_time - (current_time - countdown_start)))
        plane_flying = countdown_left <= 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                if not plane_flying:
                    if not bet_entered:
                        for btn in preset_buttons:
                            if btn.clicked(event.pos):
                                cash_in_amount = str(btn.amount)
                                bet_entered = True
                                result_text = f"✅ Bet ₹{cash_in_amount} placed!"
                                break
                    else:
                        try_next = True
                else:
                    if cash_out_button.clicked(event.pos) and player_joined and not cashed_out and not crashed:
                        cashed_out = True
                        winnings = float(cash_in_amount) * multiplier
                        result_text = f"✅ Cashed out at {multiplier:.2f}x — ₹{winnings:.2f}"

            elif event.type == pygame.KEYDOWN:
                if input_active and not bet_entered:
                    if event.key == pygame.K_BACKSPACE:
                        cash_in_amount = cash_in_amount[:-1]
                    elif event.unicode.isdigit():
                        cash_in_amount += event.unicode
                    elif event.key == pygame.K_RETURN and cash_in_amount:
                        bet_entered = True
                        result_text = f"✅ Bet ₹{cash_in_amount} placed!"

        # Fly Plane
        if plane_flying and not crashed:
            if not player_joined and bet_entered:
                player_joined = True

            multiplier += 0.008 * math.exp(t * 0.005)
            x += 3  # Reduced speed
            y = HEIGHT // 2 - math.log(multiplier) * 45
            y = max(50, min(y, HEIGHT - 100))
            t += 1

            if multiplier >= crash_point:
                crashed = True
                if player_joined and not cashed_out:
                    result_text = f"💥 Crashed at {multiplier:.2f}x — You lost!"
                elif player_joined and cashed_out:
                    result_text += f" | Crashed at {multiplier:.2f}x"

        # Reset After Crash
        if crashed:
            draw_center_text("💥 Plane Crashed", COUNTDOWN_FONT, RED, y_offset=-140)
            draw_center_text("🕒 Starting new round in 7s", SMALL_FONT, YELLOW, y_offset=140)
            pygame.display.update()
            time.sleep(7)
            # Reset all state
            x, y = 100, HEIGHT // 2
            multiplier = 1.00
            t = 0
            crashed = False
            cashed_out = False
            player_joined = False
            result_text = ""
            crashed_at = None
            crash_point = calculate_crash_point()
            countdown_start = time.time()
            cash_in_amount = ""
            input_active = False
            winnings = 0
            bet_entered = False
            try_next = False

        # Drawing
        win.fill(BLACK)
        mult_color = RED if crashed else WHITE
        mult_text = FONT.render(f"{multiplier:.2f}x", True, mult_color)
        win.blit(mult_text, (WIDTH // 2 - 70, 30))

        if not crashed:
            win.blit(plane_img, (x, y))

        if result_text:
            draw_center_text(result_text, SMALL_FONT, GREEN if "Cashed" in result_text else RED, y_offset=-100)

        if countdown_left > 0:
            draw_center_text(f"💸 Place Your Bet! {countdown_left}s", COUNTDOWN_FONT, YELLOW, y_offset=-60)

        if not bet_entered and not plane_flying:
            for btn in preset_buttons:
                btn.draw(win)
            draw_input_box(win, input_box, cash_in_amount or "Enter your bet", input_active)

        if try_next:
            draw_center_text("❌ You can't bet now! Try next round", SMALL_FONT, RED, y_offset=200)

        if player_joined and not crashed and not cashed_out and plane_flying:
            cash_out_button.draw(win)

        pygame.display.update()

if __name__ == "__main__":
    main()
