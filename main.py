import pygame
import random
import math
import array

pygame.init()

try:
    pygame.mixer.init(
        frequency=44100,
        size=-16,
        channels=1,
        buffer=512
    )
    SOUND_AVAILABLE = True
except pygame.error:
    SOUND_AVAILABLE = False

WIDTH, HEIGHT = 1280, 720

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.SCALED | pygame.FULLSCREEN
)

pygame.display.set_caption("Word Jumble Deluxe")
clock = pygame.time.Clock()

BG = (7, 12, 42)
PANEL = (16, 29, 75)
PANEL2 = (28, 48, 112)
WHITE = (255, 255, 255)
LIGHT = (190, 215, 255)
BLUE = (45, 145, 255)
CYAN = (40, 225, 255)
GREEN = (55, 230, 120)
RED = (255, 65, 95)
YELLOW = (255, 210, 55)
ORANGE = (255, 135, 45)
PURPLE = (180, 80, 255)
DARK = (10, 15, 40)

TITLE = pygame.font.Font(None, 92)
LOGO = pygame.font.Font(None, 104)
BIG = pygame.font.Font(None, 54)
FONT = pygame.font.Font(None, 34)
SMALL = pygame.font.Font(None, 26)
TINY = pygame.font.Font(None, 21)

WORDS = {
    "python": "A popular programming language",
    "computer": "An electronic machine",
    "keyboard": "Used for typing",
    "college": "A place where students study",
    "internet": "A global computer network",
    "science": "Study of the natural world",
    "database": "Used to store organized information",
    "program": "Instructions given to a computer",
    "technology": "Use of scientific knowledge",
    "education": "The process of learning",
    "algorithm": "A step-by-step problem-solving method",
    "developer": "A person who creates software",
    "function": "A reusable block of code",
    "variable": "A named storage location",
    "network": "Connected computers sharing data"
}


def make_sound(frequencies, duration=0.3, volume=0.22):
    if not SOUND_AVAILABLE:
        return None

    sample_rate = 44100
    total = int(sample_rate * duration)
    samples = array.array("h")

    for i in range(total):
        t = i / sample_rate
        position = i / max(1, total - 1)

        index = min(
            int(position * len(frequencies)),
            len(frequencies) - 1
        )

        frequency = frequencies[index]

        fade_in = min(1.0, t / 0.025)
        fade_out = min(1.0, max(0.0, (duration - t) / 0.04))
        envelope = fade_in * fade_out

        value = int(
            32767 * volume * envelope
            * math.sin(2 * math.pi * frequency * t)
        )

        samples.append(value)

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


SOUNDS = {
    "click": make_sound([500, 700], 0.08),
    "correct": make_sound([520, 660, 800, 1000, 1250], 0.42),
    "wrong": make_sound([360, 290, 220, 170], 0.30),
    "hint": make_sound([650, 850, 1050], 0.22),
    "finish": make_sound([700, 600, 500, 400], 0.42)
}

state = "menu"
score = 0
round_number = 0
MAX_ROUNDS = 5
attempts = 3

word = ""
jumbled = ""
guess = ""
hint = ""
hint_used = False

message = ""
message_color = WHITE
message_timer = 0.0
transition_timer = 0.0

sound_enabled = SOUND_AVAILABLE
particles = []
stars = []

for _ in range(100):
    stars.append([
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.randint(1, 3),
        random.uniform(8, 30)
    ])


def play_sound(name):
    if sound_enabled and SOUNDS.get(name) is not None:
        SOUNDS[name].play()


def draw_text(value, font, color, x, y, center=True):
    image = font.render(str(value), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))

    screen.blit(image, rect)


def rounded(rect, color, radius=18, border=0, border_color=WHITE):
    pygame.draw.rect(screen, color, rect, border_radius=radius)

    if border:
        pygame.draw.rect(
            screen,
            border_color,
            rect,
            border,
            border_radius=radius
        )


def draw_background():
    for y in range(HEIGHT):
        ratio = y / HEIGHT

        color = (
            int(5 + ratio * 8),
            int(10 + ratio * 12),
            int(34 + ratio * 30)
        )

        pygame.draw.line(
            screen,
            color,
            (0, y),
            (WIDTH, y)
        )

    elapsed = pygame.time.get_ticks() / 1000.0

    for i, (x, y, size, speed) in enumerate(stars):
        sy = int((y + elapsed * speed) % HEIGHT)
        brightness = int(165 + 75 * math.sin(elapsed * 2 + i))

        pygame.draw.circle(
            screen,
            (brightness, brightness, 255),
            (x, sy),
            size
        )


