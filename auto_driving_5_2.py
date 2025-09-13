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
        show_pnts = src_pnt - rotate_center
        is_show = False

    if state == 2 and is_show:
        rotated_x = np.cos(angle) * show_pnts[:, 0] - np.sin(angle) * show_pnts[:, 1]
        rotated_y = np.sin(angle) * show_pnts[:, 0] + np.cos(angle) * show_pnts[:, 1]
        rotated = np.stack((rotated_x, rotated_y), axis=1)
        show_pnts = rotated
        is_show = False

    if state == 3 and is_show:
        show_pnts = show_pnts + rotate_center
        is_show = False

    if state == 4 and is_show:
        show_pnts = show_pnts + translate
        is_show = False

    screen.fill(ad_util.black)
    draw_shape(show_pnts,colors,(400,400),)
    pygame.draw.line(screen, ad_util.red, (screen_width//2, 0), (screen_width//2, screen_height), 1)
    pygame.draw.line(screen, ad_util.red, (0,screen_height//2), (screen_width, screen_height//2), 1)
    pygame.display.flip()

pygame.quit()