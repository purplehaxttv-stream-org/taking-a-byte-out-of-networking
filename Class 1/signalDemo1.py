import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 520

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Signal Demo 1 - Bits on a Wire")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
label_font = pygame.font.SysFont(None, 26)
small_font = pygame.font.SysFont(None, 21)
button_font = pygame.font.SysFont(None, 25)
big_font = pygame.font.SysFont(None, 40)

SAMPLE_MS = 25
MAX_SAMPLES = 160

machine_a_box = pygame.Rect(40, 220, 190, 170)
machine_b_box = pygame.Rect(770, 220, 190, 170)
scope_box = pygame.Rect(260, 90, 480, 110)

wire_y = machine_a_box.centery

send0_button = pygame.Rect(machine_a_box.x + 20, machine_a_box.bottom - 80, 150, 34)
send1_button = pygame.Rect(machine_a_box.x + 20, machine_a_box.bottom - 40, 150, 34)

lonely_bubble = pygame.Rect(machine_a_box.x - 15, machine_a_box.y - 75, 240, 50)
lonely_tail = [(machine_a_box.x + 40, lonely_bubble.bottom), (machine_a_box.x + 65, lonely_bubble.bottom), (machine_a_box.x + 40, lonely_bubble.bottom + 18)]
connect_button = pygame.Rect(WIDTH // 2 - 100, 260, 200, 46)

BG_COLOR = (20, 20, 20)
TEXT_COLOR = (230, 230, 230)
DIM_TEXT_COLOR = (150, 150, 155)
BOX_COLOR = (50, 50, 60)
MACHINE_A_BORDER = (100, 200, 255)
MACHINE_B_BORDER = (150, 220, 120)
SCOPE_BORDER = (170, 140, 220)
HIGH_COLOR = (255, 90, 70)
LOW_COLOR = (90, 130, 200)
TRACE_COLOR = (255, 220, 120)
BUTTON0_COLOR = (60, 90, 150)
BUTTON1_COLOR = (150, 90, 90)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUBBLE_COLOR = (60, 55, 65)
BUBBLE_BORDER = (150, 150, 155)
CONNECT_BUTTON_COLOR = (90, 140, 100)

mode = "lonely"  # "lonely" -> "connected"
current_level = 0  # 0 = LOW, 1 = HIGH - idle wire starts LOW
history = [0] * MAX_SAMPLES
last_sample_tick = 0


def draw_text_centered(surface, text, fnt, color, center):
    rendered = fnt.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(center=center))


def draw_text_left(surface, text, fnt, color, pos):
    rendered = fnt.render(text, True, color)
    surface.blit(rendered, pos)


