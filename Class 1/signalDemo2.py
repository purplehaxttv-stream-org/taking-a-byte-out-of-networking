import pygame

pygame.init()

WIDTH, HEIGHT = 1050, 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Signal Demo 2 - No Shared Clock")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
label_font = pygame.font.SysFont(None, 25)
small_font = pygame.font.SysFont(None, 20)
button_font = pygame.font.SysFont(None, 24)
mono_font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont(None, 36)

BYTE = ord('A')
TRUE_BITS = [(BYTE >> (7 - i)) & 1 for i in range(8)]
TRUE_PERIOD = 120          # simulated ms per bit, the sender's real, fixed rate
SIM_SCALE = 5               # real ms per simulated ms - slows it down to watchable speed
TOTAL_SIM_MS = 8 * TRUE_PERIOD

MATCHED_SAMPLE_OFFSETS = [60 + i * 120 for i in range(8)]     # agrees with the sender exactly
MISMATCHED_SAMPLE_OFFSETS = [60 + i * 100 for i in range(8)]  # ~17% faster - drifts

agree_button = pygame.Rect(WIDTH // 2 - 320, 55, 300, 44)
drift_button = pygame.Rect(WIDTH // 2 + 20, 55, 300, 44)

scope_box = pygame.Rect(250, 115, 570, 200)
sender_box = pygame.Rect(30, 130, 190, 170)
receiver_box = pygame.Rect(850, 130, 190, 170)

result_box = pygame.Rect(250, 325, 570, 90)

BG_COLOR = (20, 20, 20)
TEXT_COLOR = (230, 230, 230)
DIM_TEXT_COLOR = (150, 150, 155)
BOX_COLOR = (50, 50, 60)
SENDER_BORDER = (100, 200, 255)
RECEIVER_BORDER = (150, 220, 120)
SCOPE_BORDER = (170, 140, 220)
HIGH_COLOR = (255, 90, 70)
LOW_COLOR = (90, 130, 200)
TRACE_COLOR = (255, 220, 120)
CORRECT_COLOR = (100, 200, 120)
WRONG_COLOR = (230, 90, 80)
AGREE_BUTTON_COLOR = (90, 140, 100)
DRIFT_BUTTON_COLOR = (150, 90, 90)
BUTTON_TEXT_COLOR = (255, 255, 255)
PLAYHEAD_COLOR = (255, 255, 255)

mode = "idle"       # "idle", "playing", "done"
variant = None      # "matched" or "mismatched"
start_time = 0
samples_taken = []  # list of (sim_time, value, true_idx, assumed_idx, correct)


def draw_text_centered(surface, text, fnt, color, center):
    rendered = fnt.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(center=center))


def true_bit_at(sim_t):
    idx = int(sim_t // TRUE_PERIOD)
    if idx >= 8:
        idx = 7
    return TRUE_BITS[idx], idx


def start_run(now, chosen_variant):
    global mode, variant, start_time, samples_taken
    mode = "playing"
    variant = chosen_variant
    start_time = now
    samples_taken = []


running = True
while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mode in ("idle", "done"):
                if agree_button.collidepoint(event.pos):
                    start_run(now, "matched")
                elif drift_button.collidepoint(event.pos):
                    start_run(now, "mismatched")

    sim_elapsed = 0
    if mode == "playing":
        sim_elapsed = (now - start_time) / SIM_SCALE
        offsets = MATCHED_SAMPLE_OFFSETS if variant == "matched" else MISMATCHED_SAMPLE_OFFSETS
        while len(samples_taken) < 8 and sim_elapsed >= offsets[len(samples_taken)]:
            assumed_idx = len(samples_taken)
            sim_t = offsets[assumed_idx]
            value, true_idx = true_bit_at(sim_t)
            samples_taken.append((sim_t, value, true_idx, assumed_idx, true_idx == assumed_idx))
        if sim_elapsed >= TOTAL_SIM_MS + 80 and len(samples_taken) == 8:
            mode = "done"

    screen.fill(BG_COLOR)

    draw_text_centered(screen, "No Shared Clock", font, TEXT_COLOR, (WIDTH // 2, 25))

    can_run = mode in ("idle", "done")
    pygame.draw.rect(screen, AGREE_BUTTON_COLOR if can_run else BOX_COLOR, agree_button, border_radius=8)
    draw_text_centered(screen, "SEND - CLOCKS AGREE (120ms/bit)", button_font, BUTTON_TEXT_COLOR, agree_button.center)
    pygame.draw.rect(screen, DRIFT_BUTTON_COLOR if can_run else BOX_COLOR, drift_button, border_radius=8)
    draw_text_centered(screen, "SEND - CLOCKS DRIFT (100ms/bit)", button_font, BUTTON_TEXT_COLOR, drift_button.center)

    # sender
    pygame.draw.rect(screen, BOX_COLOR, sender_box, border_radius=10)
    pygame.draw.rect(screen, SENDER_BORDER, sender_box, width=3, border_radius=10)
    draw_text_centered(screen, "SENDER", label_font, TEXT_COLOR, (sender_box.centerx, sender_box.y + 22))
    draw_text_centered(screen, f"sending 0x{BYTE:02X} 'A'", small_font, DIM_TEXT_COLOR, (sender_box.centerx, sender_box.y + 50))
    draw_text_centered(screen, f"{TRUE_PERIOD}ms per bit", small_font, DIM_TEXT_COLOR, (sender_box.centerx, sender_box.y + 72))
    draw_text_centered(screen, "".join(str(b) for b in TRUE_BITS), mono_font, TEXT_COLOR, (sender_box.centerx, sender_box.y + 105))

    # receiver
    pygame.draw.rect(screen, BOX_COLOR, receiver_box, border_radius=10)
    pygame.draw.rect(screen, RECEIVER_BORDER, receiver_box, width=3, border_radius=10)
    draw_text_centered(screen, "RECEIVER", label_font, TEXT_COLOR, (receiver_box.centerx, receiver_box.y + 22))
    if variant:
        period_text = "120ms/bit (agreed)" if variant == "matched" else "100ms/bit (17% fast)"
        draw_text_centered(screen, period_text, small_font, DIM_TEXT_COLOR, (receiver_box.centerx, receiver_box.y + 50))
    received_str = "".join(str(v) for _, v, _, _, _ in samples_taken)
    draw_text_centered(screen, received_str if received_str else "-", mono_font, TEXT_COLOR, (receiver_box.centerx, receiver_box.y + 105))
    draw_text_centered(screen, f"{len(samples_taken)}/8 bits read", small_font, DIM_TEXT_COLOR, (receiver_box.centerx, receiver_box.y + 130))

    # scope
    pygame.draw.rect(screen, BOX_COLOR, scope_box, border_radius=8)
    pygame.draw.rect(screen, SCOPE_BORDER, scope_box, width=3, border_radius=8)
    trace_left = scope_box.x + 15
    trace_right = scope_box.right - 15
    trace_width = trace_right - trace_left
    high_y = scope_box.y + 35
    low_y = scope_box.bottom - 45

    def x_for_sim_t(t):
        return trace_left + (t / TOTAL_SIM_MS) * trace_width

    if mode != "idle":
        visible_until = min(sim_elapsed, TOTAL_SIM_MS) if mode == "playing" else TOTAL_SIM_MS
        points = []
        t = 0
        while t <= visible_until:
            val, _ = true_bit_at(t)
            points.append((x_for_sim_t(t), high_y if val else low_y))
            t += 4
        points.append((x_for_sim_t(visible_until), (high_y if true_bit_at(visible_until)[0] else low_y)))
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            pygame.draw.line(screen, TRACE_COLOR, (x1, y1), (x2, y1), 2)
            if y1 != y2:
                pygame.draw.line(screen, TRACE_COLOR, (x2, y1), (x2, y2), 2)

        for bit_i in range(1, 8):
            bx = x_for_sim_t(bit_i * TRUE_PERIOD)
            if bx <= x_for_sim_t(visible_until):
                pygame.draw.line(screen, (70, 70, 78), (bx, scope_box.y + 10), (bx, scope_box.bottom - 10), 1)

        for sim_t, value, true_idx, assumed_idx, correct in samples_taken:
            sx = x_for_sim_t(sim_t)
            sy = high_y if value else low_y
            dot_color = CORRECT_COLOR if correct else WRONG_COLOR
            pygame.draw.circle(screen, dot_color, (int(sx), int(sy)), 6)
            pygame.draw.circle(screen, (0, 0, 0), (int(sx), int(sy)), 6, width=1)

        if mode == "playing":
            px = x_for_sim_t(sim_elapsed)
            pygame.draw.line(screen, PLAYHEAD_COLOR, (px, scope_box.y + 5), (px, scope_box.bottom - 5), 2)
    else:
        draw_text_centered(screen, "click a SEND button to transmit 0x41 'A', one bit at a time",
                            small_font, DIM_TEXT_COLOR, (scope_box.centerx, scope_box.centery))

    # result
    if mode == "done":
        pygame.draw.rect(screen, BOX_COLOR, result_box, border_radius=8)
        received_bits = [v for _, v, _, _, _ in samples_taken]
        received_byte = int("".join(str(b) for b in received_bits), 2)
        correct = received_byte == BYTE
        border_col = CORRECT_COLOR if correct else WRONG_COLOR
        pygame.draw.rect(screen, border_col, result_box, width=3, border_radius=8)
        sent_text = f"SENT: 0x{BYTE:02X} '{chr(BYTE)}'"
        recv_text = f"RECEIVED: 0x{received_byte:02X} '{chr(received_byte) if 32 <= received_byte < 127 else '?'}'"
        verdict = "correct - clocks agreed" if correct else "WRONG - drifted off the true bits, silently"
        draw_text_centered(screen, f"{sent_text}    {recv_text}", big_font, TEXT_COLOR, (result_box.centerx, result_box.y + 30))
        draw_text_centered(screen, verdict, small_font, border_col, (result_box.centerx, result_box.y + 65))

    if mode == "idle":
        status = "green dots = receiver sampled the right bit. red dots = it drifted onto the wrong one."
    elif mode == "playing":
        status = "watch the playhead - the receiver samples on its OWN clock, whether or not that lines up with the sender's"
    else:
        status = "click a SEND button to replay"
    status_text = small_font.render(status, True, DIM_TEXT_COLOR)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT - 25))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
