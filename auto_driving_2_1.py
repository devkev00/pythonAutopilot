# 장애물 만들기
# 장애물과 충돌 체크하기

import pygame
import numpy as np
import ad_util

# pygame 초기화
pygame.init()

# 스크린 정의
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# 타이틀
pygame.display.set_caption("AUTO DRIVING")

# 자동차
car_image = pygame.image.load("car.png")
car_image = pygame.transform.scale(car_image, (50, 30))
car_x = 400
car_y = 400
car_speed = 100 # 초다 이동하는 pixel

#장애물
walls = [
    (5, 5, screen_width-5, 5, 5),
    (5, screen_height-5, screen_width-5, screen_height-5, 5),
    (5, 5, 5, screen_height-5, 5),
    (screen_width-5, 5, screen_width-5, screen_height-5, 5),
    (200, 5, 200, 300, 5),
    (5, 500, 500, 500, 5),
    (500, 200, 500, screen_height-5, 5)
]

# 게임 진행
running = True

# FPS 설정
FPS = 30
clock = pygame.time.Clock()

i = 0
while running:
    dt = clock.tick(FPS)/1000.
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - car_x
    dy = mouse_y - car_y
    dist = np.sqrt(dx**2 + dy**2)

    car_angle = np.atan2(dy, dx)

    if dist > 0:
        v_x = dx / dist
        v_y = dy / dist
        move_distance = car_speed * dt

        if move_distance > dist:
            car_x = mouse_x
            car_y = mouse_y
        else:
            car_x = car_x + v_x * move_distance
            car_y = car_y + v_y * move_distance

    # 충돌 여부 확인
    is_collision = ad_util.check_collision((car_x,car_y), car_angle, 50, 30, walls)

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

    pygame.display.flip()
pygame.quit()