running = True
while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mode == "lonely":
                if connect_button.collidepoint(event.pos):
                    mode = "connected"
            else:
                if send0_button.collidepoint(event.pos):
                    current_level = 0
                elif send1_button.collidepoint(event.pos):
                    current_level = 1

    if mode == "connected" and now - last_sample_tick >= SAMPLE_MS:
        history.append(current_level)
        if len(history) > MAX_SAMPLES:
            history.pop(0)
        last_sample_tick = now

    screen.fill(BG_COLOR)

    # machine A - always present
    pygame.draw.rect(screen, BOX_COLOR, machine_a_box, border_radius=10)
    pygame.draw.rect(screen, MACHINE_A_BORDER, machine_a_box, width=3, border_radius=10)
    draw_text_centered(screen, "MACHINE A", label_font, TEXT_COLOR, (machine_a_box.centerx, machine_a_box.y + 22))
    draw_text_centered(screen, "(sender)" if mode == "connected" else "", small_font, DIM_TEXT_COLOR, (machine_a_box.centerx, machine_a_box.y + 44))

    if mode == "lonely":
        draw_text_centered(screen, "It's Alone", font, TEXT_COLOR, (WIDTH // 2, 25))
        draw_text_centered(screen, "no wire, no Machine B, nothing to talk to yet",
                            small_font, DIM_TEXT_COLOR, (WIDTH // 2, 55))

        pygame.draw.rect(screen, BUBBLE_COLOR, lonely_bubble, border_radius=10)
        pygame.draw.rect(screen, BUBBLE_BORDER, lonely_bubble, width=2, border_radius=10)
        pygame.draw.polygon(screen, BUBBLE_COLOR, lonely_tail)
        pygame.draw.polygon(screen, BUBBLE_BORDER, lonely_tail, width=2)
        draw_text_centered(screen, "I am lonely...", label_font, TEXT_COLOR, lonely_bubble.center)

        pygame.draw.rect(screen, CONNECT_BUTTON_COLOR, connect_button, border_radius=8)
        draw_text_centered(screen, "CONNECT MACHINE B", button_font, BUTTON_TEXT_COLOR, connect_button.center)

        status = "click CONNECT MACHINE B - let's fix that"
        status_text = small_font.render(status, True, DIM_TEXT_COLOR)
        screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)
        continue

    draw_text_centered(screen, "Bits on a Wire", font, TEXT_COLOR, (WIDTH // 2, 25))
    draw_text_centered(screen, "convention: HIGH (5V) = 1   |   LOW (0V) = 0 - agreed in advance, not inherent",
                        small_font, DIM_TEXT_COLOR, (WIDTH // 2, 55))

    pygame.draw.rect(screen, BUTTON0_COLOR, send0_button, border_radius=6)
    draw_text_centered(screen, "SEND 0 (LOW)", button_font, BUTTON_TEXT_COLOR, send0_button.center)
    pygame.draw.rect(screen, BUTTON1_COLOR, send1_button, border_radius=6)
    draw_text_centered(screen, "SEND 1 (HIGH)", button_font, BUTTON_TEXT_COLOR, send1_button.center)

    # machine B
    pygame.draw.rect(screen, BOX_COLOR, machine_b_box, border_radius=10)
    pygame.draw.rect(screen, MACHINE_B_BORDER, machine_b_box, width=3, border_radius=10)
    draw_text_centered(screen, "MACHINE B", label_font, TEXT_COLOR, (machine_b_box.centerx, machine_b_box.y + 22))
    draw_text_centered(screen, "(receiver)", small_font, DIM_TEXT_COLOR, (machine_b_box.centerx, machine_b_box.y + 44))
    level_color = HIGH_COLOR if current_level else LOW_COLOR
    draw_text_centered(screen, "HIGH" if current_level else "LOW", big_font, level_color, (machine_b_box.centerx, machine_b_box.y + 85))
    draw_text_centered(screen, f"reads as bit: {current_level}", small_font, TEXT_COLOR, (machine_b_box.centerx, machine_b_box.y + 125))

    # wire between them, colored by current level
    wire_color = HIGH_COLOR if current_level else LOW_COLOR
    pygame.draw.line(screen, wire_color, (machine_a_box.right, wire_y), (machine_b_box.x, wire_y), 5)

    # oscilloscope trace - the actual point of this demo: voltage over time
    pygame.draw.rect(screen, BOX_COLOR, scope_box, border_radius=8)
    pygame.draw.rect(screen, SCOPE_BORDER, scope_box, width=3, border_radius=8)
    draw_text_left(screen, "OSCILLOSCOPE", small_font, TEXT_COLOR, (scope_box.x + 10, scope_box.y + 6))

    high_y = scope_box.y + 30
    low_y = scope_box.bottom - 15
    trace_left = scope_box.x + 10
    trace_right = scope_box.right - 10
    step = (trace_right - trace_left) / (MAX_SAMPLES - 1)

    points = []
    for i, level in enumerate(history):
        x = trace_left + i * step
        y = high_y if level else low_y
        points.append((x, y))

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        pygame.draw.line(screen, TRACE_COLOR, (x1, y1), (x2, y1), 2)
        if y1 != y2:
            pygame.draw.line(screen, TRACE_COLOR, (x2, y1), (x2, y2), 2)

    status = "click SEND 0 or SEND 1 - Machine B reads whatever voltage is on the wire, right now, live"
    status_text = small_font.render(status, True, DIM_TEXT_COLOR)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
