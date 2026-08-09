import pygame

pygame.init()

WIDTH, HEIGHT = 1100, 520

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Signal Demo 3 - Framing")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
label_font = pygame.font.SysFont(None, 25)
small_font = pygame.font.SysFont(None, 19)
button_font = pygame.font.SysFont(None, 24)
mono_font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont(None, 34)

BYTE1, BYTE2 = ord('H'), ord('i')


def bits_of(b):
    return [(b >> (7 - i)) & 1 for i in range(8)]


B1, B2 = bits_of(BYTE1), bits_of(BYTE2)

# RAW: one accidental noise bit lands between the two bytes - the receiver has
# no way to know it's there, and blindly keeps grouping every 8 bits
RAW_STREAM = B1 + [0] + B2
RAW_CHUNK_BOUNDARIES = [0, 8, 16]  # naive fixed 8-bit grouping, blind to the glitch

# FRAMED: same two bytes, each properly framed, plus the exact same noise bit
# during an idle stretch between them
FRAMED_STREAM = [1, 1, 0] + B1 + [1] + [1, 0, 1] + [1, 0] + B2 + [1] + [1]


def decode_framed(stream):
    events = []
    i = 0
    while i < len(stream):
        if stream[i] == 0 and (i == 0 or stream[i - 1] == 1):
            if i + 9 < len(stream):
                data = stream[i + 1:i + 9]
                stop = stream[i + 9]
                if stop == 1:
                    val = int("".join(map(str, data)), 2)
                    events.append({"bit": i, "kind": "frame", "value": val})
                    i += 10
                    continue
                else:
                    events.append({"bit": i, "kind": "rejected"})
        i += 1
    return events


FRAMED_EVENTS = decode_framed(FRAMED_STREAM)

TRUE_PERIOD = 90   # simulated ms per bit
SIM_SCALE = 4      # real ms per simulated ms

