import logging
from contextlib import contextmanager
from math import pi

import pyglet.gl as gl
import pyglet.image
from pyglet.graphics import vertex_list
from pyglet.image.codecs.png import PNGImageDecoder

from pineal.graphic.shapes import solid_polygon, wired_polygon
from pineal.graphic.framebuffer import Framebuffer


log = logging.getLogger(__name__)


_effects = {}


def effect(f):
    '''Effects are the transformations applied to the drawing elements.

    A new effect is defined with a decorator:

    >>> @effect
    ... def my_effect(a, b, c):
    ...     print('before')
    ...     yield
    ...     print('after')

    And then used as a context manager:

    >>> with my_effect(1, 2, 3):
    ...     print('here draw something')
    before
    here draw something
    after

    Or as method of an entity:

    >>> e = Entity(lambda: print('here draw something'))
    >>> e.my_effect(1, 2, 3).draw()
    before
    here draw something
    after

    '''

    @contextmanager
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)

    _effects.update({f.__name__: decorated})
    return decorated


class Entity:
    '''Entity object, a "thing" with a `.draw()` method.

    >>> e = Entity(lambda: print('draw something'))
    >>> e.draw()
    draw something
    '''
    def __init__(self, draw):
        self.draw = draw

    def __getattr__(self, attr):
        fx = _effects[attr]

        def method(*args, **kwargs):
            def new_draw():
                with fx(*args, **kwargs):
                    return self.draw()

            return Entity(new_draw)

        return method


def entity(f):
    '''Decorator to define entities.

    Usage:

    >>> @entity
    ... def my_entity(a, b, c):
    ...     print('draw something', a, b, c)

    >>> my_entity(1, 2, 3).draw()
    draw something 1 2 3
    '''
    def decorated(*args, **kwargs):
        def draw():
            f(*args, **kwargs)

        return Entity(draw)

    return decorated


def make_color(*args):
    '''Convert args in an (r, g, b, a) tuple.

    >>> make_color(1, 0, 0, 0.5)
    (1, 0, 0, 0.5)

    >>> make_color(0, 1, 0)
    (0, 1, 0, 1)

    >>> make_color(0.3, 0.6)
    (0.3, 0.3, 0.3, 0.6)

    TODO: use the first item as index in a palette.

    >>> make_color(0.3)
    (0.3, 0.3, 0.3, 1)

    TODO: from string with hex html notation

    '''

    if len(args) == 4:
        return tuple(args)

    elif len(args) == 3:
        return tuple(args) + (1, )

    elif len(args) == 2:
        v, a = args
        return (v, v, v) + (a, )

    elif len(args) == 1:
        v, = args
        return (v, v, v) + (1, )

    else:
        raise TypeError('Invalid color')


psolid_memo = {}
pwired_memo = {}
image_memo = {}
layer_memo = {}
windows_memo = []


@entity
def polygon(n, color, fill=True):
    if fill:
        if n not in psolid_memo:
            psolid_memo[n] = vertex_list(n*3,
                                         ('v2f/static', solid_polygon(n)),
                                         ('c4f/stream', [1]*4 * 3*n))

        vlist = psolid_memo[n]
        vlist.colors = make_color(*color) * n*3
        vlist.draw(gl.GL_TRIANGLES)
    else:
        if n not in pwired_memo:
            pwired_memo[n] = vertex_list(n,
                                         ('v2f/static', wired_polygon(n)),
                                         ('c4f/stream', [1]*4 * n))

        vlist = pwired_memo[n]
        vlist.colors = make_color(*color) * n
        vlist.draw(gl.GL_LINE_LOOP)


@entity
def image(name):
    if name not in image_memo:
        img = pyglet.image.load("images/%s.png" % name,
                                decoder=PNGImageDecoder())
        image_memo[name] = img
        image_memo[name].blit(-1.0, 1.0, 0.0,
                              2.0, 2.0)


@entity
def layer(name):
    if name in layer_memo:
        layer_memo[name].texture.blit(-1, 1, 0,
                                      2, -2)


@effect
def scale(x, y=None, z=None):
    if y is None:
        y, z = x, x
    elif z is None:
        z = 1

    gl.glPushMatrix()
    gl.glScalef(x, y, z)
    yield
    gl.glPopMatrix()


@effect
def translate(x, y=0, z=0):
    gl.glPushMatrix()
    gl.glTranslatef(x, y, z)
    yield
    gl.glPopMatrix()


@effect
def rotate(angle, axis=(0, 0, 1)):
    gl.glPushMatrix()
    gl.glRotatef(angle * 180 / pi, *axis)
    yield
    gl.glPopMatrix()


@effect
def on_layer(name):
    if name not in layer_memo:
        layer_memo[name] = Framebuffer(800, 800)

    with layer_memo[name]:
        yield


@effect
def window(name, show_fps=False):
    with on_layer(name):
        yield

    if name in windows_memo:
        return

    windows_memo.append(name)
    win = pyglet.window.Window(resizable=True)

    # TODO: hanldle show_fps changed runtime
    if show_fps:
        fps = pyglet.clock.ClockDisplay()

    @win.event
    def on_draw():
        w, h = win.width, win.height
        side = max(w, h)

        win.clear()

        layer(name)\
            .scale(side/2.0, -side/2.0)\
            .translate(w/2, h/2)\
            .draw()

        if show_fps:
            fps.draw()

    @win.event
    def on_close():
        windows_memo.remove(name)

    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED


def stroke_weight(w):
    "OpenGL lines width"
    # TODO: make it an effect
    gl.glLineWidth(w)
