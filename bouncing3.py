import numpy as np

def accel_wrapper(x, y, x_vel, y_vel, g):
    def accel(t):
        x_pos = x + x_vel * t
        y_pos = y + y_vel * t + 0.5 * g * t**2
        y_v = y_vel + g * t
        return [x_pos, y_pos, y_v]
    def get_hit_time_for_line(m, c):
        hit_time = [((m*x_vel-y_vel) + np.sqrt((y_vel-m*x_vel)**2 - 4*0.5*g*(y-m*x-c)))/g,
                    ((m*x_vel-y_vel) - np.sqrt((y_vel-m*x_vel)**2 - 4*0.5*g*(y-m*x-c)))/g]
        x_p = [x + x_vel * hit_time[0], x + x_vel * hit_time[1]]
        return [x_p, hit_time]
    def get_y_t_for_x(x_pos):
        hit_time = np.array(x_pos - x)/x_vel
        y_p = y + y_vel * hit_time + 0.5 * g * hit_time**2
        return [y_p, hit_time]
    return [accel, get_y_t_for_x, get_hit_time_for_line]

class Wall():
    def __init__(self, x, y, width, angle, bounce):
        self.x = x
        self.y = y
        self.w = width
        self.angle = angle
        if self.angle == 90:
            self.is_v = True
        else:
            self.is_v = False
        self.bounce = bounce
        self.m = np.tan(self.angle * np.pi / 180)
        self.c = self.y - self.x * self.m
        
        
def get_movement(x, y, xv, yv, g, walls):
    movement_intervals = []
    movement_functions = []
    safety = -1
    while True:
        safety += 1
        cur_acc = accel_wrapper(x, y, xv, yv, g)
        hit_times = []
        for w in walls:
            hit_time = 9999999
            if w.is_v:
                hit = cur_acc[1](w.x)
                if hit[1] > 10e-6 and hit[0] >= w.y and hit[0] <= w.y + w.w:
                    hit_time = hit[1]
            else:
                hit = cur_acc[2](w.m, w.c)
                for i, ht in enumerate(hit[1]):
                    if w.angle < 90:
                        if ht > 10e-6 and hit[0][i] >= w.x and hit[0][i] <= w.x + np.cos(w.angle * np.pi / 180) * w.w:
                            hit_time = ht
                            break
                    else:
                        if ht > 10e-6 and hit[0][i] <= w.x and hit[0][i] >= w.x + np.cos(w.angle * np.pi / 180) * w.w:
                            hit_time = ht
                            break
            hit_times.append(hit_time)
        next_hit = np.argmin(hit_times)
        if hit_times[next_hit] == 9999999:
            next_hit = -1
            break
        if len(movement_intervals) > 0:
            movement_intervals.append([movement_intervals[-1][1],
                                       movement_intervals[-1][1] + hit_times[next_hit]])
        else:
            movement_intervals.append([0, hit_times[next_hit]])
        movement_functions.append(cur_acc[0])
        x, y, yv = cur_acc[0](hit_times[next_hit])
        total_speed = np.sqrt(yv**2 + xv**2)
        in_angle = (180 * (np.arctan2(yv, xv) / np.pi)) % 360
        out_angle = (in_angle + (2 * (walls[next_hit].angle - in_angle))) % 360
        bounce_angle = np.minimum(180 - np.abs(out_angle - in_angle) / 2,
                                  np.abs(out_angle - in_angle) / 2) / 90
        bounce_fac = 1 - (1 - walls[next_hit].bounce) * bounce_angle
        #print(bounce_fac, in_angle, out_angle, bounce_angle)
        #bounce_fac = walls[next_hit].bounce
        xv = bounce_fac * total_speed * np.cos(out_angle * np.pi / 180)
        yv = bounce_fac * total_speed * np.sin(out_angle * np.pi / 180)
        if safety > 100 or (movement_intervals[-1][1] - movement_intervals[-1][0]) < 0.01:
            break
    return movement_intervals, movement_functions

