# 행렬 연산이 선형 변환임을 이해

import pygame
import numpy as np
import ad_util

pygame.init()
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("AUTO DRIVING")
clock = pygame.time.Clock()

center = np.array([screen_width // 2, screen_height // 2])

# 단위 정사각형 좌표 (시계방향으로)
x = np.linspace(-1,1,11)
y = np.linspace(-1,1,11)

pnt = np.meshgrid(x,y)
pnt = np.stack(pnt, axis=-1).reshape(-1, 2)

# 선형 변환 행렬 A
A = np.array([[1, 2],
              [0, 2]])

colors = np.random.randint(0, 256, size=(121, 3))

trans_pnts = (A @ pnt.T).T

def draw_shape(points, color, origin, scale = 100, radius =5):
    for i in range(len(points)):
        px, py = points[i]
        screen_x = int(px * scale + origin[0])
        screen_y = int(-py * scale + origin[1])  # ← y축 반전
        pygame.draw.circle(screen, colors[i], (screen_x, screen_y), radius)

# 애니메이션 루프
running = True
step = 100
step_count = 0
while running:
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    show_pnts = (1-step_count/step) * pnt + (step_count/step) * trans_pnts

    screen.fill((0, 0, 0))
    draw_shape(show_pnts,colors,center)
    pygame.draw.line(screen, ad_util.red, (screen_width // 2, 0), (screen_width // 2, screen_height), 1)
    pygame.draw.line(screen, ad_util.red, (0, screen_height // 2), (screen_width, screen_height // 2), 1)
    pygame.display.flip()
    step_count = (step_count+1)%step
pygame.quit()
