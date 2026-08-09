import pygame

pygame.init()

WIDTH, HEIGHT = 1080, 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Signal Demo 5 - One Byte, No Idea Whose")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
label_font = pygame.font.SysFont(None, 25)
small_font = pygame.font.SysFont(None, 19)
button_font = pygame.font.SysFont(None, 25)
mono_font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont(None, 34)


def bits_of(b):
    return [(b >> (7 - i)) & 1 for i in range(8)]


B_H, B_I = bits_of(ord('H')), bits_of(ord('i'))
STREAM = [1, 1, 0] + B_H + [1] + [1, 1, 0] + B_I + [1] + [1]


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
                    events.append({"bit": i, "value": val})
                    i += 10
                    continue
        i += 1
    return events


EVENTS = decode_framed(STREAM)
TRUE_PERIOD = 90   # simulated ms per bit
SIM_SCALE = 4       # real ms per simulated ms
TOTAL_SIM_MS = len(STREAM) * TRUE_PERIOD

run_button = pygame.Rect(WIDTH // 2 - 110, 55, 220, 44)

machine_a_box = pygame.Rect(30, 115, 180, 240)
scope_box = pygame.Rect(240, 115, 470, 240)
machine_b_box = pygame.Rect(750, 115, 300, 110)
machine_c_box = pygame.Rect(750, 245, 300, 110)

BG_COLOR = (20, 20, 20)
TEXT_COLOR = (230, 230, 230)
DIM_TEXT_COLOR = (150, 150, 155)
BOX_COLOR = (50, 50, 60)
SENDER_BORDER = (100, 200, 255)
RECEIVER_BORDER = (150, 220, 120)
SCOPE_BORDER = (170, 140, 220)
TRACE_COLOR = (255, 220, 120)
START_COLOR = (100, 200, 120)
RUN_BUTTON_COLOR = (150, 90, 90)
BUTTON_TEXT_COLOR = (255, 255, 255)
PLAYHEAD_COLOR = (255, 255, 255)
BANNER_COLOR = (230, 170, 60)
BUBBLE_COLOR = (60, 55, 65)
BUBBLE_BORDER = (150, 150, 155)

mode = "idle"   # "idle", "playing", "done"
start_time = 0
received = []   # chars decoded so far - identical for B and C, since they see the same wire


def draw_text_centered(surface, text, fnt, color, center):
    rendered = fnt.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(center=center))


def start_run(now):
    global mode, start_time, received
    mode = "playing"
    start_time = now
    received = []


