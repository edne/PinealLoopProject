import pyglet.gl as gl
import pyglet.image
from pyglet.image.codecs.png import PNGImageDecoder

from core.shapes import solid_polygon, wired_polygon


psolid_memo = {}
pwired_memo = {}
image_memo = {}


def psolid(n, color):
    if n not in psolid_memo:
        psolid_memo[n] = solid_polygon(n)

    vlist = psolid_memo[n]
    vlist.colors = color * (n * 3)
    vlist.draw(gl.GL_TRIANGLES)


def pwired(n, color):
    if n not in pwired_memo:
        pwired_memo[n] = wired_polygon(n)

    vlist = pwired_memo[n]
    vlist.colors = color * n
    vlist.draw(gl.GL_LINE_LOOP)


def image(name):
    if name not in image_memo:
        image_memo[name] = pyglet.image.load("images/%s.png" % name,
                                             decoder=PNGImageDecoder())

    image_memo[name].blit(-1.0, 1.0, 0.0,
                          2.0, 2.0)
