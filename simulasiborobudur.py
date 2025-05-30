import pygame
import random
import sys

# --- Konfigurasi ---
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
FPS = 60
MAX_PER_HOUR = 100
MAX_TOTAL = 1200
HOURS = 12

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
GREEN = (0, 180, 0)
RED = (200, 50, 50)
GRAY = (100, 100, 100)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simulasi Antrean Candi Borobudur")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# Area
CANDI_AREA = pygame.Rect(500, 100, 350, 300)
ENTRY_POINT = (CANDI_AREA.centerx, CANDI_AREA.bottom + 20)
EXIT_POINT = (CANDI_AREA.centerx, CANDI_AREA.top - 40)

# Area antrean random di kiri bawah layar
QUEUE_AREA = pygame.Rect(50, 450, 200, 100)

class Visitor:
    def __init__(self, idx):
        self.idx = idx
        self.state = "waiting"  # Mulai dari waiting dulu, belum muncul di antrean
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.speed = 1.5
        self.target = None
        self.explore_time = 0
        self.path = []  # Jalur yg harus dilalui (list titik)
        self.current_target_idx = 0

    def set_random_start_pos(self):
        # Posisi acak di area antrean (random distribusi)
        self.rect.x = random.randint(QUEUE_AREA.left, QUEUE_AREA.right)
        self.rect.y = random.randint(QUEUE_AREA.top, QUEUE_AREA.bottom)

    def start_moving_path(self, path, next_state):
        # Mulai berjalan mengikuti path titik-titik, setelah sampai target terakhir ganti state
        self.path = path
        self.current_target_idx = 0
        self.next_state = next_state
        self.state = "walking"
        self.target = self.path[self.current_target_idx]

    def update(self):
        if self.state == "walking" and self.target:
            dx, dy = self.target[0] - self.rect.x, self.target[1] - self.rect.y
            dist = (dx**2 + dy**2)**0.5
            if dist < 2:
                # Sampai target, lanjut ke target berikutnya
                self.current_target_idx += 1
                if self.current_target_idx >= len(self.path):
                    # Selesai jalur, pindah ke next state
                    self.state = self.next_state
                    self.target = None
                    if self.state == "exploring":
                        self.explore_time = random.randint(8 * FPS, 15 * FPS)
                else:
                    self.target = self.path[self.current_target_idx]
            else:
                self.rect.x += int(dx / dist * self.speed)
                self.rect.y += int(dy / dist * self.speed)

        elif self.state == "exploring":
            self.explore_time -= 1
            if self.explore_time <= 0:
                # Setelah eksplorasi selesai, langsung jalan keluar candi (jalur lurus)
                self.start_moving_path([EXIT_POINT], "exiting")
            elif not self.target or random.random() < 0.02:
                # Update tujuan eksplorasi random di area candi
                self.target = [random.randint(CANDI_AREA.left, CANDI_AREA.right),
                               random.randint(CANDI_AREA.top, CANDI_AREA.bottom)]
            dx, dy = self.target[0] - self.rect.x, self.target[1] - self.rect.y
            dist = (dx**2 + dy**2)**0.5
            if dist > 1:
                self.rect.x += int(dx / dist * self.speed)
                self.rect.y += int(dy / dist * self.speed)

    def draw(self, surface):
        if self.state == "waiting":
            color = GRAY  # belum mulai antrean
        elif self.state == "walking":
            color = BLUE
        elif self.state == "exploring":
            color = GREEN
        elif self.state == "exiting":
            color = RED
        pygame.draw.rect(surface, color, self.rect)


# --- Simulasi State ---
all_visitors = [Visitor(i) for i in range(MAX_TOTAL)]
active_visitors = []
hour = 7
minute = 0
frames = 0
next_batch_time = 0  # jam batch berikutnya
current_batch = []
entered_visitors = set()

running = True
while running:
    screen.fill(WHITE)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # Update waktu simulasi
    frames += 1
    if frames >= FPS:
        frames = 0
        minute += 1
        if minute >= 60:
            minute = 0
            hour += 1

    # Tambahkan batch baru saat masuk jam baru
    if hour - 7 == next_batch_time and len(all_visitors) > len(entered_visitors):
        start_idx = next_batch_time * MAX_PER_HOUR
        end_idx = min(start_idx + MAX_PER_HOUR, MAX_TOTAL)
        batch = all_visitors[start_idx:end_idx]

        for v in batch:
            v.set_random_start_pos()
            v.entry_delay = random.randint(0, 59 * FPS)  # delay acak sampai 1 jam penuh
            v.state = "waiting"
            current_batch.append(v)

        next_batch_time += 1

    # Update antrean masuk
    for v in current_batch:
        if v.state == "waiting":
            v.entry_delay -= 1
            if v.entry_delay <= 0:
                path = [
                    (v.rect.x, v.rect.y),
                    (ENTRY_POINT[0], ENTRY_POINT[1] - 40),
                    ENTRY_POINT
                ]
                v.start_moving_path(path, "exploring")
                entered_visitors.add(v)

    # Update semua visitor
    for visitor in all_visitors:
        visitor.update()
        visitor.draw(screen)

    # Gambar area antrean
    pygame.draw.rect(screen, (220, 220, 220), QUEUE_AREA)
    screen.blit(font.render("Area Antrean (random)", True, BLACK), (QUEUE_AREA.left, QUEUE_AREA.top - 25))

    # Gambar candi bertingkat
    for i in range(6):
        width = 300 - i * 50
        x = CANDI_AREA.centerx - width // 2
        y = CANDI_AREA.bottom - i * 30 - 20
        pygame.draw.rect(screen, GRAY, (x, y, width, 20))

    # Gambar titik masuk dan keluar
    pygame.draw.circle(screen, BLACK, ENTRY_POINT, 5)
    pygame.draw.circle(screen, BLACK, EXIT_POINT, 5)
    screen.blit(font.render("Masuk", True, BLACK), (ENTRY_POINT[0] - 20, ENTRY_POINT[1] + 10))
    screen.blit(font.render("Keluar", True, BLACK), (EXIT_POINT[0] - 20, EXIT_POINT[1] - 20))
    screen.blit(font.render("Candi Borobudur", True, BLACK), (CANDI_AREA.left + 30, CANDI_AREA.top - 30))

    # Info waktu dan batch
    screen.blit(font.render(f"Jam: {hour}:{minute:02d}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Batch sekarang: {next_batch_time}", True, BLACK), (10, 40))
    screen.blit(font.render(f"Total Masuk: {len(entered_visitors)}", True, BLACK), (10, 70))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
