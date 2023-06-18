import numpy as np
import bouncing3 as bouncing
import tkinter as tk
import matplotlib.pyplot as plt


class BALL(tk.Frame):
    def __init__(self, parent, canvas, ball, walls, speed=10):
        tk.Frame.__init__(self, parent, width=500, height=100)
        self.parent = parent
        self.canvas = canvas
        self.ball = ball
        self.speed = speed
        self.walls = walls
        # Start
        self.submit_Start = tk.Button(self, text="Start", command = self.start)
        self.submit_Start.pack(side="right")
        self.submit_Start.place(y=5,x=5,height=30, width=100)
        # Stop
        self.submit_Stop = tk.Button(self, text="Stop", command = self.stop)
        self.submit_Stop.pack(side="right")
        self.submit_Stop.place(y=5,x=105,height=30, width=100)
        # Continue
        self.submit_Continue = tk.Button(self, text="Continue", command = self.continue_game)
        self.submit_Continue.pack(side="right")
        self.submit_Continue.place(y=5,x=205,height=30, width=100)
        # Reset
        self.submit_reset = tk.Button(self, text="Reset", command = self.reset)
        self.submit_reset.pack(side="right")
        self.submit_reset.place(y=5,x=305,height=30, width=100)
        # X_Pos
        self.Label_X = tk.Label(self, text="X:", anchor="w")
        self.entry_X = tk.Entry(self)
        self.Label_X.pack(side="left")
        self.entry_X.pack(side="left", padx=20)
        self.Label_X.place(y=35,x=5,height=30, width=50)
        self.entry_X.place(y=35,x=55,height=30, width=50)
        # Z_Pos
        self.Label_Z = tk.Label(self, text="Z:", anchor="w")
        self.entry_Z = tk.Entry(self)
        self.Label_Z.pack(side="left")
        self.entry_Z.pack(side="left", padx=20)
        self.Label_Z.place(y=65,x=5,height=30, width=50)
        self.entry_Z.place(y=65,x=55,height=30, width=50)
        # X_Vel
        self.Label_Xv = tk.Label(self, text="Vel_X:", anchor="w")
        self.entry_Xv = tk.Entry(self)
        self.Label_Xv.pack(side="left")
        self.entry_Xv.pack(side="left", padx=20)
        self.Label_Xv.place(y=35,x=105,height=30, width=50)
        self.entry_Xv.place(y=35,x=155,height=30, width=50)
        # Z_Vel
        self.Label_Zv = tk.Label(self, text="Vel_Z:", anchor="w")
        self.entry_Zv = tk.Entry(self)
        self.Label_Zv.pack(side="left")
        self.entry_Zv.pack(side="left", padx=20)
        self.Label_Zv.place(y=65,x=105,height=30, width=50)
        self.entry_Zv.place(y=65,x=155,height=30, width=50)
        # G
        self.Label_g = tk.Label(self, text="g:", anchor="w")
        self.entry_g = tk.Entry(self)
        self.Label_g.pack(side="left")
        self.entry_g.pack(side="left", padx=20)
        self.Label_g.place(y=35,x=205,height=30, width=50)
        self.entry_g.place(y=35,x=255,height=30, width=50)
        # Vals
        self.movement_interval = []
        self.movement_func = []
        self.start_pos = [20, 20]
        self.pos = [20, 20]
        self.g = 9.81
        self.cur_time = 0
        self.cur_movement_num = 0
        self.stopped = True
        self.started = False
        self.calculated = False
        # Defaul vals
        self.entry_X.insert(0, 380)
        self.entry_Z.insert(0, 300)
        self.entry_Xv.insert(0, -490)
        self.entry_Zv.insert(0, 150)
        self.entry_g.insert(0, -200)
        
    def reset(self):
        #print(self.pos, self.start_pos)
        if self.stopped:
            self.movement_interval = []
            self.movement_func = []
            self.cur_time = 0
            self.cur_movement_num = 0
            self.stopped = True
            self.started = False
            self.calculated = False
            #print(self.start_pos[0] - self.pos[0], self.start_pos[1] - self.pos[1])
            self.canvas.move(self.ball, self.start_pos[0] - self.pos[0], self.start_pos[1] - self.pos[1])
            self.pos = self.start_pos
        
    def stop(self):
        self.stopped = True
        
    def continue_game(self):
        if self.started and self.stopped:
            self.stopped = False
            self.apply_movement()
        
    def apply_movement(self):
        if not self.stopped:
            if self.cur_time > self.movement_interval[self.cur_movement_num][1]:
                #print(self.cur_time, self.cur_movement_num, self.movement_interval)
                self.cur_movement_num += 1
                if len(self.movement_interval) <= self.cur_movement_num:
                    self.stopped = True
                    self.started = False
                    return
            pos = self.movement_func[self.cur_movement_num](self.cur_time-self.movement_interval[self.cur_movement_num][0])
            pos = [pos[0] + 10, 400 - pos[1]]
            self.canvas.move(self.ball, pos[0] - self.pos[0], pos[1] - self.pos[1])
            self.pos = pos
            self.cur_time += self.speed/1000
            self.parent.after(self.speed, self.apply_movement)
        
    def start(self):
        try:
            x = int(self.entry_X.get())
            z = int(self.entry_Z.get())
            x_vel = int(self.entry_Xv.get())
            z_vel = int(self.entry_Zv.get())
            g = int(self.entry_g.get())
            self.start_pos = [10 + x, 400 - z]
            self.g = g
            self.reset()
            self.started = True
            self.stopped = False
            self.movement_interval,\
                self.movement_func = bouncing.get_movement(x, z, x_vel, z_vel, g, self.walls)
            print(self.movement_interval)
            print(self.movement_func)
            #plt.figure()
            #for mii, mi in enumerate(self.movement_interval):
            #    plt.scatter([self.movement_func[mii](ct - mi[0])[0] for ct in np.arange(mi[0], mi[1], 0.01)], [self.movement_func[mii](ct - mi[0])[1] for ct in np.arange(mi[0], mi[1], 0.01)])
            #plt.show()
            self.calculated = True
            self.apply_movement()
        except ValueError:
            self.fail()
            
    def fail(self):
        pass
            
                