running = True
while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if run_button.collidepoint(event.pos) and mode in ("idle", "done"):
                start_run(now)

    sim_elapsed = 0
    if mode == "playing":
        sim_elapsed = (now - start_time) / SIM_SCALE
        current_bit = sim_elapsed / TRUE_PERIOD
        for ev in EVENTS:
            if current_bit >= ev["bit"] + 9 and ev["value"] not in [v for v, _ in received]:
                received.append((ev["value"], ev["bit"]))
        if sim_elapsed >= TOTAL_SIM_MS + 150:
            mode = "done"

    screen.fill(BG_COLOR)

    draw_text_centered(screen, "One Byte, No Idea Whose", font, TEXT_COLOR, (WIDTH // 2, 25))

    can_run = mode in ("idle", "done")
    pygame.draw.rect(screen, RUN_BUTTON_COLOR if can_run else BOX_COLOR, run_button, border_radius=8)
    label = "RUN" if mode == "idle" else ("SENDING..." if mode == "playing" else "REPLAY")
    draw_text_centered(screen, label, button_font, BUTTON_TEXT_COLOR, run_button.center)

    # machine A
    pygame.draw.rect(screen, BOX_COLOR, machine_a_box, border_radius=10)
    pygame.draw.rect(screen, SENDER_BORDER, machine_a_box, width=3, border_radius=10)
    draw_text_centered(screen, "MACHINE A", label_font, TEXT_COLOR, (machine_a_box.centerx, machine_a_box.y + 24))
    draw_text_centered(screen, "sending \"Hi\"", small_font, DIM_TEXT_COLOR, (machine_a_box.centerx, machine_a_box.y + 50))
    draw_text_centered(screen, "(no address, no", small_font, DIM_TEXT_COLOR, (machine_a_box.centerx, machine_a_box.y + 90))
    draw_text_centered(screen, "recipient - just bits)", small_font, DIM_TEXT_COLOR, (machine_a_box.centerx, machine_a_box.y + 110))

    # scope - the one shared physical link
    pygame.draw.rect(screen, BOX_COLOR, scope_box, border_radius=8)
    pygame.draw.rect(screen, SCOPE_BORDER, scope_box, width=3, border_radius=8)
    draw_text_centered(screen, "SHARED WIRE", small_font, TEXT_COLOR, (scope_box.centerx, scope_box.y + 16))

    trace_left = scope_box.x + 15
    trace_right = scope_box.right - 15
    trace_width = trace_right - trace_left
    high_y = scope_box.y + 55
    low_y = scope_box.bottom - 40

    def x_for_bit(b):
        return trace_left + (b / len(STREAM)) * trace_width

    if mode != "idle":
        visible_bits = min(sim_elapsed / TRUE_PERIOD, len(STREAM)) if mode == "playing" else len(STREAM)
        points = []
        t = 0.0
        while t <= visible_bits:
            idx = min(int(t), len(STREAM) - 1)
            points.append((x_for_bit(t), high_y if STREAM[idx] else low_y))
            t += 0.1
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            pygame.draw.line(screen, TRACE_COLOR, (x1, y1), (x2, y1), 2)
            if y1 != y2:
                pygame.draw.line(screen, TRACE_COLOR, (x2, y1), (x2, y2), 2)
        for ev in EVENTS:
            if ev["bit"] <= visible_bits:
                bx = x_for_bit(ev["bit"])
                pygame.draw.circle(screen, START_COLOR, (int(bx), int(high_y - 15)), 5)
        if mode == "playing":
            px = x_for_bit(visible_bits)
            pygame.draw.line(screen, PLAYHEAD_COLOR, (px, scope_box.y + 30), (px, scope_box.bottom - 10), 2)
    else:
        draw_text_centered(screen, "click RUN to transmit", small_font, DIM_TEXT_COLOR, (scope_box.centerx, scope_box.centery))

    # taps out to B and C - both literally the same wire
    tap_x = scope_box.right
    pygame.draw.line(screen, SCOPE_BORDER, (tap_x, scope_box.centery), (tap_x + 30, scope_box.centery), 2)
    pygame.draw.line(screen, SCOPE_BORDER, (tap_x + 30, machine_b_box.centery), (machine_b_box.x, machine_b_box.centery), 2)
    pygame.draw.line(screen, SCOPE_BORDER, (tap_x + 30, machine_c_box.centery), (machine_c_box.x, machine_c_box.centery), 2)
    pygame.draw.line(screen, SCOPE_BORDER, (tap_x + 30, machine_b_box.centery), (tap_x + 30, machine_c_box.centery), 2)

    received_str = "".join(chr(v) for v, _ in received)

    for box, name in ((machine_b_box, "MACHINE B"), (machine_c_box, "MACHINE C")):
        pygame.draw.rect(screen, BOX_COLOR, box, border_radius=10)
        pygame.draw.rect(screen, RECEIVER_BORDER, box, width=3, border_radius=10)
        draw_text_centered(screen, name, label_font, TEXT_COLOR, (box.centerx, box.y + 24))
        draw_text_centered(screen, f"received: \"{received_str}\"" if received_str else "received: -",
                            mono_font, TEXT_COLOR, (box.centerx, box.y + 55))
        if mode == "done":
            draw_text_centered(screen, "...is this for me?", small_font, BANNER_COLOR, (box.centerx, box.y + 82))

    if mode == "done":
        banner = pygame.Rect(240, 365, 470, 44)
        pygame.draw.rect(screen, BOX_COLOR, banner, border_radius=8)
        pygame.draw.rect(screen, BANNER_COLOR, banner, width=3, border_radius=8)
        draw_text_centered(screen, "both got it perfectly - neither knows if it's theirs", small_font, BANNER_COLOR, banner.center)

    if mode == "idle":
        status = "click RUN - Machine A sends \"Hi\" over one shared physical wire"
    elif mode == "playing":
        status = "Machine B and Machine C are both on this same wire - they see the exact same signal, live"
    else:
        status = "the physical layer moved bits across a link perfectly. it has no idea who they were for."
    status_text = small_font.render(status, True, DIM_TEXT_COLOR)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT - 22))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
