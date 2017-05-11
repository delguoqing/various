import random
import cmath
import pyglet
import jacobian
import numpy

WIDTH = 640
HEIGHT = 480
HALFW = WIDTH / 2.0
HALFH = HEIGHT / 2.0

class IKChain(object):
    
    def __init__(self, l):
        self.l = l
        self.n = len(l)
        self.theta = [0] * self.n
        for i in xrange(self.n):
            self.theta[i] = random.uniform(-0.001, 0.001)
        self.jx = []
        for i in xrange(self.n):
            self.jx.append(self.l[i])
            if i - 1 >= 0:
                self.jx[-1] += self.jx[i - 1]
        self.jy = [0] * self.n
        self.solver = None
    
    def set_solver(self, solver):
        self.solver = solver
        
    def solve(self, t, max_iter=10, epsilon=1e-3):
        opt_theta, jx, jy = self.solver(self.l, self.theta, t, max_iter=max_iter, epsilon=epsilon)
        self.jx = jx
        self.jy = jy
        self.theta = opt_theta
       
window = pyglet.window.Window(WIDTH, HEIGHT)

ik_chain = None
target_pos = None

def draw_ik_chain(ik_chain):
    jx = ik_chain.jx
    jy = ik_chain.jy
    pyglet.gl.glColor3f(0.0, 0.0, 1.0)
    pyglet.gl.glLineWidth(2)
    for i in xrange(ik_chain.n):
        if i == 0:
            draw_line((0, 0), (jx[i], jy[i]))
        else:
            draw_line((jx[i - 1], jy[i - 1]), (jx[i], jy[i]))
    pyglet.gl.glColor3f(1.0, 1.0, 1.0)
    pyglet.gl.glPointSize(5)
    for i in xrange(ik_chain.n):
        draw_point((jx[i], jy[i]))
    draw_point((0, 0))
    
def draw_line(pos1, pos2):
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, 
            ("v2f", (pos1[0] + HALFW, pos1[1] + HALFH, pos2[0] + HALFW, pos2[1] + HALFH))
        )

def draw_point(pos):
    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, 
        ("v2f", (pos[0] + HALFW, pos[1] + HALFH))
    )

@window.event
def on_draw():
    window.clear()
    draw_ik_chain(ik_chain)
    
    if target_pos is not None:
        pyglet.gl.glPointSize(10)
        pyglet.gl.glColor3f(1.0, 0.0, 0.0)
        draw_point(target_pos)

def on_update(dt):
    if target_pos is not None:
        d = numpy.array([target_pos[0] - ik_chain.jx[-1], target_pos[1] - ik_chain.jy[-1]])
        dlen = numpy.linalg.norm(d)
        speed = 40.0
        dist = speed * dt
        if dist > dlen:
            t = target_pos
        else:
            d = d / dlen * dist
            t = (ik_chain.jx[-1] + d[0], ik_chain.jy[-1] + d[1])
        ik_chain.solve(t)
        
@window.event
def on_mouse_press(x, y, button, modifiers):
    global target_pos
    target_pos = (x - HALFW, y - HALFH)

def start():
    global ik_chain
    ik_chain = IKChain([20, 20, 40, 60])
    ik_chain.set_solver(jacobian.solve)
    pyglet.clock.schedule_interval(on_update, 1.0 / 60.0)
    
    pyglet.app.run()

start()
    