def add_particles(x, y, color, amount=35):
    for _ in range(amount):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(70, 280)

        particles.append([
            float(x),
            float(y),
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            random.uniform(0.45, 1.15),
            color,
            random.randint(2, 5)
        ])


def update_particles(dt):
    for particle in particles[:]:
        particle[0] += particle[2] * dt
        particle[1] += particle[3] * dt
        particle[3] += 260 * dt
        particle[4] -= dt

        if particle[4] <= 0:
            particles.remove(particle)


def draw_particles():
    for x, y, vx, vy, life, color, size in particles:
        pygame.draw.circle(
            screen,
            color,
            (int(x), int(y)),
            size
        )


def draw_button(label, rect, color, hover_color):
    active = rect.collidepoint(pygame.mouse.get_pos())

    if active:
        rounded(rect.inflate(8, 8), WHITE, 17)

    rounded(
        rect,
        hover_color if active else color,
        15
    )

    draw_text(
        label,
        FONT,
        WHITE,
        rect.centerx,
        rect.centery
    )

    return rect


def draw_face(x, y, happy=True, radius=27):
    pygame.draw.circle(screen, YELLOW, (x, y), radius)

    pygame.draw.circle(
        screen, DARK, (x - 9, y - 5), 3
    )
    pygame.draw.circle(
        screen, DARK, (x + 9, y - 5), 3
    )

    mouth = pygame.Rect(
        x - 12,
        y + (0 if happy else 8),
        24,
        15
    )

    if happy:
        pygame.draw.arc(
            screen, DARK, mouth, math.pi, math.tau, 3
        )
    else:
        pygame.draw.arc(
            screen, DARK, mouth, 0, math.pi, 3
        )


def draw_character(x, y):
    pygame.draw.circle(
        screen, (65, 40, 30), (x, y - 30), 39
    )
    pygame.draw.circle(
        screen, (255, 205, 155), (x, y), 33
    )
    pygame.draw.circle(
        screen, (55, 35, 25), (x - 15, y - 25), 19
    )
    pygame.draw.circle(
        screen, (55, 35, 25), (x + 8, y - 27), 20
    )

    pygame.draw.circle(screen, DARK, (x - 10, y - 1), 3)
    pygame.draw.circle(screen, DARK, (x + 10, y - 1), 3)

    pygame.draw.arc(
        screen,
        DARK,
        (x - 14, y + 1, 28, 19),
        math.pi,
        math.tau,
        3
    )

    pygame.draw.rect(
        screen,
        ORANGE,
        (x - 31, y + 30, 62, 74),
        border_radius=16
    )

    pygame.draw.line(
        screen,
        (255, 205, 155),
        (x + 25, y + 44),
        (x + 50, y + 12),
        12
    )

    pygame.draw.circle(
        screen, (255, 205, 155), (x + 52, y + 10), 10
    )


def draw_books():
    books = [
        ("PYTHON", BLUE),
        ("CODING", RED),
        ("DREAMS", GREEN)
    ]

    for i, (label, color) in enumerate(books):
        rect = pygame.Rect(18, 495 - i * 43, 155, 36)

        rounded(rect, color, 7)

        draw_text(
            label, TINY, WHITE,
            rect.centerx, rect.centery
        )


def scramble_word(value):
    letters = list(value)

    for _ in range(20):
        random.shuffle(letters)
        result = "".join(letters)

        if result != value:
            return result

    return result


def start_round():
    global word, jumbled, guess, attempts
    global hint, hint_used, message, round_number

    word = random.choice(list(WORDS.keys()))
    jumbled = scramble_word(word)

    guess = ""
    attempts = 3
    hint = ""
    hint_used = False
    message = ""

    round_number += 1


def start_game():
    global state, score, round_number, transition_timer

    state = "game"
    score = 0
    round_number = 0
    transition_timer = 0

    start_round()


