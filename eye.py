#!/usr/bin/env python

from threading import Thread

import OpenGL.GLUT as glut
from lib.windows import Window

import hy
from lib.osc import Osc
from config import OSC_EYE


class Eye(Thread):
    """Run visuals and show them in Overview and Master windows"""
    def __init__(self):
        Thread.__init__(self)
        self.visuals = {}
        self.osc = Osc()
        self.osc.reciver(OSC_EYE)
        self._stop = False

    def run(self):
        print('starting eye.py')
        glut.glutInit([])

        self.osc.listen('/ear', self.audio)
        self.osc.listen('/visual/new', self.new)

        self.osc.start()
        self.output = Window(self.visuals)

        try:
            while not self._stop:
                self.output.update()
        except KeyboardInterrupt:
            pass

        print('\rstopping eye.py')
        self.osc.stop()

    def stop(self):
        self._stop = True

    def audio(self, path, args):
        for v in self.visuals.values():
            v.box.__dict__[args[0]] = args[1]

    def new(self, path, args):
        name, code = args
        self.visuals[name] = Visual(name, code)


class Visual(object):
    class Box(object):
        def setup(self):
            pass

        def draw(self):
            pass

    def __init__(self, name, code):
        self.name = name

        print 'creating visual'
        self._stack = list()
        self.box = Visual.Box()

        self.load(code)

    def load(self, code):
        try:
            exec(code, self.box.__dict__)
            self.box.setup()
            self._stack.append(code)
        except Exception as e:
            print(e)

    def iteration(self):
        if not self._stack:
            return

        try:
            self.box.draw()
        except Exception as e:
            print(e)
            self._stack = self._stack[:-1]
            if not self._stack:
                print "%s.py is BROKEN" % self.name
            else:
                self.iteration()


if __name__ == "__main__":
    Eye().run()
