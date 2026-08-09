import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Signal Demo 4 - Not All Wires Are Wires")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
label_font = pygame.font.SysFont(None, 25)
small_font = pygame.font.SysFont(None, 19)
button_font = pygame.font.SysFont(None, 25)
mono_font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont(None, 32)

BYTE = ord('N')
TRUE_BITS = [(BYTE >> (7 - i)) & 1 for i in range(8)]
INTERFERENCE_BITS = [2, 5]  # bit indices where an EMI pulse fires

LANES = [
    {"name": "COPPER", "flips": {2, 5}, "color": (200, 130, 90), "note": "electrical, unshielded"},
    {"name": "COAX", "flips": {2}, "color": (150, 170, 200), "note": "electrical, shielded"},
    {"name": "FIBER", "flips": set(), "color": (150, 220, 170), "note": "light - immune to EMI"},
]

for lane in LANES:
    bits = TRUE_BITS[:]
    for i in lane["flips"]:
        bits[i] = 1 - bits[i]
    lane["final_bits"] = bits
    lane["final_value"] = int("".join(map(str, bits)), 2)

BIT_PERIOD_MS = 420

send_button = pygame.Rect(WIDTH // 2 - 110, 55, 220, 40)
emi_box = pygame.Rect(WIDTH // 2 - 90, 105, 180, 46)

cell_size, cell_gap = 50, 5
cells_start_x = 220
lane_ys = [175, 265, 355]

BG_COLOR = (20, 20, 20)
TEXT_COLOR = (230, 230, 230)
DIM_TEXT_COLOR = (150, 150, 155)
BOX_COLOR = (50, 50, 60)
CELL_EMPTY = (45, 45, 50)
FLIPPED_BORDER = (230, 90, 80)
NORMAL_BORDER = (90, 90, 100)
EMI_BORDER = (230, 170, 60)
EMI_FLASH = (255, 220, 120)
SEND_BUTTON_COLOR = (150, 90, 90)
BUTTON_TEXT_COLOR = (255, 255, 255)
CORRECT_COLOR = (100, 200, 120)
WRONG_COLOR = (230, 90, 80)

mode = "idle"  # "idle", "playing", "done"
start_time = 0


def draw_text_centered(surface, text, fnt, color, center):
    rendered = fnt.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(center=center))


def draw_text_left(surface, text, fnt, color, pos):
    rendered = fnt.render(text, True, color)
    surface.blit(rendered, pos)


def cell_center_x(i):
    return cells_start_x + i * (cell_size + cell_gap) + cell_size // 2


def start_run(now):
    global mode, start_time
    mode = "playing"
    start_time = now


running = True
while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if send_button.collidepoint(event.pos) and mode in ("idle", "done"):
                start_run(now)

    elapsed = now - start_time if mode == "playing" else 0
    current_bit = elapsed / BIT_PERIOD_MS
    revealed = min(8, int(current_bit) + 1) if mode == "playing" else (8 if mode == "done" else 0)

    if mode == "playing" and elapsed >= 8 * BIT_PERIOD_MS + 300:
        mode = "done"
        revealed = 8

    screen.fill(BG_COLOR)

    draw_text_centered(screen, "Not All Wires Are Wires", font, TEXT_COLOR, (WIDTH // 2, 25))

    can_send = mode in ("idle", "done")
    pygame.draw.rect(screen, SEND_BUTTON_COLOR if can_send else BOX_COLOR, send_button, border_radius=8)
    label = "SEND 'N' OVER ALL THREE" if mode != "playing" else "SENDING..."
    draw_text_centered(screen, label, button_font, BUTTON_TEXT_COLOR, send_button.center)

    active_pulse = None
    if mode == "playing":
        cur_idx = int(current_bit)
        if cur_idx in INTERFERENCE_BITS and current_bit - cur_idx < 0.6:
            active_pulse = cur_idx

    emi_border = EMI_FLASH if active_pulse is not None else EMI_BORDER
    pygame.draw.rect(screen, BOX_COLOR, emi_box, border_radius=8)
    pygame.draw.rect(screen, emi_border, emi_box, width=3, border_radius=8)
    draw_text_centered(screen, "EMI SOURCE", small_font, TEXT_COLOR, emi_box.center)

    for i, lane in enumerate(LANES):
        ly = lane_ys[i]
        draw_text_left(screen, lane["name"], label_font, lane["color"], (30, ly + 8))
        draw_text_left(screen, lane["note"], small_font, DIM_TEXT_COLOR, (30, ly + 30))

        for b in range(8):
            cx = cell_center_x(b)
            rect = pygame.Rect(cx - cell_size // 2, ly, cell_size, cell_size)
            if b < revealed:
                fill = lane["color"] if lane["flips"] and b in lane["flips"] else BOX_COLOR
                border = FLIPPED_BORDER if b in lane["flips"] else NORMAL_BORDER
                pygame.draw.rect(screen, fill, rect, border_radius=5)
                pygame.draw.rect(screen, border, rect, width=2, border_radius=5)
                draw_text_centered(screen, str(lane["final_bits"][b]), mono_font, TEXT_COLOR, rect.center)
            else:
                pygame.draw.rect(screen, CELL_EMPTY, rect, border_radius=5)

        if active_pulse is not None:
            px = cell_center_x(active_pulse)
            hit = active_pulse in lane["flips"]
            ray_color = FLIPPED_BORDER if hit else (90, 200, 120)
            pygame.draw.line(screen, ray_color, (emi_box.centerx, emi_box.bottom), (px, ly), 2)

        if revealed == 8:
            correct = lane["final_value"] == BYTE
            col = CORRECT_COLOR if correct else WRONG_COLOR
            result_x = cell_center_x(7) + 60
            ch = chr(lane["final_value"]) if 32 <= lane["final_value"] < 127 else "?"
            draw_text_centered(screen, f"'{ch}'", big_font, col, (result_x, ly + cell_size // 2))

    if mode == "idle":
        status = "click SEND - same byte 'N', same interference, three different physical mediums"
    elif mode == "playing":
        status = "watch the EMI pulses - green ray = no effect, red ray = bit flipped"
    else:
        all_correct = all(lane["final_value"] == BYTE for lane in LANES)
        status = "fiber alone came through clean - light doesn't care about electromagnetic noise (click SEND to replay)"
    status_text = small_font.render(status, True, DIM_TEXT_COLOR)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT - 45))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
