"""
    A COVID-19 simulator 
    developed by geraldo@selvadebits.com.br
    at 20-03-2020
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
    def __init__(self, x, y, vx, vy, radius=0.01, styles=None, health=None):
        """Initialize the person's position, velocity, and radius.

        Any key-value pairs passed in the styles dictionary will be passed
        as arguments to Matplotlib's Circle patch constructor.

        """
        self.idade = 0
        self.r = np.array((x, y)) #posicao
        self.v = np.array((vx, vy)) #velocidade
        self.radius = radius
        self.mass = self.radius**2
        self.styles = styles
        if not self.styles:
            # Default circle styles
            self.styles = {'edgecolor': 'b', 'facecolor':'b','fill': False}

        self.health = health
        if not self.health:
            self.health = 0


    # For convenience, map the components of the person's position and
    # velocity vector onto the attributes x, y, vx and vy.
    @property
    def x(self):
        return self.r[0] #retorna a atual posicao X
    @x.setter
    def x(self, value):
        self.r[0] = value #seta uma posicao X
    @property
    def y(self):
        return self.r[1]
    @y.setter
    def y(self, value):
        self.r[1] = value
    @property
    def vx(self):
        return self.v[0] #retorna a atual velocidade
    @vx.setter
    def vx(self, value):
        self.v[0] = value #seta uma velocidade
    @property
    def vy(self):
        return self.v[1]
    @vy.setter
    def vy(self, value):
        self.v[1] = value

    def overlaps(self, other):
        """Does the circle of this Person overlap that of other?"""
        return np.hypot(*(self.r - other.r)) < self.radius + other.radius

    def draw(self, ax):
        """Add this Person's Circle patch to the Matplotlib Axes ax."""
        circle = Circle(xy=self.r, radius=self.radius, **self.styles)
        ax.add_patch(circle)
        return circle

    def advance(self, dt):
        """Advance the Person's position forward in time by dt."""
        self.idade += dt*100
        self.r += self.v * dt
        if (self.idade % 30) == 0:
            if self.health == 1:
                global doentes
                if np.random.randint(100) > 4:
                    global recuperados
                    self.health = -1
                    self.styles =  {'edgecolor': 'g', 'facecolor':'g','fill': True}
                    recuperados += 1
                    doentes -= 1
                else:
                    
                    global mortos
                    self.health = -2
                    self.styles =  {'edgecolor': 'k', 'facecolor':'k','fill': True}
                    self.v = 0
                    mortos += 1
                    doentes -= 1

            if self.health > 0:
                self.health -= 1


