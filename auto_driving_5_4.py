# Lidar의 직접 DATA 확인

import pygame
import numpy as np
import ad_util

# pygame 초기화
pygame.init()

# 스크린 정의
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width * 2, screen_height + 200))

# 타이틀
pygame.display.set_caption("AUTO DRIVING")

# 자동차
car_image = pygame.image.load("car.png")
car_image = pygame.transform.scale(car_image, (50, 30))
car = ad_util.AD_Car(100,100,np.radians(90))

target_speed = 0
target_steer = 0

# 목표점 설정
target_x = car.x
target_y = car.y

# 장애물
walls = [
    (5, 5, screen_width-5, 5, 5),
    (5, screen_height-5, screen_width-5, screen_height-5, 5),
    (5, 5, 5, screen_height-5, 5),
    (screen_width-5, 5, screen_width-5, screen_height-5, 5),
    (200, 5, 200, 300, 5),
    (5, 500, 500, 500, 5),
    (500, 200, 500, screen_height-5, 5)
]

# Grid map 만들기
GRID_INTERVAL = 20
GRID_W, GRID_H = screen_width // GRID_INTERVAL, screen_height // GRID_INTERVAL
grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)

# path 설정
path =[]
path_index = 0

# 게임 진행
running = True

# FPS 설정
FPS = 30
clock = pygame.time.Clock()

while running:
    dt = clock.tick(FPS) / 1000.
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            target_speed = min(car.max_speed, target_speed + 10)
        elif keys[pygame.K_DOWN]:
            target_speed = max(-car.max_speed, target_speed - 10)

        elif keys[pygame.K_RIGHT]:
            target_steer = min(car.max_steer, target_steer + np.radians(5))
        elif keys[pygame.K_LEFT]:
            target_steer = max(-car.max_steer, target_steer - np.radians(5))
        elif keys[pygame.K_SPACE]:
            target_speed = 0
            target_steer = 0

    car.set_speed(target_speed,dt)
    car.set_steering(target_steer,dt)
    car.update(dt)

    lidar_pos = (car.x, car.y, car.angle)
    lidar_pnts = ad_util.lidar_scan(lidar_pos, walls, lidar_range = 200, angular_resolution = 1)
    local_lidar_pnts = ad_util.lidar_scan_origin_lidar(lidar_pos, lidar_pnts)

    grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
    if len(local_lidar_pnts)>0:
        for pnt in local_lidar_pnts:
            gx = int((pnt[0] + screen_width // 2) // GRID_INTERVAL)
            gy = int((pnt[1] + screen_height // 2) // GRID_INTERVAL)
            if 0 <= gx < grid.shape[1] and 0 <= gy < grid.shape[0]:
                grid[gy, gx] = 1

    # 충돌 여부 확인
    is_collision = ad_util.check_collision((car.x, car.y), car.angle, 50, 30, walls)

    if is_collision:
        print("충돌")
        screen.fill(ad_util.red)
    else:
        screen.fill(ad_util.black)

    # 그리기
    pygame.draw.circle(screen, ad_util.white, (int(car.x), int(car.y)), 200)
    ad_util.draw_car(screen,car_image,car.x,car.y,car.angle)

    #ad_util.draw_walls(screen,walls)
    ad_util.draw_lidar_pnts(screen,lidar_pnts)

    car_grid = (int(car.x // GRID_INTERVAL), int(car.y // GRID_INTERVAL))
    target_grid = (int(target_x // GRID_INTERVAL), int(target_y // GRID_INTERVAL))
    ad_util.draw_map(screen, screen_width, grid, GRID_INTERVAL)

    ad_util.draw_info(screen, screen_height, car, target_speed, target_steer, target_x, target_y)

    pygame.display.flip()
pygame.quit()