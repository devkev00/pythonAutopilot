# ICP 기초 구현

import pygame
import numpy as np
import ad_util


def nearest_neighbor(src, dst,distance_threshold):
    indices = []
    for p in src:
        p = np.array(p)
        d = np.linalg.norm(dst - p, axis=1)
        min_idx = np.argmin(d)
        if d[min_idx] < distance_threshold:
            indices.append(min_idx)
        else:
            indices.append(-1)
    return np.array(indices)

def SVD_fit(A, B):
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B
    H = AA.T @ BB
    U, _, VT = np.linalg.svd(H)
    R = VT.T @ U.T
    if np.linalg.det(R) < 0:
        VT[1, :] *= -1
        R = VT.T @ U.T
    t = centroid_B - R @ centroid_A
    T = np.eye(3)
    T[:2, :2] = R
    T[:2, 2] = t
    return T

pygame.init()
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width * 2, screen_height))
pygame.display.set_caption("AUTO DRIVING")
clock = pygame.time.Clock()

center = np.array([screen_width // 2, screen_height // 2])
dst_center = np.array([screen_width + screen_width // 2, screen_height // 2])
# 단위 정사각형 좌표 (시계방향으로)


src_pnts = np.random.normal(loc=0.0, scale = 1.0, size=(100,2))
src_pnts = np.stack(src_pnts, axis=-1).reshape(-1, 2)

colors = np.random.randint(0, 256, size=(121, 3))

# 임의의 T
theta = np.radians(7)
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


# 애니메이션 루프
running = True
show_pnts = src_pnts.copy()
T_total = np.eye(3)

while running:
    clock.tick(1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    indices = nearest_neighbor(show_pnts, dst_pnts, distance_threshold = 1)
    valid = indices[indices >= 0]

    matched_src = show_pnts[valid]
    matched_dst = dst_pnts[indices[valid]]

    T_est = SVD_fit(matched_src, matched_dst)
    ones = np.ones((src_pnts.shape[0], 1))
    show_homo = np.hstack([show_pnts, ones])
    show_pnts = (T_est @ show_homo.T).T[:, :2]
    rmse = np.sqrt(np.mean(np.sum((matched_src - matched_dst) ** 2, axis=1)))

    print(rmse)
    if (rmse<0.001):
        print(T_total)
        running = False
    T_total = T_est @ T_total
    screen.fill(ad_util.black)

    draw_shape(show_pnts, colors, center)
    draw_shape(dst_pnts,colors,dst_center)

    pygame.draw.line(screen, ad_util.red, (screen_width // 2, 0), (screen_width // 2, screen_height), 1)
    pygame.draw.line(screen, ad_util.red, (screen_width + screen_width // 2, 0), (screen_width + screen_width // 2, screen_height), 1)
    pygame.draw.line(screen, ad_util.red, (0, screen_height // 2), (screen_width*2, screen_height // 2), 1)
    pygame.display.flip()

pygame.quit()
