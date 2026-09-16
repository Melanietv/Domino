import pygame
import random
import sys

pygame.init()

# --- Einstellungen ---
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Domino 4-Spieler – Fotorealistisch")

FONT = pygame.font.SysFont("arial", 24)
SMALL_FONT = pygame.font.SysFont("arial", 18)
TINY_FONT = pygame.font.SysFont("arial", 16)
BOLD_FONT = pygame.font.SysFont("arial", 26, bold=True)

STONE_W, STONE_H = 100, 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GREEN = (20, 120, 20)
DARK_GREEN = (10, 60, 10)
LIGHT_GREEN = (40, 160, 40)

PINK = (255, 105, 180)  # Rosa für Topf-Zahl

# --- Domino-Set erzeugen ---
def create_domino_set():
    return [(i, j) for i in range(7) for j in range(i, 7)]

def stone_points(stone):
    return stone[0] + stone[1]

# --- Hintergrund ---
def draw_background():
    for y in range(0, HEIGHT, 40):
        color = GREEN if (y // 40) % 2 == 0 else DARK_GREEN
        pygame.draw.rect(SCREEN, color, (0, y, WIDTH, 40))

# --- Topf ---
def draw_pot(x, y, deck_count):
    pygame.draw.ellipse(SCREEN, DARK_GREEN, (x, y, 120, 60))
    pygame.draw.ellipse(SCREEN, GREEN, (x+5, y+5, 110, 50))
    pygame.draw.ellipse(SCREEN, WHITE, (x+30, y+10, 40, 20))

    txt = BOLD_FONT.render(str(deck_count), True, PINK)
    SCREEN.blit(txt, (x + 40, y + 15))

# --- Domino-Stein ---
def draw_domino(surface, stone, x, y, selected=False):
    rect = pygame.Rect(x, y, STONE_W, STONE_H)

    pygame.draw.rect(surface, (0, 0, 0, 80), (x+4, y+4, STONE_W, STONE_H))
    pygame.draw.rect(surface, (230, 230, 230), rect, border_radius=8)
    pygame.draw.rect(surface, (200, 200, 200), rect, 3, border_radius=8)

    pygame.draw.line(surface, BLACK,
                     (rect.x + rect.w // 2, rect.y + 5),
                     (rect.x + rect.w // 2, rect.y + rect.h - 5), 3)

    def draw_pips(value, rx, ry, rw, rh):
        cx = rx + rw // 2
        cy = ry + rh // 2
        r = 6
        offset_x = 15
        offset_y = 10

        positions = {
            0: [],
            1: [(cx, cy)],
            2: [(cx - offset_x, cy - offset_y), (cx + offset_x, cy + offset_y)],
            3: [(cx - offset_x, cy - offset_y), (cx, cy), (cx + offset_x, cy + offset_y)],
            4: [(cx - offset_x, cy - offset_y), (cx + offset_x, cy - offset_y),
                (cx - offset_x, cy + offset_y), (cx + offset_x, cy + offset_y)],
            5: [(cx - offset_x, cy - offset_y), (cx + offset_x, cy - offset_y),
                (cx, cy),
                (cx - offset_x, cy + offset_y), (cx + offset_x, cy + offset_y)],
            6: [(cx - offset_x, cy - offset_y), (cx, cy - offset_y), (cx + offset_x, cy - offset_y),
                (cx - offset_x, cy + offset_y), (cx, cy + offset_y), (cx + offset_x, cy + object_y if 'object_y' in locals() else cy + offset_y)],
        }

        # Fix minor syntax typo if any inside the dict definition
        positions[6] = [(cx - offset_x, cy - offset_y), (cx, cy - offset_y), (cx + offset_x, cy - offset_y),
                        (cx - offset_x, cy + offset_y), (cx, cy + offset_y), (cx + offset_x, cy + offset_y)]

        for (px, py) in positions[value]:
            pygame.draw.circle(surface, BLACK, (px, py), r)
            pygame.draw.circle(surface, WHITE, (px-2, py-2), r//2)

    draw_pips(stone[0], rect.x, rect.y, rect.w//2, rect.h)
    draw_pips(stone[1], rect.x + rect.w//2, rect.y, rect.w//2, rect.h)

    if selected:
        pygame.draw.rect(surface, LIGHT_GREEN, rect, 3)

    return rect

# --- Popup Auswahl Links/Rechts ---
def choose_side_popup():
    popup = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 300, 160)
    left_btn = pygame.Rect(popup.x + 20, popup.y + 80, 120, 50)
    right_btn = pygame.Rect(popup.x + 160, popup.y + 80, 120, 50)

    while True:
        draw_background()
        draw_board(game)
        draw_hand(game)

        pygame.draw.rect(SCREEN, BLACK, popup)
        pygame.draw.rect(SCREEN, WHITE, popup, 2)

        txt = FONT.render("Wohin legen?", True, WHITE)
        SCREEN.blit(txt, (popup.x + 80, popup.y + 20))

        pygame.draw.rect(SCREEN, LIGHT_GREEN, left_btn)
        pygame.draw.rect(SCREEN, WHITE, left_btn, 2)
        SCREEN.blit(FONT.render("Links", True, WHITE), (left_btn.x + 20, left_btn.y + 10))

        pygame.draw.rect(SCREEN, LIGHT_GREEN, right_btn)
        pygame.draw.rect(SCREEN, WHITE, right_btn, 2)
        SCREEN.blit(FONT.render("Rechts", True, WHITE), (right_btn.x + 20, right_btn.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if left_btn.collidepoint(event.pos):
                    return "left"
                if right_btn.collidepoint(event.pos):
                    return "right"

# --- Prüfen, ob links/rechts möglich ---
def move_options(game, stone):
    if not game.board:
        return ["right"]

    left = game.board[0][0]
    right = game.board[-1][1]
    a, b = stone

    options = []
    if a == left or b == left:
        options.append("left")
    if a == right or b == right:
        options.append("right")

    return options

# --- Spieler ---
class Player:
    def __init__(self, idx):
        self.idx = idx
        self.hand = []
        self.total_win = 0

    def hand_points(self):
        return sum(stone_points(s) for s in self.hand)

# --- Spielklasse ---
class DominoGame:
    def __init__(self):
        self.jackpot = 0
        self.state = "menu"
        self.reset_round()

    def reset_round(self):
        deck = create_domino_set()
        random.shuffle(deck)

        self.players = [Player(i) for i in range(4)]
        for p in self.players:
            p.hand = [deck.pop() for _ in range(5)]

        self.deck = deck
        self.board = []
        self.current_player = 0
        self.message = "Klicke einen Stein."
        self.winner = None
        self.blocked_counter = 0

    def draw_from_deck(self, player):
        if self.deck:
            new_stone = self.deck.pop()
            player.hand.append(new_stone)
            return new_stone
        return None

    def next_player(self):
        self.current_player = (self.current_player + 1) % 4

    def check_winner(self):
        for p in self.players:
            if len(p.hand) == 0:
                return p.idx
        return None

    def handle_end(self):
        self.winner = self.check_winner()

        if self.winner is not None:
            total = sum(p.hand_points() for p in self.players if p.idx != self.winner)
            self.players[self.winner].total_win += total

            msg = f"Spieler {self.winner+1} gewinnt {total} Euro"

            if self.jackpot > 0:
                msg += f" + Jackpot {self.jackpot}"
                self.players[self.winner].total_win += self.jackpot

            self.message = msg
            self.jackpot = 0
            self.state = "game_over"
            return

        if self.blocked_counter >= 4:
            blocked_jackpot_animation(self)

# --- Darstellung der gelegten Steine ---
def draw_board(game):
    stones_per_row = 12
    x_start = 100
    y_start = 200

    for i, stone in enumerate(game.board):
        row = i // stones_per_row
        col = i % stones_per_row
        x = x_start + col * (STONE_W + 10)
        y = y_start + row * (STONE_H + 10)
        draw_domino(SCREEN, stone, x, y)

# --- Darstellung der Spielerhände ---
def draw_hand(game):
    p = game.players[game.current_player]
    x = 50
    y = HEIGHT - 120
    for stone in p.hand:
        draw_domino(SCREEN, stone, x, y)
        x += STONE_W + 10

# --- Alle Hände für Blockade anzeigen ---
def draw_all_hands(game):
    start_y = 250
    for idx, p in enumerate(game.players):
        label = SMALL_FONT.render(f"Spieler {idx+1}", True, WHITE)
        SCREEN.blit(label, (50, start_y - 30))

        x = 50
        y = start_y
        for stone in p.hand:
            draw_domino(SCREEN, stone, x, y)
            x += STONE_W + 10

        start_y += 100

# --- Gesamtgewinne rechts unten ---
def draw_total_scores(game):
    y = HEIGHT - 120
    for p in game.players:
        txt = TINY_FONT.render(f"P{p.idx+1}: {p.total_win}€", True, WHITE)
        SCREEN.blit(txt, (WIDTH - 150, y))
        y += 20

# --- Jackpotanzeige ---
def draw_jackpot(game):
    txt = BOLD_FONT.render(f"Jackpot: {game.jackpot}€", True, WHITE)
    SCREEN.blit(txt, (WIDTH//2 - txt.get_width()//2, 10))

# --- Blockade-Animation: Punkte wandern in den Jackpot ---
def blocked_jackpot_animation(game):
    clock = pygame.time.Clock()

    # Punkte jedes Spielers berechnen
    player_points = [p.hand_points() for p in game.players]
    total_points = sum(player_points)

    # Schritt 1: alle Hände anzeigen
    for _ in range(60):
        clock.tick(60)
        draw_background()
        draw_board(game)
        draw_all_hands(game)
        draw_jackpot(game)
        info = FONT.render("Blockiert! Alle Punkte wandern in den Jackpot...", True, WHITE)
        SCREEN.blit(info, (50, 200))
        pygame.display.flip()

    # Schritt 2: einfache „Flug“-Animation der Punkte zum Topf
    pot_x, pot_y = WIDTH - 180 + 60, 20 + 30  # Mitte des Topfes
    start_positions = []
    current_y = 250
    for idx, pts in enumerate(player_points):
        start_positions.append((100, current_y - 10))
        current_y += 100

    steps = 60
    for step in range(steps):
        clock.tick(60)
        draw_background()
        draw_board(game)
        draw_all_hands(game)
        draw_jackpot(game)

        for i, pts in enumerate(player_points):
            sx, sy = start_positions[i]
            t = step / steps
            x = sx + (pot_x - sx) * t
            y = sy + (pot_y - sy) * t
            txt = SMALL_FONT.render(f"{pts} Punkte", True, WHITE)
            SCREEN.blit(txt, (x, y))

        info = FONT.render("Punkte fliegen in den Jackpot...", True, WHITE)
        SCREEN.blit(info, (50, 200))

        pygame.display.flip()

    # Schritt 3: Jackpot erhöhen und Hände bleiben sichtbar
    game.jackpot += total_points
    game.message = f"Blockiert! {total_points} Punkte im Jackpot."
    game.state = "game_over"

# --- Hauptloop ---
def main():
    global game
    clock = pygame.time.Clock()
    game = DominoGame()

    while True:
        clock.tick(60)

        if game.state == "menu":
            draw_background()

            title = FONT.render("Domino 4-Spieler – Fotorealistisch", True, WHITE)
            SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 150))

            draw_jackpot(game)

            btn = pygame.Rect(WIDTH//2 - 150, 300, 300, 60)
            pygame.draw.rect(SCREEN, LIGHT_GREEN, btn)
            pygame.draw.rect(SCREEN, WHITE, btn, 2)

            txt = FONT.render("Neue Runde starten", True, WHITE)
            SCREEN.blit(txt, (btn.x + 60, btn.y + 15))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn.collidepoint(event.pos):
                        game.reset_round()
                        game.state = "playing"

        elif game.state == "playing":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    p = game.players[game.current_player]

                    x = 50
                    y = HEIGHT - 120
                    clicked = None

                    for i, stone in enumerate(p.hand):
                        rect = pygame.Rect(x, y, STONE_W, STONE_H)
                        if rect.collidepoint(mx, my):
                            clicked = i
                            break
                        x += STONE_W + 10

                    if clicked is not None:
                        stone = p.hand[clicked]
                        pos = (50 + clicked * (STONE_W + 10), HEIGHT - 120)

                        options = move_options(game, stone)

                        if len(options) == 0:
                            # Kein Stein passt → automatisch ziehen
                            new_stone = game.draw_from_deck(p)

                            if new_stone is None:
                                game.message = "Kein Stein passt – Topf leer!"
                                game.blocked_counter += 1
                                game.handle_end()
                                if game.state == "playing":
                                    game.next_player()
                            else:
                                game.message = "Kein Stein passt – ziehe aus dem Topf!"
                                new_options = move_options(game, new_stone)

                                if len(new_options) == 0:
                                    game.message = "Neuer Stein passt auch nicht."
                                    game.blocked_counter += 1
                                    game.handle_end()
                                    if game.state == "playing":
                                        game.next_player()
                                else:
                                    # neuen Stein automatisch anlegen
                                    chosen = new_options[0]
                                    a, b = new_stone

                                    row = len(game.board) // 12
                                    col = len(game.board) % 12
                                    end_pos = (100 + col * (STONE_W + 10),
                                               200 + row * (STONE_H + 10))

                                    if chosen == "left":
                                        left = game.board[0][0] if game.board else None
                                        if b == left:
                                            game.board.insert(0, (a, b))
                                        else:
                                            game.board.insert(0, (b, a))
                                    else:
                                        right = game.board[-1][1] if game.board else None
                                        if a == right:
                                            game.board.append((a, b))
                                        else:
                                            game.board.append((b, a))

                                    p.hand.remove(new_stone)
                                    game.blocked_counter = 0
                                    game.handle_end()
                                    if game.state == "playing":
                                        game.next_player()

                        else:
                            # Stein passt → normal legen
                            if len(options) == 1:
                                chosen = options[0]
                            else:
                                chosen = choose_side_popup()

                            row = len(game.board) // 12
                            col = len(game.board) % 12
                            end_pos = (100 + col * (STONE_W + 10),
                                       200 + row * (STONE_H + 10))

                            a, b = stone

                            if chosen == "left":
                                left = game.board[0][0] if game.board else None
                                if b == left:
                                    game.board.insert(0, (a, b))
                                else:
                                    game.board.insert(0, (b, a))
                            else:
                                right = game.board[-1][1] if game.board else None
                                if a == right:
                                    game.board.append((a, b))
                                else:
                                    game.board.append((b, a))

                            p.hand.pop(clicked)
                            game.blocked_counter = 0
                            game.handle_end()

                            if game.state == "playing":
                                game.next_player()

            draw_background()
            draw_board(game)
            draw_hand(game)

            turn_text = FONT.render(f"Spieler {game.current_player+1} ist dran", True, WHITE)
            SCREEN.blit(turn_text, (50, 50))

            draw_pot(WIDTH - 180, 20, len(game.deck))

            msg = FONT.render(game.message, True, WHITE)
            SCREEN.blit(msg, (50, 90))

            draw_total_scores(game)
            draw_jackpot(game)

            pygame.display.flip()

        elif game.state == "game_over":
            draw_background()

            draw_board(game)
            draw_all_hands(game)
            draw_jackpot(game)

            msg = FONT.render(game.message, True, WHITE)
            SCREEN.blit(msg, (50, 50))

            btn = pygame.Rect(WIDTH//2 - 150, HEIGHT - 100, 300, 60)
            pygame.draw.rect(SCREEN, LIGHT_GREEN, btn)
            pygame.draw.rect(SCREEN, WHITE, btn, 2)

            txt = FONT.render("Zurück ins Menü", True, WHITE)
            SCREEN.blit(txt, (btn.x + 60, btn.y + 15))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn.collidepoint(event.pos):
                        game.state = "menu"

if __name__ == "__main__":
    main()