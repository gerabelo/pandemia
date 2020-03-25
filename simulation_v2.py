"""
    Uma silumação por contágio
    desenvolvida por geraldo@selvadebits.com.br
    em 20-03-2020

    uso: 
    
        ./python simulation_v2.py <r>
        r: restrição da mobilidade variável entre 0 e 99.
"""

import sys,time,argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from matplotlib.patches import Circle
from matplotlib import animation
from itertools import combinations

class Person:
    def __init__(self, x, y, vx, vy, radius=0.01, styles=None, saude=None, mobilidade=1):
        self.mobilidade = mobilidade
        self.idade = 0
        self.r = np.array((x, y)) #posicao
        self.v = np.array((vx, vy)) #velocidade
        self.radius = radius
        self.massa = self.radius**2
        self.styles = styles
        if not self.styles:
            self.styles = {'edgecolor': 'b', 'facecolor':'b','fill': False}

        self.saude = saude
        if not self.saude:
            self.saude = 0


    @property
    def x(self):
        return self.r[0]
    @x.setter
    def x(self, value):
        self.r[0] = value
    @property
    def y(self):
        return self.r[1]
    @y.setter
    def y(self, value):
        self.r[1] = value
    @property
    def vx(self):
        return self.v[0]
    @vx.setter
    def vx(self, value):
        self.v[0] = value
    @property
    def vy(self):
        return self.v[1]
    @vy.setter
    def vy(self, value):
        self.v[1] = value

    def overlaps(self, other):
        return np.hypot(*(self.r - other.r)) < self.radius + other.radius

    def draw(self, ax):
        circle = Circle(xy=self.r, radius=self.radius, **self.styles)
        ax.add_patch(circle)
        return circle

    def advance(self, dt):
        self.idade += dt*100
        self.r += self.v * dt
        if (self.idade % 30) == 0:
            if self.saude == 1:
                global infectados
                if infectados < 20:    # supondo uma capacidade hospitalar de 20%
                    letalidade = 4  # 4%
                else:
                    letalidade = 20 # 20%
                if np.random.randint(100) > letalidade:
                    global recuperados
                    self.saude = -1
                    self.styles =  {'edgecolor': 'g', 'facecolor':'g','fill': True}
                    recuperados += 1
                    infectados -= 1
                else:
                    
                    global mortos
                    self.saude = -2
                    self.styles =  {'edgecolor': 'k', 'facecolor':'k','fill': True}
                    self.v = 0
                    mortos += 1
                    infectados -= 1

            if self.saude > 0:
                self.saude -= 1


