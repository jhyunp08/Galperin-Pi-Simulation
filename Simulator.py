import platform
import time
import numpy as np
PI = np.pi

from tkinter import *
from tkinter import font as tkFont

if platform.system() == "Darwin":
    from tkmacosx import Button
else:
    from tkinter import Button as tkButton


    class Button(tkButton):
        def __init__(self, master=None, cnf={}, **kw):
            kwargs = kw
            if "height" in kw:
                kwargs["height"] = int(kw["height"] / 30)
            if "width" in kw:
                kwargs["width"] = int(kw["width"] / 14)
            tkButton.__init__(self, master, cnf, **kwargs)


def set_default_font():
    def_font = tkFont.nametofont("TkDefaultFont")
    def_font.config(family="Helvetica", size=13)


def itemconfig_(self: Canvas, tagOrId, cnf=None, **kw):
    if tagOrId == None:
        return
    self.itemconfig(tagOrId, cnf, **kw)


class App(Tk):
    def __init__(self, master=None):
        # initialize window
        Tk.__init__(self)
        self.wm_title("Collision Simulator")
        self.geometry("1000x600")
        self.menu = Menu(self)
        self.config(menu=self.menu)
        self.createMenu()

        self.display_modes = {"bright": [{"bg": "#d9d9dd", "fg": "#101010", "wall": "#909095", "sq1": "#fdbb24", "sq2": "#199e91"},
                                         {"bg": "#a0a0a2", "highlightbackground": "#a0a0a0", "highlightthickness": 2,
                                          "fg": "black", "pbut_bg": "gray", "ment_bg": "#a9a9a9", "canvas_bg": "white", "axes": "#888888", "circle": "#aaaaaa", "point":"#0080fd", "line":"#999999"}],
                              "dark1": [{"bg": "gray17", "fg": "white", "wall": "#c0c0c0", "sq1": "#fdf32e", "sq2": "#00cae0"},
                                       {"bg": "#606067", "highlightbackground": "#707070", "highlightthickness": 2,
                                        "fg": "white", "pbut_bg": "gray19", "ment_bg": "gray17", "canvas_bg": "black", "axes": "#bbbbbb", "circle": "white", "point":"#faf0a8", "line":"#b0d9e3"}],
                              "dark2": [{"bg": "gray6", "fg": "white", "wall": "#b2b2b2", "sq1": "#87c7e8", "sq2": "#199e91"},
                                        {"bg": "gray15", "highlightbackground": "#404040", "highlightthickness": 2,
                                         "fg": "white", "pbut_bg": "gray", "ment_bg": "gray9", "canvas_bg": "black", "axes": "#cccccc", "circle": "#b0d9e3", "point":"#efe959", "line":"#999999"}]}
        self.display_mode = "dark2"

        self.sim_win = SimWindow(self)
        self.set_win = SettingWindow(self)

    def createMenu(self):
        fileMenu = Menu(self.menu)
        fileMenu.add_command(label="Exit", command=self.exitProgram)
        self.menu.add_cascade(label="File", menu=fileMenu)

        displayMenu = Menu(self.menu)
        display_mode = Menu(displayMenu)
        display_mode.add_command(label="Bright", command=lambda: self.change_display_mode("bright"))
        display_mode.add_command(label="Dark1", command=lambda: self.change_display_mode("dark1"))
        display_mode.add_command(label="Dark2", command=lambda: self.change_display_mode("dark2"))
        displayMenu.add_cascade(label="Mode", menu=display_mode)
        self.menu.add_cascade(label="Display", menu=displayMenu)

        helpMenu = Menu(self.menu)
        devTools = Menu(helpMenu)
        devTools.add_command(label="test",
                             command=lambda: self.sim_win.start_animation(True))
        helpMenu.add_cascade(label="Developer Tools", menu=devTools)
        self.menu.add_cascade(label="Help", menu=helpMenu)

    def exitProgram(self):
        exit()

    def change_display_mode(self, mode):
        if (self.display_mode == mode):
            return
        self.display_mode = mode
        self.sim_win.style_dict = st_sim = self.display_modes[self.display_mode][0]
        self.set_win.style_dict = st_set = self.display_modes[self.display_mode][1]
        self.sim_win.config(bg=st_sim["bg"])
        self.sim_win.count.config(bg=st_sim["bg"], fg=st_sim["fg"])
        self.sim_win.canvas.config(bg=st_sim["bg"])
        itemconfig_(self.sim_win.canvas, self.sim_win.wall[0], fill=st_sim["wall"], outline=st_sim["wall"])
        itemconfig_(self.sim_win.canvas, self.sim_win.wall[1], fill=st_sim["wall"], outline=st_sim["wall"])
        itemconfig_(self.sim_win.canvas, self.sim_win.sq1, fill=st_sim["sq1"], outline=st_sim["sq1"])
        itemconfig_(self.sim_win.canvas, self.sim_win.sq2, fill=st_sim["sq2"], outline=st_sim["sq2"])
        self.set_win.config(bg=st_set["bg"], highlightbackground=st_set["highlightbackground"],
                    highlightthickness=st_set["highlightthickness"])
        self.set_win.playpauseButton.config(fg=st_set["fg"],
                                  bg=st_set["pbut_bg"],
                                  highlightbackground=st_set["bg"])
        self.set_win.startoverButton.config(fg=st_set["fg"],
                                  bg=st_set["pbut_bg"],
                                  highlightbackground=st_set["bg"])                          
        self.set_win.label_massEntry.config(fg=st_set["fg"], bg=st_set["bg"])
        self.set_win.massEntry.config(fg=st_set["fg"], bg=st_set["ment_bg"])
        self.set_win.canvas.config(bg=st_set["canvas_bg"])
        itemconfig_(self.set_win.canvas, self.set_win.canvas_x, fill=st_set["axes"])
        itemconfig_(self.set_win.canvas, self.set_win.canvas_y, fill=st_set["axes"])
        itemconfig_(self.set_win.canvas, self.set_win.canvas_label_x, fill=st_set["fg"])
        itemconfig_(self.set_win.canvas, self.set_win.canvas_label_y, fill=st_set["fg"])
        itemconfig_(self.set_win.canvas, self.set_win.canvas_circle, outline=st_set["circle"])
        if self.set_win.diagram[0]:
            for point in self.set_win.diagram[0]:
                itemconfig_(self.set_win.canvas, point, fill=st_set["point"], outline=st_set["point"])
            for line in self.set_win.diagram[1]:
                itemconfig_(self.set_win.canvas, line, fill=st_set["line"])
        self.update()



class SimWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, width=700, height=600)
        self.master = master
        self.pack(side=LEFT, fill=BOTH, expand=1)
        self.style_dict = self.master.display_modes[self.master.display_mode][0]
        self.config(bg=self.style_dict["bg"])

        self.run = True
        self.dt = 0.0004
        self.canvas = None
        f = tkFont.Font()
        f.config(family='times', size=20)
        self.count = Label(text="Collisions: 0", width=28, height=4, font=f, bg=self.style_dict["bg"], fg=self.style_dict["fg"])
        self.wall = [None, None]
        self.create_canvas()
        self.count.place(x=450, y=20)

        self.sq1 = None
        self.sq2 = None
        self.m1 = 1
        self.m2 = 100
        self.v1 = 0.0
        self.v2 = 0.0
        self.c = 0

    def create_canvas(self):
        self.canvas = Canvas(self, width=self.cget("width"), height=self.cget("height"),
                             bg=self.cget("bg"), highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=1)
        self.wall[0] = self.canvas.create_rectangle(0, 500, 1500, 1200, fill=self.style_dict["wall"], outline=self.style_dict["wall"])
        self.wall[1] = self.canvas.create_rectangle(0, 0, 75, 500, fill=self.style_dict["wall"], outline=self.style_dict["wall"])

    def start_animation(self, init):
        self.master.set_win.playpauseButton.config(text="Pause", command=self.pause_animation)
        self.master.set_win.update()
        if self.m2 != int(self.master.set_win.massEntry.get()) or init:
            self.m2 = int(self.master.set_win.massEntry.get())
            self.canvas.delete(self.sq1)
            self.canvas.delete(self.sq2)
            self.sq1 = self.canvas.create_rectangle(85, 459, 125, 499, fill=self.style_dict["sq1"], outline=self.style_dict["sq1"])
            self.sq2 = self.canvas.create_rectangle(150, 399, 250, 499, fill=self.style_dict["sq2"], outline=self.style_dict["sq2"])
            self.v1 = 0.0
            self.v2 = -750 * self.dt
            self.c = 0
            self.count.config(text=f"Collisions: {self.c}")
            self.master.set_win.draw_diagram(self.m2)
        while self.run:
            self.canvas.move(self.sq1, self.v1, 0)
            self.canvas.move(self.sq2, self.v2, 0)
            sq1_pos = self.canvas.coords(self.sq1)
            sq2_pos = self.canvas.coords(self.sq2)
            if sq1_pos[0] <= 75:
                self.canvas.move(self.sq1, 76 - sq1_pos[0], 0)
                self.v1 *= -1
                self.c += 1
                self.count.config(text=f"Collisions: {self.c}")
            if sq2_pos[0] <= sq1_pos[2]:
                self.canvas.move(self.sq1,  3 * (sq2_pos[0] - sq1_pos[2] - 1) / 4, 0)
                self.canvas.move(self.sq2, -(sq2_pos[0] - sq1_pos[2] - 1) / 4, 0)
                v1_0 = self.v1
                v2_0 = self.v2
                self.v1 = ((self.m1-self.m2)*v1_0 + 2*self.m2*v2_0)/(self.m1 + self.m2)
                self.v2 = ((self.m2-self.m1)*v2_0 + 2*self.m1*v1_0)/(self.m1 + self.m2)
                self.c += 1
                self.count.config(text=f"Collisions: {self.c}")
            if 0 < self.v1 < self.v2 and sq1_pos[0] >= 600:
                self.pause_animation()

            self.update()
            time.sleep(self.dt)


    def pause_animation(self):
        self.run = False
        self.master.set_win.playpauseButton.config(text="Play", command=self.restart_animation)
        self.master.set_win.update()

    def restart_animation(self):
        self.run = True
        self.start_animation(False)
        self.master.set_win.playpauseButton.config(text="Pause", command=self.pause_animation)
        self.master.set_win.update()


class SettingWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, width=300)
        self.master = master
        self.pack(side=RIGHT, fill=Y, expand=0)
        self.style_dict = self.master.display_modes[self.master.display_mode][1]
        self.config(bg=self.style_dict["bg"], highlightbackground=self.style_dict["highlightbackground"],
                    highlightthickness=self.style_dict["highlightthickness"])

        self.playpauseButton = Button(self,
                                  text="Play",
                                  width=60,
                                  height=30,
                                  fg=self.style_dict["fg"],
                                  bg=self.style_dict["pbut_bg"],
                                  highlightbackground=self.style_dict["bg"],
                                  command=lambda: self.master.sim_win.start_animation(True)
                                  )
        self.playpauseButton.place(x=10, y=10)
        self.startoverButton = Button(self,
                                  text="Reset",
                                  width=60,
                                  height=30,
                                  fg=self.style_dict["fg"],
                                  bg=self.style_dict["pbut_bg"],
                                  highlightbackground=self.style_dict["bg"],
                                  command=lambda: self.master.sim_win.start_animation(True)
                                  )
        self.startoverButton.place(x=75, y=10)

        self.label_massEntry = Label(self, text="mass:", fg=self.style_dict["fg"], bg=self.style_dict["bg"])
        self.label_massEntry.place(x=10, y=60)
        self.massEntry = Entry(self, width=15, fg=self.style_dict["fg"], bg=self.style_dict["ment_bg"])
        self.massEntry.insert(0, "100")
        self.massEntry.place(x=50, y=58)

        self.canvas = Canvas(self, width=280, height=280,
                             bg=self.style_dict["canvas_bg"], highlightthickness=0)
        self.canvas.place(x=8, y=310)
        self.diagram = [[], []]
        self.canvas_x = self.canvas.create_line(140, 0, 140, 280, fill=self.style_dict["axes"])
        self.canvas_y = self.canvas.create_line(0, 140, 280, 140, fill=self.style_dict["axes"])
        self.canvas_circle = self.canvas.create_oval(15, 15, 265, 265, outline=self.style_dict["circle"])
        f = tkFont.Font()
        f.config(family='times', size=9)
        self.canvas_label_x = self.canvas.create_text(257, 150, font=f, text="\u221a(m1)v1", fill=self.style_dict["fg"])
        self.canvas_label_y = self.canvas.create_text(158, 10, font=f, text="\u221a(m2)v2", fill=self.style_dict["fg"])

    def draw_diagram(self, m2):
        if self.diagram[0]:
            for point in self.diagram[0]:
                self.canvas.delete(point)
            for line in self.diagram[1]:
                self.canvas.delete(line)
        theta = 2 * np.arctan(np.sqrt(1 / m2))
        i = 0
        colls = []
        points = []
        while i * theta <= PI:
            colls.append(-i)
            colls.append(i)
            i += 1
        i -= 1
        if (2 * i + 1) * theta <= 2 * PI:
            colls.append(-i - 1)
        for coll in colls[1:]:
            points.append((140 + 125 * np.sin(coll * theta), 140 + 125 * np.cos(coll * theta)))
        for point in points:
            p = self.canvas.create_oval(point[0]- 2, point[1]- 2, point[0]+2, point[1]+2, fill=self.style_dict["point"], outline=self.style_dict["point"])
            self.diagram[0].append(p)
        for i in range(len(points)-1):
            l = self.canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=self.style_dict["line"])
            self.diagram[1].append(l)
        print(f'm2/m1={m2}: estimated \u03a0={sum(1 for p in range(len(points)) if points[p] != points[p-1]) - 1}')
        self.update()


if __name__ == "__main__":
    app = App()
    set_default_font()
    app.mainloop()