class Simulation:
    """A class for a simple hard-circle molecular dynamics simulation.
    The simulation is carried out on a square domain: 0 <= x < 2, 0 <= y < 2.
    """

    PersonClass = Person

    def __init__(self, n, radius=0.01, styles=None, isolation=0):
        """Initialize the simulation with n Persons with radii radius.

        radius can be a single value or a sequence with n values.

        Any key-value pairs passed in the styles dictionary will be passed
        as arguments to Matplotlib's Circle patch constructor when drawing
        the Persons.

        """

        self.init_persons(n, radius, styles,isolation)
        self.dt = 0.08

    def place_person(self, rad, styles, pId=None, isolation=0):
        # Choose x, y so that the Person is entirely inside the
        # domain of the simulation.
        x, y = rad + (2 - 2*rad) * np.random.random(2)
        # Choose a random velocity (within some reasonable range of
        # values) for the Person.
        vr = 0.1 * np.sqrt(np.random.random()) + 0.03
        vphi = 2*np.pi * np.random.random()
        vx, vy = vr * np.cos(vphi), vr * np.sin(vphi)
        if pId == 1:
            person = self.PersonClass(x, y, vx, vy, rad, {'edgecolor': 'r',  'facecolor':'r', 'fill': True},7)
        else:
            if pId < isolation:
                person = self.PersonClass(x, y, 0, 0, rad, styles,-2)
            else:
                person = self.PersonClass(x, y, vx, vy, rad, styles,0)
        # Check that the Person doesn't overlap one that's already
        # been placed.
        for p2 in self.persons:
            if p2.overlaps(person):
                break
        else:
            self.persons.append(person)
            return True
        return False

    def init_persons(self, n, radius, styles=None,isolation=0):
        """Initialize the n Persons of the simulation.

        Positions and velocities are chosen randomly; radius can be a single
        value or a sequence with n values.

        """

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
        """
        Persons p1 and p2 have collided elastically: update their
        velocities.

        """
        
        m1, m2 = p1.mass, p2.mass
        M = m1 + m2
        r1, r2 = p1.r, p2.r
        d = np.linalg.norm(r1 - r2)**2
        v1, v2 = p1.v, p2.v
        u1 = v1 - 2*m2 / M * np.dot(v1-v2, r1-r2) / d * (r1 - r2)
        u2 = v2 - 2*m1 / M * np.dot(v2-v1, r2-r1) / d * (r2 - r1)
        p1.v = u1
        p2.v = u2
        if p1.health == -2:
            p1.v = 0
        if p2.health == -2:
            p2.v = 0

    def change_health(self, p1, p2):
        """
        Persons p1 and p2 have contacted one another: update their
        healthies.

        """
        global vulneraveis
        global doentes

        if p1.health > 0 and p2.health == 0:
            p2.health = 7
            p2.styles = {'edgecolor': 'r', 'facecolor': 'r','fill': True}   
            vulneraveis -= 1
            doentes +=1
     
        elif p2.health > 0 and p1.health == 0:
            p1.health = 7
            p1.styles = {'edgecolor': 'r', 'facecolor': 'r','fill': True}        
            vulneraveis -= 1
            doentes +=1


    def handle_collisions(self):
        """Detect and handle any collisions between the Persons.

        When two Persons collide, they do so elastically: their velocities
        change such that both energy and momentum are conserved.

        """ 

        # We're going to need a sequence of all of the pairs of persons when
        # we are detecting collisions. combinations generates pairs of indexes
        # into the self.persons list of Persons on the fly.
        pairs = combinations(range(self.n), 2)
        for i,j in pairs:
            if self.persons[i].overlaps(self.persons[j]):
                if self.persons[j].health > 0 or self.persons[i].health > 0:
                    self.change_health(self.persons[i],self.persons[j])
                self.change_velocities(self.persons[i], self.persons[j])

    def handle_boundary_collisions(self, p):
        """Bounce the persons off the walls elastically."""

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
        """Advance the animation by dt, returning the updated Circles list."""        
        global era
        global pause
        
        era += 1
    
        global doentes
        if doentes == 0:
            pause = True
            self.report()
            plt.savefig("simulation.png", dpi=150)
            time.sleep(30)
            return sys.exit()
        elif (era % 10) == 0:
            global doentes_v
            global recuperados_v
            global mortos_v
            global vulneraveis_v
            
            # global doentes
            global recuperados
            global mortos
            global vulneraveis

            doentes_v.append(doentes)
            recuperados_v.append(recuperados)
            mortos_v.append(mortos)
            vulneraveis_v.append(vulneraveis)

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
        """Advance the animation by dt."""
        for i, p in enumerate(self.persons):
            p.advance(self.dt)
            self.handle_boundary_collisions(p)
        self.handle_collisions()
        self.apply_forces()

    def init(self):
        """Initialize the Matplotlib animation."""

        self.circles = []
        for person in self.persons:
            self.circles.append(person.draw(self.ax))
        return self.circles

    def animate(self, i):
        """The function passed to Matplotlib's FuncAnimation routine."""

        self.advance_animation()
        return self.circles

    def setup_animation(self):
        #ax is the box
        #ax2 is the stacked-area chart

        self.fig, self.ax = plt.subplots()
        self.fig2, self.ax2 = plt.subplots()

        for s in ['top','bottom','left','right']:
            self.ax.spines[s].set_linewidth(2)

        self.ax.set_aspect(1)
        self.ax.set_xlim(0, 2)
        self.ax.set_ylim(0, 2)
        self.ax.xaxis.set_ticks([])
        self.ax.yaxis.set_ticks([])

    def save_or_show_animation(self, anim, save, filename='collision.mp4'):
        if save:
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=5, bitrate=1800,extra_args=["-vcodec", "libx264"])
            anim.save(filename, writer=writer)
        else:
            plt.show()


    def do_animation(self, save=False, interval=1, filename='collision.mp4'):
        """Set up and carry out the animation of the molecular dynamics.

        To save the animation as a MP4 movie, set save=True.
        """

        self.setup_animation()
        anim = animation.FuncAnimation(self.fig, self.animate,
                init_func=self.init, frames=5, interval=interval, repeat=True, blit=True)
        self.save_or_show_animation(anim, save, filename)

    def report(self):
        global era
        global doentes_v
        global recuperados_v
        global mortos_v
        global vulneraveis_v

        pal = ["#ff0000", "#00ff00", "#ffffff", "#000000"]

        x = range(1,int(era/10)+1)

        # Make data
        data = pd.DataFrame({'doentes':doentes_v, 'recuperados':recuperados_v,'vulneraveis':vulneraveis_v, 'mortos':mortos_v }, index=x)
 
        # We need to transform the data from raw data to percentage (fraction)
        data_perc = data.divide(data.sum(axis=1), axis=0)

        self.ax2.stackplot(x, data_perc["doentes"],  data_perc["recuperados"], data_perc["vulneraveis"], data_perc["mortos"], labels=['doentes','recuperados','vulneraveis','mortos'],colors=pal)
        self.ax2.margins(0,0)

        self.fig2.canvas.draw()
        self.fig2.canvas.flush_events()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='COVID-19 Simulação')
    parser.add_argument('mob', help='Mobilidade') # valor entre 0 e 100
    args = parser.parse_args()

    pause = False
    era = 1

    doentes = 1
    vulneraveis = 99
    recuperados = 0
    mortos = 0

    doentes_v = []
    recuperados_v = []
    mortos_v = []
    vulneraveis_v = []


    radii = np.random.random(vulneraveis+doentes)*0.03+0.01
    styles = {'edgecolor': 'C0', 'linewidth': 2, 'fill': None}
    sim = Simulation(vulneraveis+doentes, radii, styles,int(args.mob))
    sim.do_animation(save=False)