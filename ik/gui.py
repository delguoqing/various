import pyglet

WIDTH = 640
HEIGHT = 480

window = pyglet.window.Window(WIDTH, HEIGHT)

@window.event
def on_draw():
    pass

def start():
    pyglet.app.run()
