# 다이익스트라 경로를 따라가는 pure persuit

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
look_ahead_distance = 100

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
ad_util.apply_wall_to_grid(grid,walls,GRID_INTERVAL)
ad_util.apply_margin_to_grid(grid,2)

# path 설정
path =[]
real_path = []
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x >= screen_width:  # 마우스가 오른쪽 맵에 있으면 무시
                    continue
                car_grid = (int(car.x // GRID_INTERVAL), int(car.y // GRID_INTERVAL))
                mouse_grid = (int(mouse_x // GRID_INTERVAL), int(mouse_y // GRID_INTERVAL))
                path = ad_util.ad_dijkstra(grid, car_grid, mouse_grid)
                real_path = [(x * GRID_INTERVAL + GRID_INTERVAL //2, y * GRID_INTERVAL + GRID_INTERVAL //2) for (x, y) in path]
                real_path[-1] = (mouse_x,mouse_y)
                path_index = 0

    if path:
        lookahead_point, dist, next_path_index = car.set_look_ahead_point(real_path, path_index,look_ahead_distance,10)
        path_index = next_path_index

        if lookahead_point:
            target_speed = 50
            target_x = lookahead_point[0]
            target_y = lookahead_point[1]
            target_steer = car.cal_steer(lookahead_point[0], lookahead_point[1])
        else:
            target_x = car.x
            target_y = car.y
            target_speed = 0
            target_steer = 0
            path =[]
            path_index = 0

    car.set_speed(target_speed, dt)
    car.set_steering(target_steer, dt)
    car.update(dt)

    # 충돌 여부 확인(
    is_collision = ad_util.check_collision((car.x, car.y), car.angle, 50, 30, walls)

    if is_collision:
        car_speed = 0
        print("충돌")
        screen.fill(ad_util.red)
    else:
        screen.fill(ad_util.white)

    # 그리기
    ad_util.draw_car(screen,car_image,car.x,car.y,car.angle)

    ad_util.draw_walls(screen,walls)

    car_grid = (int(car.x // GRID_INTERVAL), int(car.y // GRID_INTERVAL))
    target_grid = (int(target_x // GRID_INTERVAL), int(target_y // GRID_INTERVAL))
    ad_util.draw_map(screen, screen_width, grid, GRID_INTERVAL, car_grid, target_grid, path)

    ad_util.draw_info(screen, screen_height, car, target_speed, target_steer, target_x, target_y)

    pygame.display.flip()
pygame.quit()