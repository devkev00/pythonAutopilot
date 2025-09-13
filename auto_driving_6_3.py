# SVD를 이용하여 회전와 이동을 알아내자

import pygame
import numpy as np
import ad_util

pygame.init()
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width * 2, screen_height))
pygame.display.set_caption("AUTO DRIVING")
clock = pygame.time.Clock()

center = np.array([screen_width // 2, screen_height // 2])
dst_center = np.array([screen_width + screen_width // 2, screen_height // 2])
# 단위 정사각형 좌표 (시계방향으로)
x = np.linspace(-1,1,11)
y = np.linspace(-1,1,11)

src_pnts = np.meshgrid(x,y)
src_pnts = np.stack(src_pnts, axis=-1).reshape(-1, 2)

colors = np.random.randint(0, 256, size=(121, 3))

# 임의의 T
theta = np.radians(30)
T = np.array([[np.cos(theta), -np.sin(theta), 1.0],
              [np.sin(theta),  np.cos(theta), 0.5],
              [1,1,0]])
ones = np.ones((src_pnts.shape[0], 1))
src_homo = np.hstack([src_pnts, ones])
dst_pnts = (T @ src_homo.T).T[:,:2]
print(T)

def draw_shape(points, color, origin, scale = 100, radius =5):
    for i in range(len(points)):
        px, py = points[i]
        screen_x = int(px * scale + origin[0])
        screen_y = int(-py * scale + origin[1])  # ← y축 반전
        pygame.draw.circle(screen, colors[i], (screen_x, screen_y), radius)

centroid_src = np.mean(src_pnts, axis=0)
centroid_dst = np.mean(dst_pnts, axis=0)
SS = src_pnts - centroid_src
DD = dst_pnts - centroid_dst
H = SS.T @ DD
U, _, VT = np.linalg.svd(H)
R = VT.T @ U.T
if np.linalg.det(R) < 0:
    VT[1, :] *= -1
    R = VT.T @ U.T
t = centroid_dst - R @ centroid_src
T_est = np.eye(3)
T_est[:2, :2] = R
T_est[:2, 2] = t
print(T_est)

ones = np.ones((src_pnts.shape[0], 1))
src_homo = np.hstack([src_pnts, ones])
dst_est_pnts = (T_est @ src_homo.T).T[:,:2]

# 애니메이션 루프
running = True
i = 0
show_pnts = src_pnts
while running:
    clock.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    show_pnts = (1 - i / 100) * src_pnts + (i / 100) * dst_est_pnts

    draw_shape(show_pnts, colors, center)
    draw_shape(dst_pnts,colors,dst_center)

    pygame.draw.line(screen, ad_util.red, (screen_width // 2, 0), (screen_width // 2, screen_height), 1)
    pygame.draw.line(screen, ad_util.red, (screen_width + screen_width // 2, 0), (screen_width + screen_width // 2, screen_height), 1)
    pygame.draw.line(screen, ad_util.red, (0, screen_height // 2), (screen_width*2, screen_height // 2), 1)
    pygame.display.flip()
    i = (i+1)%100
pygame.quit()
