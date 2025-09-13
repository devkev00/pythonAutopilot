# 방향에 맞게 회전하기

import pygame
import numpy as np

# pygame 초기화
pygame.init()

# 색상 정의
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (180, 180, 180)
green = (0, 255, 0)
black = (0, 0, 0)

# 스크린 정의
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# 타이틀
pygame.display.set_caption("AUTO DRIVING")

# 자동차 이미지
car_image = pygame.image.load("car.png")
car_image = pygame.transform.scale(car_image, (50, 30))
car_x = 400
car_y = 400
car_speed = 100 # 초다 이동하는 pixel

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

    screen.fill(white)
    # 회전은 반시계가 + 방향이지만 좌표계는 시계방향이 + 방향임
    rotated_car_image = pygame.transform.rotate(car_image, -np.degrees(car_angle))
    new_car_rect = rotated_car_image.get_rect(center=(int(car_x), int(car_y)))
    screen.blit(rotated_car_image, new_car_rect)

    pygame.display.flip()
pygame.quit()