import numpy as np
import pygame
import ad_util

def point_to_segment_distance(px, py, x1, y1, x2, y2):
    A = np.array([px, py])
    B = np.array([x1, y1])
    C = np.array([x2, y2])
    BC = C - B
    BA = A - B
    t = np.dot(BA, BC) / np.dot(BC, BC)
    t = np.clip(t, 0.0, 1.0)
    closest = B + t * BC
    return np.linalg.norm(A - closest)

pygame.init()

white = (255, 255, 255)
red= (255, 0, 0)
blue = (0, 0, 255)
gray = (180, 180, 180)
green = (0, 255, 0)
black = (0, 0, 0)

screen_width = 800 # pixel 단위
screen_height = 800
screen = pygame.display.set_mode((screen_width * 2, screen_height))

ad_rect = pygame.Surface((100, 300), pygame.SRCALPHA)
pygame.draw.rect(ad_rect, green, (0, 0, 100, 300))
rotated_rect = pygame.transform.rotate(ad_rect, 50)
new_rect = rotated_rect.get_rect(center=(500, 500))

pygame.display.set_caption('Auto_Driving')
car_image = pygame.image.load('car.png')
car_image = pygame.transform.scale(car_image, (50, 30))
car_x = 100
car_y = 100
car_angle = 0 # 차 머리 초기 각도
car_rect = car_image.get_rect(center=(car_x, car_y)) # 차 위치 설정
car_speed = 300 # 초당 이동 가능한 픽셀 수
target_x = car_x
target_y = car_y

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

GRID_INTERVAL = 20 # 한 셀의 크기: 20px * 20px
GRID_W, GRID_H = screen_width // GRID_INTERVAL, screen_height // GRID_INTERVAL
grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
ad_util.apply_wall_to_grid(grid, walls, GRID_INTERVAL)
ad_util.apply_margin_to_grid(grid, 2)
path = []
path_index = 0
look_ahead_distance = 5

FPS = 60
clock = pygame.time.Clock()

running = True
i = 0

while running:
    dt = clock.tick(FPS) / 1000
    clock.tick(FPS)
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_grid = (int(mouse_x // GRID_INTERVAL), int(mouse_y // GRID_INTERVAL)) # 마우스 픽셀 기준 좌표를 셀 좌표로 변환
            if event.button == 1:
                path.append(mouse_grid)
    if path and path_index < len(path):
        _x, _y = path[path_index]
        target_x = _x * GRID_INTERVAL + GRID_INTERVAL // 2 # 그리드 셀의 정중앙으로 가게 하기 위함
        target_y = _y * GRID_INTERVAL + GRID_INTERVAL // 2

        dx = target_x - car_x
        dy = target_y - car_y
        dist = np.sqrt(dx ** 2 + dy ** 2)
        car_angle = np.atan2(dy, dx) # arctan dy / dx

        if dist < look_ahead_distance:
            path_index += 1
        else:
            v_x = dx / dist  # 단위 벡터
            v_y = dy / dist
            move_distance = car_speed * dt
            if move_distance > dist:
                car_x = mouse_x
                car_y = mouse_y
            else:
                car_x = car_x + v_x * move_distance
                car_y = car_y + v_y * move_distance

    is_collision = ad_util.check_collision((car_x, car_y), car_angle, 50, 50, walls)

    if is_collision:
        car_speed = 0
        print("충돌")
        screen.fill(red)
    else:
        screen.fill(black)

    rotated_car_image = pygame.transform.rotate(car_image, -np.degrees(car_angle))
    # 회전은 반시계가 + 방향이지만 좌표계는 시계방향이 + 방향임
    new_car_rect = rotated_car_image.get_rect(center=(car_x, car_y))
    screen.blit(rotated_car_image, new_car_rect)

    for wall in walls:
        wall_start_x, wall_start_y, wall_end_x, wall_end_y, wall_thickness = wall
        pygame.draw.line(screen, green, (wall_start_x, wall_start_y), (wall_end_x, wall_end_y), wall_thickness)

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
                elif grid[y, x] == 1:
                    pygame.draw.rect(screen, gray, rect)
                elif grid[y, x] == 2: # margin 그리기
                    pygame.draw.rect(screen, ad_util.light_gray, rect)
                else:
                    pygame.draw.rect(screen, ad_util.gray, rect, 1)

    pygame.display.flip()

    i = (i + 1) % 360

pygame.quit()