class Simulation:
    PersonClass = Person

    def __init__(self, n, radius=0.01, styles=None, isolation=0):
        self.init_persons(n, radius, styles,isolation)
        self.dt = 0.08

    def place_person(self, rad, styles, pId=None, isolation=0):
        x, y = rad + (2 - 2*rad) * np.random.random(2)
        vr = 0.1 * np.sqrt(np.random.random()) + 0.03
        vphi = 2*np.pi * np.random.random()
        vx, vy = vr * np.cos(vphi), vr * np.sin(vphi)
        if pId == 1:
            person = self.PersonClass(x, y, vx, vy, rad, {'edgecolor': 'r',  'facecolor':'r', 'fill': True},7)
        else:
            if pId < isolation:
                person = self.PersonClass(x, y, 0, 0, rad, styles,0,0)
            else:
                person = self.PersonClass(x, y, vx, vy, rad, styles,0)
        for p2 in self.persons:
            if p2.overlaps(person):
                break
        else:
            self.persons.append(person)
            return True
        return False

    def init_persons(self, n, radius, styles=None,isolation=0):
        try:
            iterator = iter(radius)
            assert n == len(radius)
        except TypeError:
            # r isn't iterable: turn it into a generator that returns the
            # same value n times.
            def r_gen(n, radius):
                for i in range(n):
                    yield radius
            radius = r_gen(n, radius)

        self.n = n
        self.persons = []
        for i, rad in enumerate(radius):
            # Try to find a random initial position for this person.
            while not self.place_person(rad, styles,i,isolation):
                pass

    def change_velocities(self, p1, p2):        
        m1, m2 = p1.massa, p2.massa
        M = m1 + m2
        r1, r2 = p1.r, p2.r
        d = np.linalg.norm(r1 - r2)**2
        v1, v2 = p1.v, p2.v
        u1 = v1 - 2*m2 / M * np.dot(v1-v2, r1-r2) / d * (r1 - r2)
        u2 = v2 - 2*m1 / M * np.dot(v2-v1, r2-r1) / d * (r2 - r1)
        p1.v = u1
        p2.v = u2
        if p1.saude == -2 or p1.mobilidade == 0:
            p1.v = 0
        if p2.saude == -2 or p2.mobilidade == 0:
            p2.v = 0

    def change_saude(self, p1, p2):
        global suscetiveis
        global infectados

        if p1.saude > 0 and p2.saude == 0 or p2.saude == -3:
            p2.saude = 7
            p2.styles = {'edgecolor': 'r', 'facecolor': 'r','fill': True}   
            suscetiveis -= 1
            infectados +=1
     
        elif p2.saude > 0 and p1.saude == 0 or p1.saude == -3:
            p1.saude = 7
            p1.styles = {'edgecolor': 'r', 'facecolor': 'r','fill': True}        
            suscetiveis -= 1
            infectados +=1



    def handle_collisions(self):
        pairs = combinations(range(self.n), 2)
        for i,j in pairs:
            if self.persons[i].overlaps(self.persons[j]):
                if self.persons[j].saude > 0 or self.persons[i].saude > 0:
                    self.change_saude(self.persons[i],self.persons[j])
                self.change_velocities(self.persons[i], self.persons[j])

    def handle_boundary_collisions(self, p):
        if p.x - p.radius < 0:
            p.x = p.radius
            p.vx = -p.vx
        if p.x + p.radius > 2:
            p.x = 2-p.radius
            p.vx = -p.vx
        if p.y - p.radius < 0:
            p.y = p.radius
            p.vy = -p.vy
        if p.y + p.radius > 2:
            p.y = 2-p.radius
            p.vy = -p.vy

    def apply_forces(self):
        """Override this method to accelerate the persons."""
        pass

    def advance_animation(self):
        global era
        global pause
        if era == 1:        
	        time.sleep(10)

        era += 1
    
        global infectados
        if infectados == 0:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            pause = True
            self.report()
            plt.savefig(timestr+".png", dpi=150)
            time.sleep(3)
            return sys.exit()
            
        elif (era % 10) == 0:
            global infectados_v
            global recuperados_v
            global mortos_v
            global suscetiveis_v
            
            # global infectados
            global recuperados
            global mortos
            global suscetiveis

            infectados_v.append(infectados)
            recuperados_v.append(recuperados)
            mortos_v.append(mortos)
            suscetiveis_v.append(suscetiveis)

            self.report()

        for i, p in enumerate(self.persons):
            p.advance(self.dt)
            self.handle_boundary_collisions(p)
            self.circles[i].center = p.r
            self.circles[i].styles = p.styles

        self.handle_collisions()
        self.apply_forces()
        return self.circles

    def advance(self):
        for i, p in enumerate(self.persons):
            p.advance(self.dt)
            self.handle_boundary_collisions(p)
        self.handle_collisions()
        self.apply_forces()

    def init(self):
        self.circles = []
        for person in self.persons:
            self.circles.append(person.draw(self.ax))
        return self.circles

    def animate(self, i):
        self.advance_animation()
        return self.circles

    def setup_animation(self):
        self.fig, self.ax = plt.subplots()
        self.fig2, self.ax2 = plt.subplots()

        for s in ['top','bottom','left','right']:
            self.ax.spines[s].set_linewidth(2)

        self.ax.set_aspect(1)
        self.ax.set_xlim(0, 2)
        self.ax.set_ylim(0, 2)
        self.ax.xaxis.set_ticks([])
        self.ax.yaxis.set_ticks([])

    def save_or_show_animation(self, anim, save, filename='covid19.mp4'):
        if save:
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=5, bitrate=1800,extra_args=["-vcodec", "libx264"])
            anim.save(filename, writer=writer)
        else:
            plt.show()


    def do_animation(self, save=False, interval=1, filename='covid19.mp4'):

        self.setup_animation()
        anim = animation.FuncAnimation(self.fig, self.animate,
                init_func=self.init, frames=5, interval=interval, repeat=True, blit=True)
        self.save_or_show_animation(anim, save, filename)

    def report(self):
        global era
        global infectados_v
        global recuperados_v
        global mortos_v
        global suscetiveis_v

        pal = ["#ff0000", "#00ff00", "#ffffff", "#000000"]

        x = range(1,int(era/10)+1)

        data = pd.DataFrame({'infectados':infectados_v, 'recuperados':recuperados_v,'suscetiveis':suscetiveis_v, 'mortos':mortos_v }, index=x)
 
        data_perc = data.divide(data.sum(axis=1), axis=0)

        self.ax2.stackplot(x, data_perc["infectados"],  data_perc["recuperados"], data_perc["suscetiveis"], data_perc["mortos"], labels=['infectados','recuperados','suscetiveis','mortos'],colors=pal)
        self.ax2.margins(0,0)

        self.fig2.canvas.draw()
        self.fig2.canvas.flush_events()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pandemia Simulação')
    parser.add_argument('mob', help='Mobilidade') # valor entre 0 e 100
    args = parser.parse_args()

    pause = False
    era = 1

    infectados = 1
    suscetiveis = 99
    recuperados = 0
    mortos = 0

    infectados_v = []
    recuperados_v = []
    mortos_v = []
    suscetiveis_v = []


    radii = np.random.random(suscetiveis+infectados)*0.03+0.01
    styles = {'edgecolor': 'C0', 'linewidth': 2, 'fill': None}
    sim = Simulation(suscetiveis+infectados, radii, styles,int(args.mob))
    sim.do_animation(save=False)