def notify(value, color=WHITE, duration=1.1):
    global message, message_color, message_timer

    message = value
    message_color = color
    message_timer = duration


def submit_answer():
    global score, attempts, transition_timer

    if transition_timer > 0:
        return

    if not guess.strip():
        notify("TYPE YOUR ANSWER FIRST!", YELLOW)
        play_sound("click")
        return

    if guess.strip().lower() == word:
        score += 5 if hint_used else 10

        play_sound("correct")

        add_particles(
            WIDTH // 2, 270, GREEN, 55
        )
        add_particles(
            WIDTH // 2, 270, YELLOW, 35
        )

        notify("CORRECT! GREAT JOB!", GREEN, 1.2)
        transition_timer = 1.2

    else:
        attempts -= 1

        play_sound("wrong")
        add_particles(
            WIDTH // 2, 270, RED, 25
        )

        if attempts > 0:
            notify("OOPS! TRY AGAIN!", RED, 1.0)
        else:
            notify("ANSWER: " + word.upper(), RED, 1.4)
            transition_timer = 1.4


def draw_menu():
    draw_background()

    draw_text("WORD", LOGO, ORANGE, WIDTH // 2, 115)
    draw_text("JUMBLE", LOGO, CYAN, WIDTH // 2, 205)

    draw_text(
        "UNSCRAMBLE  •  GUESS  •  WIN",
        SMALL, WHITE, WIDTH // 2, 260
    )

    panel = pygame.Rect(
        WIDTH // 2 - 320, 300, 640, 235
    )

    rounded(panel, PANEL, 28, 3, BLUE)

    draw_text(
        "THINK  •  SOLVE  •  WIN!",
        BIG, YELLOW, WIDTH // 2, 345
    )

    draw_text(
        "15+ Words", SMALL, WHITE,
        WIDTH // 2 - 190, 400
    )
    draw_text(
        "5 Rounds", SMALL, WHITE,
        WIDTH // 2, 400
    )
    draw_text(
        "3 Attempts", SMALL, WHITE,
        WIDTH // 2 + 190, 400
    )

    draw_text(
        "Hints  •  Score  •  Fireworks",
        SMALL, LIGHT, WIDTH // 2, 445
    )

    play_rect = pygame.Rect(
        WIDTH // 2 - 145, 475, 290, 62
    )

    draw_button(
        "PLAY NOW",
        play_rect,
        GREEN,
        (100, 255, 160)
    )

    draw_face(175, 350, True, 35)
    draw_character(WIDTH - 150, 430)

    return play_rect


def draw_game():
    draw_background()

    left = pygame.Rect(25, 22, 300, 62)
    rounded(left, PANEL, 30, 2, BLUE)

    draw_text(
        f"ROUND {round_number} / {MAX_ROUNDS}",
        FONT, WHITE, left.centerx, left.centery
    )

    right = pygame.Rect(
        WIDTH - 330, 22, 300, 62
    )

    rounded(right, PANEL, 30, 2, YELLOW)

    draw_text(
        f"SCORE: {score}",
        FONT, YELLOW, right.centerx, right.centery
    )

    panel = pygame.Rect(65, 110, 850, 510)
    rounded(panel, PANEL, 28, 3, BLUE)

    draw_text(
        "UNSCRAMBLE THIS WORD",
        BIG, WHITE, 490, 158
    )

    word_rect = pygame.Rect(145, 205, 690, 90)
    rounded(word_rect, PANEL2, 20, 2, CYAN)

    draw_text(
        jumbled.upper(),
        LOGO, YELLOW, 490, 250
    )

    input_rect = pygame.Rect(170, 320, 640, 62)
    rounded(input_rect, WHITE, 14)

    draw_text(
        guess.upper() if guess else "Type your answer...",
        FONT,
        DARK if guess else (125, 135, 160),
        input_rect.centerx,
        input_rect.centery
    )

    draw_text(
        "ATTEMPTS LEFT",
        SMALL, WHITE, 400, 420
    )

    for i in range(3):
        draw_face(
            535 + i * 43,
            420,
            i < attempts,
            15
        )

    submit_rect = pygame.Rect(175, 460, 260, 60)
    hint_rect = pygame.Rect(490, 460, 260, 60)
    end_rect = pygame.Rect(320, 540, 300, 48)

    draw_button(
        "SUBMIT", submit_rect,
        GREEN, (100, 255, 160)
    )

    draw_button(
        "HINT", hint_rect,
        BLUE, (100, 185, 255)
    )

    draw_button(
        "END GAME", end_rect,
        RED, (255, 105, 125)
    )

    hint_card = pygame.Rect(945, 135, 290, 255)
    rounded(hint_card, (35, 35, 85), 22, 2, YELLOW)

    draw_text(
        "HINT CARD",
        BIG, YELLOW,
        hint_card.centerx, 180
    )

    if hint:
        lines = [
            hint[i:i + 23]
            for i in range(0, len(hint), 23)
        ]
    else:
        lines = [
            "Need help?",
            "Press the HINT",
            "button to reveal",
            "a clue!"
        ]

    for i, line in enumerate(lines[:5]):
        draw_text(
            line, SMALL, WHITE,
            hint_card.centerx, 235 + i * 30
        )

    draw_books()
    draw_character(1090, 515)

    if message:
        reaction = pygame.Rect(240, 605, 610, 50)
        rounded(
            reaction, (20, 35, 80),
            14, 2, message_color
        )

        draw_text(
            message, SMALL, message_color,
            reaction.centerx, reaction.centery
        )

    return submit_rect, hint_rect, end_rect


def draw_game_over():
    draw_background()

    draw_text(
        "GAME COMPLETE!",
        TITLE, YELLOW, WIDTH // 2, 160
    )

    panel = pygame.Rect(
        WIDTH // 2 - 300, 215, 600, 300
    )

    rounded(panel, PANEL, 28, 3, PURPLE)

    draw_text(
        "FINAL SCORE",
        BIG, WHITE, WIDTH // 2, 270
    )

    draw_text(
        str(score),
        LOGO, YELLOW, WIDTH // 2, 350
    )

    draw_text(
        f"You completed {round_number} rounds!",
        SMALL, GREEN, WIDTH // 2, 420
    )

    draw_face(WIDTH // 2 - 180, 465, True)
    draw_face(WIDTH // 2 + 180, 465, True)

    again_rect = pygame.Rect(
        WIDTH // 2 - 220, 565, 200, 60
    )

    exit_rect = pygame.Rect(
        WIDTH // 2 + 20, 565, 200, 60
    )

    draw_button(
        "PLAY AGAIN",
        again_rect,
        GREEN,
        (100, 255, 160)
    )

    draw_button(
        "EXIT",
        exit_rect,
        RED,
        (255, 105, 125)
    )

    return again_rect, exit_rect


running = True

while running:
    dt = clock.tick(60) / 1000.0

    update_particles(dt)

    if message_timer > 0:
        message_timer -= dt

        if message_timer <= 0 and transition_timer <= 0:
            message = ""

    if transition_timer > 0:
        transition_timer -= dt

        if transition_timer <= 0 and state == "game":
            if round_number >= MAX_ROUNDS:
                state = "gameover"
                play_sound("finish")
            else:
                start_round()

    if state == "menu":
        play_rect = draw_menu()

    elif state == "game":
        submit_rect, hint_rect, end_rect = draw_game()

    else:
        again_rect, exit_rect = draw_game_over()

    draw_particles()
    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif state == "game" and transition_timer <= 0:

                if event.key == pygame.K_BACKSPACE:
                    guess = guess[:-1]

                elif event.key == pygame.K_RETURN:
                    submit_answer()

                elif event.unicode.isalpha():
                    guess += event.unicode

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            if state == "menu":

                if play_rect.collidepoint(event.pos):
                    play_sound("click")
                    start_game()

            elif state == "game":

                if transition_timer > 0:
                    continue

                if submit_rect.collidepoint(event.pos):
                    play_sound("click")
                    submit_answer()

                elif hint_rect.collidepoint(event.pos):
                    hint = WORDS[word]
                    hint_used = True
                    play_sound("hint")
                    notify("HINT UNLOCKED!", YELLOW)

                elif end_rect.collidepoint(event.pos):
                    state = "gameover"
                    play_sound("finish")

            elif state == "gameover":

                if again_rect.collidepoint(event.pos):
                    play_sound("click")
                    start_game()

                elif exit_rect.collidepoint(event.pos):
                    running = False

pygame.quit()