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

def rolling_wrapper(x, y, x_vel, y_vel, g, cwall):
    g_small = g * (1 - (np.abs(90 - cwall.angle) / 90))
    g_partial_x = g_small * np.cos(cwall.angle * np.pi / 180)
    g_partial_y = g_small * np.sin(cwall.angle * np.pi / 180)
    def accel(t):
        x_pos = x + x_vel * t + 0.5 * g_partial_x * t**2
        y_pos = y + y_vel * t + 0.5 * g_partial_y * t**2
        y_v = y_vel + g_partial_y * t
        x_v = x_vel + g_partial_x * t
        return [x_pos, y_pos, x_v, y_v]
    def get_y_t_for_x(x_pos):
        hit_time = [(-x_vel + np.sqrt(x_vel**2 - 2 * g_partial_x * (x-x_pos))) / g_partial_x,
                    (-x_vel - np.sqrt(x_vel**2 - 2 * g_partial_x * (x-x_pos))) / g_partial_x]
        y_p = [y + y_vel * hit_time[0] + 0.5 * g_partial_y * hit_time[0]**2,
               y + y_vel * hit_time[1] + 0.5 * g_partial_y * hit_time[1]**2]
        return [y_p, hit_time]
    def get_hit_time_for_line(m, c):
        hit_time = [((m*x_vel-y_vel) + np.sqrt((y_vel-m*x_vel)**2 - 2*(g_partial_y - g_partial_x*m)*(y-m*x-c)))/(g_partial_y-g_partial_x*m),
                    ((m*x_vel-y_vel) - np.sqrt((y_vel-m*x_vel)**2 - 2*(g_partial_y - g_partial_x*m)*(y-m*x-c)))/(g_partial_y-g_partial_x*m)]
        x_p = [x + x_vel * hit_time[0] + 0.5 * g_partial_x * hit_time[0]**2,
               x + x_vel * hit_time[1] + 0.5 * g_partial_x * hit_time[1]**2]
        return [x_p, hit_time]
    _, pot_roll_time = get_y_t_for_x(cwall.x)
    roll_time = 9999999
    for prt in pot_roll_time:
        if prt > 10e-6:
            roll_time = np.minimum(roll_time, prt)
    _, pot_roll_time = get_y_t_for_x(cwall.x + int(cwall.w * np.cos(cwall.angle * np.pi / 180)))
    for prt in pot_roll_time:
        if prt > 10e-6:
            roll_time = np.minimum(roll_time, prt)
    return [accel, get_y_t_for_x, get_hit_time_for_line, roll_time]

class Wall():
    def __init__(self, x, y, width, angle, bounce, roll):
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
        self.is_r = roll
        
        
def get_movement(x, y, xv, yv, g, walls):
    movement_intervals = []
    movement_functions = []
    safety = -1
    rolling = False
    rolling_on = -1
    while True:
        safety += 1
        if rolling:
            cur_acc = rolling_wrapper(x, y, xv, yv, g, walls[rolling_on])
            hit_times = []
            for cw, w in enumerate(walls):
                if cw == rolling_on:
                    hit_times.append(9999999)
                    continue
                hit_time = 9999999
                if w.is_v:
                    hit = cur_acc[1](w.x)
                    if hit[1][0] > 10e-6 and hit[0][0] >= w.y and hit[0][0] <= w.y + w.w:
                        hit_time = hit[1][0]
                    if hit[1][1] > 10e-6 and hit[0][1] >= w.y and hit[0][1] <= w.y + w.w:
                        hit_time = np.minimum(hit[1][1], hit_time)
                else:
                    hit = cur_acc[2](w.m, w.c)
                    for i, ht in enumerate(hit[1]):
                        if w.angle < 90:
                            if ht > 10e-6 and hit[0][i] >= w.x and hit[0][i] <= w.x + np.cos(w.angle * np.pi / 180) * w.w:
                                hit_time = np.minimum(ht, hit_time)
                        else:
                            if ht > 10e-6 and hit[0][i] <= w.x and hit[0][i] >= w.x + np.cos(w.angle * np.pi / 180) * w.w:
                                hit_time = np.minimum(ht, hit_time)
                hit_times.append(hit_time)
            hit_times.append(cur_acc[3])
            next_hit = np.argmin(hit_times)
            if hit_times[next_hit] == 9999999:
                next_hit = -1
                break
            if len(movement_intervals) > 0:
                movement_intervals.append([movement_intervals[-1][1],
                                           movement_intervals[-1][1] + hit_times[next_hit]])
            else:
                movement_intervals.append([0, next_hit])
            movement_functions.append(cur_acc[0])
            x, y, xv, yv = cur_acc[0](hit_times[next_hit])
            if next_hit == len(hit_times) - 1:
                rolling = False
                rolling_on = -1
                if safety > 100 or (movement_intervals[-1][1] - movement_intervals[-1][0]) < 0.001:
                    break
                continue
        else:
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
        if rolling:
            if in_angle >= 180:
                if in_angle >= 270:
                    if out_angle >= in_angle - 180 and out_angle <= in_angle:
                        break
                else:
                    if out_angle <= in_angle - 180 or out_angle >= in_angle:
                        break
            else:
                if in_angle >= 90:
                    if out_angle >= in_angle and out_angle <= in_angle + 180:
                        xv = 0
                        yv = 0
                        continue
                else:
                    if out_angle <= in_angle or out_angle >= in_angle + 180:
                        xv = 0
                        yv = 0
                        continue
        bounce_angle = np.minimum(180 - np.abs(out_angle - in_angle) / 2,
                                  np.abs(out_angle - in_angle) / 2) / 90
        bounce_fac = 1 - (1 - walls[next_hit].bounce) * bounce_angle
        print(bounce_angle)
        if bounce_angle != 90:
            if walls[next_hit].is_r:
                if walls[next_hit].angle < 90 and (in_angle <= walls[next_hit].angle or in_angle >= (walls[next_hit].angle + 180)):
                    rolling = True
                    rolling_on = next_hit
                    if in_angle <= walls[next_hit].angle or in_angle >= walls[next_hit].angle + 270:
                        out_angle = walls[next_hit].angle
                    else:
                        out_angle = walls[next_hit].angle + 180
                    bounce_fac = 1 - bounce_angle
                elif walls[next_hit].angle > 90 and (in_angle >= walls[next_hit].angle and in_angle <= (walls[next_hit].angle + 180)):
                    rolling = True
                    rolling_on = next_hit
                    if in_angle >= walls[next_hit].angle + 90:
                        out_angle = walls[next_hit].angle + 180
                    else:
                        out_angle = walls[next_hit].angle
                    bounce_fac = 1 - bounce_angle
                else:
                    rolling = False
                    rolling_on = -1
            else:
                rolling = False
                rolling_on = -1
        xv = bounce_fac * total_speed * np.cos(out_angle * np.pi / 180)
        yv = bounce_fac * total_speed * np.sin(out_angle * np.pi / 180)
        if safety > 100 or (movement_intervals[-1][1] - movement_intervals[-1][0]) < 0.001:
            break
    return movement_intervals, movement_functions

