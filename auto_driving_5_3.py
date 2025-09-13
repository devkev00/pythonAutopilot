# 점군 데이터 이동

import pygame
import numpy as np
import ad_util

def draw_shape(points, color, origin, scale = 100, radius =5):
    for i in range(len(points)):
        px, py = points[i]
        screen_x = int(px * scale + origin[0])
        screen_y = int(-py * scale + origin[1])  # ← y축 반전
        pygame.draw.circle(screen, colors[i], (screen_x, screen_y), radius)

# pygame 초기화
pygame.init()

# 스크린 정의
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# 타이틀
pygame.display.set_caption("AUTO DRIVING")

# 단위 정사각형 좌표 (시계방향으로)
x = np.linspace(-1,1,11)
y = np.linspace(-1,1,11)

src_pnt = np.meshgrid(x,y)
src_pnt = np.stack(src_pnt, axis=-1).reshape(-1, 2)

colors = np.random.randint(0, 256, size=(src_pnt.shape[0], 3))

translate = np.array([1, -1])
rotate_center = np.array([0.5, 0.5])
angle = np.radians(45)

T1 = np.array([[1, 0, -rotate_center[0]],
               [0, 1, -rotate_center[1]],
               [0, 0, 1]])

T2 = np.array([[np.cos(angle), -np.sin(angle), 0],
               [np.sin(angle),  np.cos(angle), 0],
               [0, 0, 1]])

T3 = np.array([[1, 0, rotate_center[0]],
               [0, 1, rotate_center[1]],
               [0, 0, 1]])

T4 = np.array([[1, 0, translate[0]],
               [0, 1, translate[1]],
               [0, 0, 1]])

# 게임 진행
running = True

# FPS 설정
FPS = 10
clock = pygame.time.Clock()
state = 0
show_pnts = src_pnt
while running:
    dt = clock.tick(FPS) / 1000.
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        state = state + 1
        is_show = True
    # 회전 중심을 원점으로 이동
    if state == 1 and is_show:
        ones = np.ones((show_pnts.shape[0], 1))
        homo = np.hstack([show_pnts, ones])
        show_pnts = (T1 @ homo.T).T[:, :2]
        is_show = False

    if state == 2 and is_show:
        ones = np.ones((show_pnts.shape[0], 1))
        homo = np.hstack([show_pnts, ones])
        show_pnts = (T2 @ homo.T).T[:, :2]
        is_show = False

    if state == 3 and is_show:
        ones = np.ones((show_pnts.shape[0], 1))
        homo = np.hstack([show_pnts, ones])
        show_pnts = (T3 @ homo.T).T[:, :2]
        is_show = False

    if state == 4 and is_show:
        ones = np.ones((show_pnts.shape[0], 1))
        homo = np.hstack([show_pnts, ones])
        show_pnts = (T4 @ homo.T).T[:, :2]
        is_show = False

    if state == 5 and is_show:
        show_pnts = src_pnt
        is_show = False

    if state == 6 and is_show:
        ones = np.ones((show_pnts.shape[0], 1))
        homo = np.hstack([show_pnts, ones])
        show_pnts = (T4@T3@T2@T1 @ homo.T).T[:, :2]
        is_show = False

    screen.fill(ad_util.black)
    draw_shape(show_pnts,colors,(400,400),)
    pygame.draw.line(screen, ad_util.red, (screen_width//2, 0), (screen_width//2, screen_height), 1)
    pygame.draw.line(screen, ad_util.red, (0,screen_height//2), (screen_width, screen_height//2), 1)
    pygame.display.flip()

pygame.quit()