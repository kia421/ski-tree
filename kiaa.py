import pygame
import random
#بازيو دادم تغيير يکم

pygame.init()

# اندازه صفحه بازی
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ski Tree Game")

#موزيک
pygame.mixer.music.load('02. Mehrad Hidden Ft Pishro - Rock A Chock.mp3')
pygame.mixer.music.play(-1,0.0)
musicPlaying=True

# رنگ‌ها
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# تنظیمات بازی
clock = pygame.time.Clock()
ski_speed = 5
tree_speed = 5
ski_width = 50
ski_height = 50
tree_width = 50
tree_height = 50
font = pygame.font.SysFont("arial", 30)

# موقعیت اولیه اسکی‌باز
ski_x = screen_width // 2 - ski_width // 2
ski_y = screen_height - ski_height - 10

# ایجاد درخت‌ها
trees = []

# تابع برای نمایش امتیاز
def draw_score(score):
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))

# تابع برای نمایش اسکی‌باز
def draw_ski(ski_x, ski_y):
    pygame.draw.rect(screen, GREEN, (ski_x, ski_y, ski_width, ski_height))

# تابع برای نمایش درخت
def draw_tree(x, y):
    pygame.draw.rect(screen, RED, (x, y, tree_width, tree_height))

# تابع برای حرکت درخت‌ها
def move_trees(trees):
    for tree in trees:
        tree[1] += tree_speed
        if tree[1] > screen_height:
            trees.remove(tree)
            trees.append([random.randint(0, screen_width - tree_width), -tree_height])

# تابع برای بررسی برخورد
def check_collision(ski_x, ski_y, trees):
    for tree in trees:
        tree_x, tree_y = tree
        if (ski_x < tree_x + tree_width and ski_x + ski_width > tree_x) and \
           (ski_y < tree_y + tree_height and ski_y + ski_height > tree_y):
            return True
    return False

# حلقه اصلی بازی
def game_loop():
    ski_x = screen_width // 2 - ski_width // 2
    ski_y = screen_height - ski_height - 10
    ski_move_left = False
    ski_move_right = False
    score = 0
    trees.clear()

    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_score(score)

        # مدیریت رویدادها
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    ski_move_left = True
                elif event.key == pygame.K_d:
                    ski_move_right = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    ski_move_left = False
                elif event.key == pygame.K_d:
                    ski_move_right = False

        # حرکت اسکی‌باز
        if ski_move_left and ski_x > 0:
            ski_x -= ski_speed
        if ski_move_right and ski_x < screen_width - ski_width:
            ski_x += ski_speed

        # اضافه کردن درخت‌ها
        if random.random() < 0.02:  # احتمال ایجاد درخت جدید
            trees.append([random.randint(0, screen_width - tree_width), -tree_height])

        # حرکت درخت‌ها
        move_trees(trees)

        # نمایش درخت‌ها
        for tree in trees:
            draw_tree(tree[0], tree[1])

        # نمایش اسکی‌باز
        draw_ski(ski_x, ski_y)

        # بررسی برخورد
        if check_collision(ski_x, ski_y, trees):
            game_over_text = font.render("Game Over", True, WHITE)
            screen.blit(game_over_text, (screen_width // 2 - 100, screen_height // 2))
            pygame.display.update()
            pygame.time.wait(2000)  # 2 ثانیه تا پایان بازی
            break

        # به روز رسانی صفحه
        score += 1
        pygame.display.update()

        # تنظیم FPS (فریم در ثانیه)
        clock.tick(60)

# شروع بازی
game_loop()

# بستن pygame
pygame.quit()