raw_button = pygame.Rect(WIDTH // 2 - 330, 55, 310, 44)
framed_button = pygame.Rect(WIDTH // 2 + 20, 55, 310, 44)

sender_box = pygame.Rect(30, 130, 190, 160)
scope_box = pygame.Rect(250, 115, 630, 200)
receiver_box = pygame.Rect(910, 130, 160, 160)
result_box = pygame.Rect(250, 325, 630, 80)

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
NOISE_COLOR = (230, 170, 60)
RAW_BUTTON_COLOR = (150, 90, 90)
FRAMED_BUTTON_COLOR = (90, 140, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
PLAYHEAD_COLOR = (255, 255, 255)

mode = "idle"     # "idle", "playing", "done"
variant = None    # "raw" or "framed"
start_time = 0
revealed_markers = []  # markers whose bit position the playhead has already passed
received_chars = []


def draw_text_centered(surface, text, fnt, color, center):
    rendered = fnt.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(center=center))


def stream_for(v):
    return RAW_STREAM if v == "raw" else FRAMED_STREAM


def start_run(now, chosen_variant):
    global mode, variant, start_time, revealed_markers, received_chars
    mode = "playing"
    variant = chosen_variant
    start_time = now
    revealed_markers = []
    received_chars = []


running = True
while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mode in ("idle", "done"):
                if raw_button.collidepoint(event.pos):
                    start_run(now, "raw")
                elif framed_button.collidepoint(event.pos):
                    start_run(now, "framed")

    stream = stream_for(variant) if variant else []
    total_sim_ms = len(stream) * TRUE_PERIOD
    sim_elapsed = 0

    if mode == "playing":
        sim_elapsed = (now - start_time) / SIM_SCALE
        current_bit = sim_elapsed / TRUE_PERIOD

        if variant == "raw":
            for boundary in RAW_CHUNK_BOUNDARIES[1:]:
                if current_bit >= boundary and boundary not in revealed_markers:
                    revealed_markers.append(boundary)
                    chunk = RAW_STREAM[boundary - 8:boundary]
                    val = int("".join(map(str, chunk)), 2)
                    ch = chr(val) if 32 <= val < 127 else "?"
                    expected = "Hi"[len(received_chars)] if len(received_chars) < 2 else None
                    received_chars.append((ch, expected == ch))
        else:
            for ev in FRAMED_EVENTS:
                if current_bit >= ev["bit"] and id(ev) not in revealed_markers:
                    revealed_markers.append(id(ev))
                    if ev["kind"] == "frame":
                        val = ev["value"]
                        ch = chr(val) if 32 <= val < 127 else "?"
                        received_chars.append((ch, True))

        if sim_elapsed >= total_sim_ms + 100:
            mode = "done"

    screen.fill(BG_COLOR)

    draw_text_centered(screen, "Framing", font, TEXT_COLOR, (WIDTH // 2, 25))

    can_run = mode in ("idle", "done")
    pygame.draw.rect(screen, RAW_BUTTON_COLOR if can_run else BOX_COLOR, raw_button, border_radius=8)
    draw_text_centered(screen, "SEND RAW (NO FRAMING)", button_font, BUTTON_TEXT_COLOR, raw_button.center)
    pygame.draw.rect(screen, FRAMED_BUTTON_COLOR if can_run else BOX_COLOR, framed_button, border_radius=8)
    draw_text_centered(screen, "SEND FRAMED (START/STOP BITS)", button_font, BUTTON_TEXT_COLOR, framed_button.center)

    # sender
    pygame.draw.rect(screen, BOX_COLOR, sender_box, border_radius=10)
    pygame.draw.rect(screen, SENDER_BORDER, sender_box, width=3, border_radius=10)
    draw_text_centered(screen, "SENDER", label_font, TEXT_COLOR, (sender_box.centerx, sender_box.y + 22))
    draw_text_centered(screen, "sending \"Hi\"", small_font, DIM_TEXT_COLOR, (sender_box.centerx, sender_box.y + 48))
    draw_text_centered(screen, "+ one real", small_font, NOISE_COLOR, (sender_box.centerx, sender_box.y + 72))
    draw_text_centered(screen, "noise bit", small_font, NOISE_COLOR, (sender_box.centerx, sender_box.y + 92))

    # receiver
    pygame.draw.rect(screen, BOX_COLOR, receiver_box, border_radius=10)
    pygame.draw.rect(screen, RECEIVER_BORDER, receiver_box, width=3, border_radius=10)
    draw_text_centered(screen, "RECEIVER", label_font, TEXT_COLOR, (receiver_box.centerx, receiver_box.y + 22))
    for i, (ch, ok) in enumerate(received_chars):
        col = CORRECT_COLOR if ok else WRONG_COLOR
        draw_text_centered(screen, f"'{ch}'" if ok else f"'{ch}' (wrong)", mono_font, col, (receiver_box.centerx, receiver_box.y + 60 + i * 26))

    # scope
    pygame.draw.rect(screen, BOX_COLOR, scope_box, border_radius=8)
    pygame.draw.rect(screen, SCOPE_BORDER, scope_box, width=3, border_radius=8)
    trace_left = scope_box.x + 15
    trace_right = scope_box.right - 15
    trace_width = trace_right - trace_left
    high_y = scope_box.y + 60
    low_y = scope_box.bottom - 40

    if mode != "idle" and stream:
        def x_for_bit(b):
            return trace_left + (b / len(stream)) * trace_width

        visible_bits = min(sim_elapsed / TRUE_PERIOD, len(stream)) if mode == "playing" else len(stream)

        points = []
        t = 0.0
        while t <= visible_bits:
            idx = min(int(t), len(stream) - 1)
            points.append((x_for_bit(t), high_y if stream[idx] else low_y))
            t += 0.1
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            pygame.draw.line(screen, TRACE_COLOR, (x1, y1), (x2, y1), 2)
            if y1 != y2:
                pygame.draw.line(screen, TRACE_COLOR, (x2, y1), (x2, y2), 2)

        if variant == "raw":
            for b in RAW_CHUNK_BOUNDARIES:
                if b <= visible_bits:
                    bx = x_for_bit(b)
                    pygame.draw.line(screen, (90, 90, 100), (bx, scope_box.y + 8), (bx, scope_box.bottom - 8), 1)
            glitch_x = x_for_bit(8)
            if 8 <= visible_bits:
                draw_text_centered(screen, "noise", small_font, NOISE_COLOR, (glitch_x, scope_box.bottom - 20))
        else:
            for ev in FRAMED_EVENTS:
                if ev["bit"] <= visible_bits:
                    bx = x_for_bit(ev["bit"])
                    if ev["kind"] == "frame":
                        pygame.draw.circle(screen, CORRECT_COLOR, (int(bx), int(high_y - 15)), 5)
                        draw_text_centered(screen, "start", small_font, CORRECT_COLOR, (bx, high_y - 30))
                    else:
                        pygame.draw.circle(screen, WRONG_COLOR, (int(bx), int(high_y - 15)), 5)
                        draw_text_centered(screen, "noise -", small_font, WRONG_COLOR, (bx, high_y - 30))
                        draw_text_centered(screen, "ignored", small_font, WRONG_COLOR, (bx, high_y - 45))

        if mode == "playing":
            px = x_for_bit(visible_bits)
            pygame.draw.line(screen, PLAYHEAD_COLOR, (px, scope_box.y + 5), (px, scope_box.bottom - 5), 2)
    else:
        draw_text_centered(screen, "click a SEND button - both send \"Hi\" plus one real bit of noise",
                            small_font, DIM_TEXT_COLOR, (scope_box.centerx, scope_box.centery))

    # result
    if mode == "done":
        received_str = "".join(ch for ch, _ in received_chars)
        all_correct = all(ok for _, ok in received_chars) and received_str == "Hi"
        border_col = CORRECT_COLOR if all_correct else WRONG_COLOR
        pygame.draw.rect(screen, BOX_COLOR, result_box, border_radius=8)
        pygame.draw.rect(screen, border_col, result_box, width=3, border_radius=8)
        draw_text_centered(screen, f"SENT: \"Hi\"    RECEIVED: \"{received_str}\"", big_font, TEXT_COLOR, (result_box.centerx, result_box.y + 28))
        verdict = "correct - the noise was rejected, framing recovered" if all_correct else "corrupted - one glitch bit permanently threw off every byte after it"
        draw_text_centered(screen, verdict, small_font, border_col, (result_box.centerx, result_box.y + 58))

    if mode == "idle":
        status = "same data, same noise bit, both times - only framing can tell noise from a real start bit"
    elif mode == "playing":
        status = "watch the playhead cross the noise bit - RAW has no way to know it's there"
    else:
        status = "click a SEND button to replay"
    status_text = small_font.render(status, True, DIM_TEXT_COLOR)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT - 22))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
