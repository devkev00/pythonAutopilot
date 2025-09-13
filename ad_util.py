import numpy as np
import pygame

# 색상 정의
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (100, 100, 100)
light_gray = (200,200,200)
green = (0, 255, 0)
black = (0, 0, 0)

############### 2_1 ################
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

def get_rotated_corners(pos, angle, width, height):
    cx, cy = pos
    pnts = np.array([[-width / 2, -height / 2],
            [ width / 2, -height / 2],
            [ width / 2,  height / 2],
            [-width / 2,  height / 2]])

    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])

    r_pnts = (R @ pnts.T).T
    r_pnts = r_pnts + np.array([cx, cy])
    return r_pnts

def check_collision(pos, angle_deg, width, height, walls):
    pnts = get_rotated_corners(pos, angle_deg, width, height)
    for pnt in pnts:
        px, py = pnt
        for wall in walls:
            wall_start_x, wall_start_y, wall_end_x, wall_end_y, wall_thickness = wall
            dist = point_to_segment_distance(px, py, wall_start_x, wall_start_y, wall_end_x, wall_end_y)
            if dist < wall_thickness:
                return True
    return False


############### 2_2 ################
def apply_wall_to_grid(grid, walls, grid_interval):
    for x0, y0, x1, y1, _ in walls:
        steps = int(max(abs(x1 - x0), abs(y1 - y0)))
        for i in range(steps + 1):
            t = i / steps
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            gx = int(x // grid_interval)
            gy = int(y // grid_interval)
            if 0 <= gx < grid.shape[1] and 0 <= gy < grid.shape[0]:
                grid[gy, gx] = 1

def apply_margin_to_grid(grid,margin):
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i,j] == 1:
                for dx in range(-margin, margin + 1):
                    for dy in range(-margin, margin + 1):
                        nx, ny = j + dx, i + dy
                        if 0 <= nx < grid.shape[1] and 0 <= ny < grid.shape[0] and grid[ny,nx]==0:
                            grid[ny, nx] = 2


############### 3_1 ################

def ad_dijkstra(grid, start, goal):
    G_H, G_W = grid.shape
    directions = [(-1, -1), (0, -1), (1, -1),
                  (-1,  0),          (1,  0),
                  (-1,  1), (0,  1), (1,  1)]

    dist = np.full((G_H, G_W), np.inf)
    prev = np.full((G_H, G_W, 2), -1, dtype=int)
    visited = np.zeros((G_H, G_W), dtype=bool)

    sx, sy = start
    dist[sy, sx] = 0
    open_list = [start]

    while open_list:
        # 현재까지 거리(dist)가 가장 짧은 노드 선택
        current = min(open_list, key=lambda c: dist[c[1], c[0]])
        open_list.remove(current)
        x, y = current

        if visited[y, x]:
            continue
        visited[y, x] = True

        if (x, y) == goal:
            break

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < G_W and 0 <= ny < G_H and grid[ny, nx] == 0:
                if visited[ny, nx]:
                    continue
                cost = dx * dx + dy * dy  # 대각선은 2, 직선은 1
                new_dist = dist[y, x] + cost
                if new_dist < dist[ny, nx]:
                    dist[ny, nx] = new_dist
                    prev[ny, nx] = (x, y)
                    if (nx, ny) not in open_list:
                        open_list.append((nx, ny))

    # 경로 복원
    path = []
    x, y = goal
    if dist[y, x] == np.inf:
        return []  # 도달 불가
    while (x, y) != start:
        path.append((x, y))
        x, y = prev[y, x]
    path.append(start)
    path.reverse()
    return path

############### 4_1 ################

class AD_Car:
    def __init__(self, x=0.0, y=0.0, angle=0.0,
                 v=0.0, steer = 0.0, L=30.0,
                 max_steer = np.radians(45), max_speed=100.0,
                 acc = 100, steer_speed = np.radians(20)):
        self.x = x
        self.y = y
        self.angle = angle
        self.v = v
        self.steer = steer
        self.L = L

        self.max_steer = max_steer
        self.max_speed = max_speed
        self.acc = acc
        self.steer_speed = steer_speed

    def set_speed(self, target_speed, dt):
        if self.v < target_speed:
            self.v += self.acc  * dt
            self.v = min(self.v, target_speed)
        elif self.v > target_speed:
            self.v -= self.acc  * dt
            self.v = max(self.v, target_speed)
        else:
            self.v = target_speed

    def set_steering(self, target_steer,dt):
        if self.steer < target_steer:
            self.steer += self.steer_speed  * dt
            self.steer = min(self.steer, target_steer)
        elif self.steer > target_steer:
            self.steer -= self.steer_speed  * dt
            self.steer = max(self.steer, target_steer)
        else:
            self.steer = target_steer

    def update(self, dt):
        """dt 시간 동안 차량 상태 업데이트"""
        self.x += self.v * np.cos(self.angle) * dt
        self.y += self.v * np.sin(self.angle) * dt
        self.angle += (self.v / self.L) * np.tan(self.steer) * dt

    def pose(self):
        """현재 위치 및 방향 반환"""
        return self.x, self.y, self.angle

    ############### 4_2 ################
    def cal_steer(self, t_x, t_y):
        dx = t_x - self.x
        dy = t_y - self.y
        dist = np.sqrt(dx**2 + dy**2)
        target_theta = np.atan2(dy, dx)
        th = np.atan2(np.sin(target_theta - self.angle), np.cos(target_theta - self.angle))
        target_steer = np.atan2(2 * self.L * np.sin(th), dist)
        return target_steer

    ############### 4_3 ################

    def set_look_ahead_point(self, path, path_index,look_ahead_distance, last_dist):
        lookahead_point = None
        dist = 0
        next_path_index = len(path)
        if path and path_index < len(path):
            if path_index == len(path) - 1:
                tx, ty = path[-1]
                dist = np.sqrt((self.x - tx) ** 2 + (self.y - ty) ** 2)
                if dist > last_dist:
                    lookahead_point = (tx, ty)
                    next_path_index = len(path)-1
                else:
                    lookahead_point = None
                    next_path_index = len(path)
            else:
                for i in range(path_index, len(path)):
                    tx, ty = path[i]
                    dist = np.sqrt((self.x - tx)**2 +  (self.y - ty)**2)
                    if  dist> look_ahead_distance:
                        lookahead_point = (tx, ty)
                        next_path_index = i
                        break
        return lookahead_point, dist, next_path_index


def draw_car(screen, car_image, car_x,car_y, car_angle, alpha=255):
    rotated_image = pygame.transform.rotate(car_image, -np.degrees(car_angle))
    rotated_image.set_alpha(alpha)
    new_rect = rotated_image.get_rect(center=(car_x, car_y))
    screen.blit(rotated_image, new_rect)

def draw_walls(screen,walls):
    for wall in walls:
        wall_start_x, wall_start_y, wall_end_x, wall_end_y, wall_thickness = wall
        pygame.draw.line(screen, blue, (wall_start_x, wall_start_y), (wall_end_x, wall_end_y), wall_thickness)

def draw_map(screen, screen_width, grid, interval, car_grid=None, target_grid=None, path=[]):
    GRID_H, GRID_W = grid.shape
    for y in range(GRID_H):
        for x in range(GRID_W):
            rect = pygame.Rect(screen_width + x * interval, y * interval, interval, interval)
            if (x, y) == car_grid:
                pygame.draw.rect(screen, red, rect)
            elif (x, y) == target_grid:
                pygame.draw.rect(screen, blue, rect)
            elif (x,y) in path:
                pygame.draw.rect(screen, green, rect)
            elif grid[y, x] == 1:
                pygame.draw.rect(screen, gray, rect)
            elif grid[y, x] == 2:
                pygame.draw.rect(screen, light_gray, rect)
            else:
                pygame.draw.rect(screen, gray, rect, 1)


def draw_info(screen, screen_height, car, target_speed, target_steer, target_x, target_y):
    font = pygame.font.SysFont(None, 20)
    info_lines = [
        f" Target Position : ({int(target_x)}, {int(target_y)})",
        f" Target Speed     : {target_speed:.2f}",
        f" Target Steering  : {np.degrees(target_steer):.2f} deg",
        f" Car Position     : ({int(car.x)}, {int(car.y)})",
        f" Car Speed        : {car.v:.2f}",
        f" Car Steering     : {np.degrees(car.steer):.2f} deg",
    ]
    for i, line in enumerate(info_lines):
        text_surface = font.render(line, True, green)
        screen.blit(text_surface, (10, screen_height + 10 + i * 24))

############### 5_1 ################

def ray_segment_intersect(ray_origin, ray_direction, wall_start, wall_end):
    x1, y1 = ray_origin
    x2, y2 = x1 + ray_direction[0], y1 + ray_direction[1]
    x3, y3 = wall_start
    x4, y4 = wall_end

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denom == 0:
        return None  # 평행

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        return px, py
    return None

def lidar_scan(lidar_pos, walls, lidar_range, angular_resolution):
    lidar_pnts=[]
    num_rays = 360 * angular_resolution
    for i in range(num_rays):
        angle = lidar_pos[2] + np.radians(i/angular_resolution)
        dir_x = np.cos(angle)
        dir_y = np.sin(angle)
        min_dist = lidar_range
        hit_point = None

        for wall in walls:
            x1, y1, x2, y2, _ = wall
            intersect = ray_segment_intersect(
                (lidar_pos[0], lidar_pos[1]),
                (dir_x * lidar_range, dir_y * lidar_range),
                (x1, y1),
                (x2, y2)
            )
            if intersect:
                dx = intersect[0] - lidar_pos[0]
                dy = intersect[1] - lidar_pos[1]
                dist = np.sqrt(dx**2+dy**2)
                if dist < min_dist:
                    min_dist = dist
                    hit_point = intersect
        if hit_point:
            lidar_pnts.append(hit_point)
    return np.array(lidar_pnts)

def draw_lidar_pnts(screen,lidar_pnts):
    if len(lidar_pnts)>0:
        for pnt in lidar_pnts:
            pygame.draw.circle(screen, blue, (int(pnt[0]), int(pnt[1])), 2)

def lidar_scan_origin_lidar(lidar_pos,lidar_pnts):
    lidar_x,lidar_y,lidar_angle = lidar_pos
    c = np.cos(lidar_angle)
    s = np.sin(lidar_angle)
    T = np.array([[c, -s, lidar_x],
                  [s, c, lidar_y],
                  [0, 0, 1]])
    T_inv = np.linalg.inv(T)

    # Homogenize points (N x 3)
    num_pts = lidar_pnts.shape[0]
    homo_points = np.hstack((lidar_pnts, np.ones((num_pts, 1))))  # Nx3

    # Transform points to lidar frame
    local_pnts = (T_inv @ homo_points.T).T[:,:2]
    return local_pnts

############### 7_1 ################

def icp_2d_rmse(source_points, target_points, init_T, max_iterations = 100, distance_threshold = 50.0, rmse_threshold=1e-2):
    """
    ICP 2D with RMSE-based convergence.
    """
    def nearest_neighbor(src, dst):
        indices = []
        distances = []
        for p in src:
            p = np.array(p)
            d = np.linalg.norm(dst - p, axis=1)
            min_idx = np.argmin(d)
            if d[min_idx] < distance_threshold:
                indices.append(min_idx)
                distances.append(d[min_idx])
            else:
                indices.append(-1)
                distances.append(np.inf)
        return np.array(indices), np.array(distances)

    def best_fit_transform(A, B):
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
        return R, t

    source_points = np.asarray(source_points)
    target_points = np.asarray(target_points)
    src = source_points.copy()
    T_total = init_T.copy()

    R_init = T_total[:2, :2]
    t_init = T_total[:2, 2]
    src = (R_init @ src.T).T + t_init

    for i in range(max_iterations):
        indices, dists = nearest_neighbor(src, target_points)
        valid = indices >= 0

        if np.sum(valid) < 3:
            print(f"Iteration {i}: not enough valid correspondences.")
            break

        matched_src = src[valid]
        matched_dst = target_points[indices[valid]]

        R, t = best_fit_transform(matched_src, matched_dst)
        src = (R @ src.T).T + t

        # Update total transform
        T = np.eye(3)
        T[:2, :2] = R
        T[:2, 2] = t
        T_total = T @ T_total

        # RMSE 계산
        rmse = np.sqrt(np.mean(np.sum((matched_src - matched_dst) ** 2, axis=1)))
        #print(f"Iteration {i}: RMSE = {rmse:.6f}")

        if rmse < rmse_threshold:
            #print(f"Iteration {i}: Converged by RMSE.")
            break

    return T_total, src, rmse

def matrix_to_pose(T):
    dx, dy = T[0, 2], T[1, 2]
    dtheta = np.atan2(T[1, 0], T[0, 0])
    return dx, dy, dtheta

def grid_downsample(lidar_pnts, cell_size=10):
    grid_indices = np.floor(lidar_pnts / cell_size).astype(int)
    down_pnts = (grid_indices+0.5) * cell_size
    unique_pnts = np.unique(down_pnts, axis=0)
    return unique_pnts

def update_global_map(grid_indices, global_map_set):
    new_cells = set(map(tuple, grid_indices))
    global_map_set.update(new_cells)
    return global_map_set
