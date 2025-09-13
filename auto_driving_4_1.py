# 아커만 조향 모델
# 자동차의 움직임을 Class로 정의
# 그리는 것들 함수화

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
ad_util.apply_wall_to_grid(grid,walls,GRID_INTERVAL)
ad_util.apply_margin_to_grid(grid,2)

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

    # 충돌 여부 확인
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