if __name__ == "__main__":
    colors_dcit = {2.0: "blue", 1.0: "green", 0.9: "green", 0.8: "green", 0.7: "orange",
                   0.6: "green", 0.5: "orange", 0.4: "orange", 0.3: "red",
                   0.2: "red", 0.1: "red", 0.0: "darkred"}
    
    ws1 = bouncing.Wall(250, 0, 50, 0, 2.0) # 2.0
    ws2 = bouncing.Wall(0, 0, 400, 90, 0.9) # 0.9
    ws3 = bouncing.Wall(400, 0, 400, 90, 0.9) # 0.9
    ws4 = bouncing.Wall(0, 400, 400, 0, 0.9) # 0.9
    w5 = bouncing.Wall(50, 200, 100, 45, 1) # 1
    w6 = bouncing.Wall(150, 100, 50, 0, 0.9) # 0.9
    w7 = bouncing.Wall(200, 200, 100, 120, 0.9) # 0.9
    w8 = bouncing.Wall(300, 300, 80, 150, 0.9) # 0.9
    w9 = bouncing.Wall(300, 100, 100, 30, 0.8) # 0.8
    w10 = bouncing.Wall(50, 50, 100, 60, 0.9) # 0.9
    ws5 = bouncing.Wall(300, 0, 100, 0, 0.4) # 0.4
    ws6 = bouncing.Wall(0, 0, 250, 0, 0.1) # 0.1
    walls = [ws1, ws2, ws3, ws4, w5, w6, w7, w8, w9, w10, ws5, ws6]
    """
    # Random walls --------------------------------------- #
    ws1 = bouncing.Wall(200, 0, 100, 0, 0.9)
    ws2 = bouncing.Wall(0, 0, 400, 90, 0.9)
    ws3 = bouncing.Wall(400, 0, 400, 90, 0.9)
    ws4 = bouncing.Wall(0, 400, 400, 0, 0.9)
    ws5 = bouncing.Wall(300, 0, 100, 0, 0.1)
    ws6 = bouncing.Wall(0, 0, 200, 0, 0.1)
    walls = [ws1, ws2, ws3, ws4, ws5, ws6]
    rand_walls = 10
    for rwi in range(rand_walls):
        walls.append(bouncing.Wall(np.random.randint(10, 300), np.random.randint(10, 300), np.random.randint(10, 100), np.random.randint(0, 180), np.around(0.1 * np.random.randint(0, 10), 1)))
    # Random walls end------------------------------------ #
    """
    lw = 2
    root = tk.Tk()
    root.title("Ball")
    root.resizable(False,False)
    canvas = tk.Canvas(root, width = 420, height = 420)
    canvas.pack()
    # x,y x,y
    for w in walls:
        x_len = int(w.w * np.cos(w.angle * np.pi / 180))
        y_len = int(w.w * np.sin(w.angle * np.pi / 180))
        canvas.create_line(w.x + 10, 410 - w.y, w.x + 10 + x_len, 410 - (w.y + y_len), fill=colors_dcit[w.bounce], width=lw)
    ball = canvas.create_oval(20,20,30,30, fill="red")
    
    app=BALL(parent=root, canvas=canvas, ball=ball, walls=walls)
    app.pack(fill="both", expand=True)
    root.mainloop()