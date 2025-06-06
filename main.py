

#video
# main.py (Integrated: Video + Game)
import pygame
import threading
import json
import sys
import os
from ffpyplayer.player import MediaPlayer
from tts_engine import speak, stop_tts
from voice_listener import listen

# ------------------ VIDEO INTRO FUNCTION ------------------
def play_video(video_path):
    is_playing = True
    video_speed = 1.0
    screen_width, screen_height = 1000, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    player = MediaPlayer(video_path)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if is_playing:
            frame, val = player.get_frame()
            if val == 'eof':
                return  # Exit video on finish

            if frame is not None:
                img, t = frame
                frame_surface = pygame.image.frombuffer(img.to_bytearray()[0], img.get_size(), "RGB")
                frame_surface = pygame.transform.scale(frame_surface, (800, 450))
                screen.fill((0, 0, 0))
                screen.blit(frame_surface, (100, 75))  # Centered
        pygame.display.flip()
        clock.tick(30 * video_speed)

# ------------------ GAME CODE ------------------
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 600
WHITE = (255, 255, 255)
PURPLE = (80, 0, 130)
YELLOW = (255, 204, 0)
BLACK = (0, 0, 0)
FPS = 60
FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 28, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎧 KBC Quiz Game")
clock = pygame.time.Clock()

bg_image = pygame.image.load("./assets/kbc_background.jpg")
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

with open("questions.json", "r", encoding='utf-8') as f:
    questions = json.load(f)

current_question = 0
user_result = ""
running = True

question_rect = pygame.Rect(50, 400, 900, 60)
option_rects = [
    pygame.Rect(50, 470, 430, 40),
    pygame.Rect(520, 470, 430, 40),
    pygame.Rect(50, 520, 430, 40),
    pygame.Rect(520, 520, 430, 40)
]

repeat_btn = pygame.Rect(50, 20, 100, 40)
answer_btn = pygame.Rect(170, 20, 100, 40)
next_btn = pygame.Rect(290, 20, 100, 40)
exit_btn = pygame.Rect(850, 20, 100, 40)

levels = [
    "₹1,000", "₹2,000", "₹3,000", "₹5,000", "₹10,000",
    "₹20,000", "₹40,000", "₹80,000", "₹1,60,000", "₹3,20,000",
    "₹6,40,000", "₹12,50,000", "₹25,00,000", "₹50,00,000", "₹1,00,00,000"
][::-1]

level_box = pygame.Rect(WIDTH - 160, 60, 150, 30 * len(levels))


def draw_text(surface, text, pos, font, color):
    rendered = font.render(text, True, color)
    surface.blit(rendered, pos)


def speak_question():
    q = questions[current_question]
    speak(q["question"])
    for i, opt in enumerate(q["options"]):
        speak(f"Option {chr(65 + i)}: {opt}")


def ask_question():
    threading.Thread(target=speak_question, daemon=True).start()


def listen_answer():
    global user_result, current_question
    response = listen().strip().lower()
    answer = questions[current_question]['answer'].strip().lower()
    opts = questions[current_question]['options']

    letter_to_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    selected_text = response

    if response in letter_to_index:
        selected_text = opts[letter_to_index[response]].strip().lower()
    else:
        for opt in opts:
            if response in opt.lower() or opt.lower() in response:
                selected_text = opt.strip().lower()
                break

    if selected_text == answer or answer in selected_text:
        user_result = "✅ Correct!"
        speak("Correct answer!")
        current_question += 1
        if current_question >= len(questions):
            speak("Game Over. Thanks for playing.")
            current_question = 0
        threading.Thread(target=ask_question, daemon=True).start()
    else:
        user_result = f"❌ Wrong! Correct: {answer}"
        speak(f"Wrong answer. Correct was {answer}.")


def draw_levels():
    pygame.draw.rect(screen, (30, 30, 30), level_box, border_radius=10)
    for i, prize in enumerate(levels):
        color = YELLOW if len(levels) - 1 - i == current_question else WHITE
        draw_text(screen, prize, (WIDTH - 150, 65 + i * 30), FONT, color)


def draw_button(rect, text, active=False):
    color = (255, 255, 150) if active else YELLOW
    pygame.draw.rect(screen, color, rect, border_radius=8)
    draw_text(screen, text, (rect.x + 10, rect.y + 10), FONT, BLACK)


def draw_ui():
    screen.blit(bg_image, (0, 0))
    pygame.draw.rect(screen, PURPLE, question_rect, border_radius=10)
    draw_text(screen, questions[current_question]["question"], (60, 415), FONT, WHITE)

    for i, rect in enumerate(option_rects):
        pygame.draw.rect(screen, PURPLE, rect, border_radius=10)
        draw_text(screen, f"{chr(65 + i)}. {questions[current_question]['options'][i]}", (rect.x + 10, rect.y + 10), FONT, WHITE)

    draw_button(repeat_btn, "Repeat")
    draw_button(answer_btn, "Answer")
    draw_button(next_btn, "Next")
    draw_button(exit_btn, "Exit")

    draw_text(screen, user_result, (450, 30), BIG_FONT, YELLOW)
    draw_levels()

# ---------------------- RUN APP ----------------------

# Step 1: Show intro video
play_video("./assets/KBC1080.mp4")

# Step 2: Start game
ask_question()

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            stop_tts()
            break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if repeat_btn.collidepoint(event.pos):
                ask_question()
            elif answer_btn.collidepoint(event.pos):
                threading.Thread(target=listen_answer, daemon=True).start()
            elif next_btn.collidepoint(event.pos):
                current_question += 1
                user_result = ""
                if current_question >= len(questions):
                    speak("Game Over. Thanks for playing.")
                    current_question = 0
                ask_question()
            elif exit_btn.collidepoint(event.pos):
                running = False
                stop_tts()
                break

    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()
