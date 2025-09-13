# 마우스 클릭으로 목표점을 만들고 따라가기

import pygame
import numpy as np
import ad_util

# pygame 초기화
pygame.init()

# 스크린 정의
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width * 2, screen_height))

# 타이틀
pygame.display.set_caption("AUTO DRIVING")

# 자동차
car_image = pygame.image.load("car.png")
car_image = pygame.transform.scale(car_image, (50, 30))
car_x = 100
car_y = 100
car_angle = np.radians(90)
car_speed = 100  # 초다 이동하는 pixel
look_ahead_distance = 5

# 목표점 설정
target_x = car_x
target_y = car_y

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

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_grid = (int(mouse_x // GRID_INTERVAL), int(mouse_y // GRID_INTERVAL))
            if event.button == 1:
                path.append(mouse_grid)
            if event.button == 3:
                path = []
                path_index = 0

    if path and path_index < len(path):
        _x, _y = path[path_index]
        target_x = _x * GRID_INTERVAL + GRID_INTERVAL // 2
        target_y = _y * GRID_INTERVAL + GRID_INTERVAL // 2

        dx = target_x - car_x
        dy = target_y - car_y
        dist = np.sqrt(dx ** 2 + dy ** 2)
        car_angle = np.atan2(dy, dx)

        if dist < look_ahead_distance:
            path_index += 1
        else:
            v_x = dx / dist
            v_y = dy / dist
            move_distance = car_speed * dt

            if move_distance > dist:
                car_x = target_x
                car_y = target_y
            else:
                car_x = car_x + v_x * move_distance
                car_y = car_y + v_y * move_distance


    # 충돌 여부 확인
    is_collision = ad_util.check_collision((car_x, car_y), car_angle, 50, 30, walls)

    if is_collision:
        car_speed = 0
        print("충돌")
        screen.fill(ad_util.red)
    else:
        screen.fill(ad_util.white)

    # 자동차 그리기
    rotated_car_image = pygame.transform.rotate(car_image, -np.degrees(car_angle))
    new_car_rect = rotated_car_image.get_rect(center=(int(car_x), int(car_y)))
    screen.blit(rotated_car_image, new_car_rect)

    # wall 그리기
    for wall in walls:
        wall_start_x, wall_start_y, wall_end_x, wall_end_y, wall_thickness = wall
        pygame.draw.line(screen, ad_util.blue, (wall_start_x, wall_start_y), (wall_end_x, wall_end_y), wall_thickness)

    # 그리드 map 그리기
    car_grid = (int(car_x // GRID_INTERVAL), int(car_y // GRID_INTERVAL))
    mouse_grid = (int(target_x // GRID_INTERVAL), int(target_y // GRID_INTERVAL))
    for y in range(GRID_H):
        for x in range(GRID_W):
            rect = pygame.Rect(screen_width + x * GRID_INTERVAL, y * GRID_INTERVAL, GRID_INTERVAL, GRID_INTERVAL)
            if (x, y) == car_grid:
                pygame.draw.rect(screen, ad_util.red, rect)
            elif (x, y) == mouse_grid:
                pygame.draw.rect(screen, ad_util.blue, rect)
            elif (x,y) in path:
                pygame.draw.rect(screen, ad_util.green, rect)
            elif grid[y, x] == 1:
                pygame.draw.rect(screen, ad_util.gray, rect)
            elif grid[y, x] == 2:
                pygame.draw.rect(screen, ad_util.light_gray, rect)
            else:
                pygame.draw.rect(screen, ad_util.gray, rect, 1)

    pygame.display.flip()
pygame.quit()