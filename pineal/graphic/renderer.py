import logging
from contextlib import contextmanager
from hy.lex import tokenize
from hy.importer import hy_eval
from hy.models import HyList
import pyglet
import pyglet.gl as gl
import pineal.watcher as watcher

log = logging.getLogger(__name__)


def rendering_window(draw, h, w):
    window = pyglet.window.Window(width=w, height=h,
                                  visible=False)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    # gl.glEnable(gl.GL_LINE_SMOOTH)
    # gl.glEnable(gl.GL_POLYGON_SMOOTH)
    # gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
    # gl.glHint(gl.GL_POLYGON_SMOOTH_HINT, gl.GL_NICEST)

    @window.event
    def on_draw():
        pyglet.clock.tick()

        window.clear()
        gl.glLoadIdentity()
        draw()

    pyglet.clock.set_fps_limit(30)
    pyglet.clock.schedule_interval(lambda dt: None, 1.0/30)


@contextmanager
def safety(stack, ns, exec_fn):
    try:
        yield
    except Exception as e:
        log.error(str(e))
        if stack:
            stack.pop()
        if stack:
            exec_fn(stack[-1], ns)


def safe_eval(code, ns, stack, exec_fn):
    with safety(stack, ns, exec_fn):
        exec_fn(code, ns)
        stack.append(code)


def render(file_name):
    if file_name.endswith('.py'):
        def exec_fn(code, ns):
            exec(code, ns)  # in Python2 exec is not a function

    elif file_name.endswith('.hy'):
        def exec_fn(code, ns):
            tokens = HyList(tokenize(code))
            hy_eval(tokens, ns, '__pineal__')

    else:
        raise Exception('Invalid file format')

    with open(file_name) as f:
        initial_code = f.read()

    stack = [initial_code]
    ns = {'__file__': ''}

    safe_eval(initial_code, ns, stack, exec_fn)
    watcher.add_callback(lambda code:
                         safe_eval(code, ns, stack, exec_fn))

    if 'draw' not in ns:
        raise Exception('No draw() function defined')

    def safe_draw():
        with safety(stack, ns, exec_fn):
            ns['draw']()

    rendering_window(safe_draw, 800, 800)
    pyglet.app.run()
