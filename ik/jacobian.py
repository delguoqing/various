import numpy
import cmath
g_jx = None
g_jy = None

def solve(l, theta, t, max_iter=10, epsilon=1e-3):
    pass

def calc_world_positions(l, theta, jx, jy):
    world_mat = []
    n = len(l)
    origin = numpy.matrix([[0], [0], [1]])
    for i in xrange(n):
        c = cmath.cos(theta[i])
        s = cmath.sin(theta[i])
        mat = numpy.matrix([
            [c, s, l[i] * c],
            [-s, c, -l[i] * s],
            [0, 0, 1]
        ])
        if i == 0:
            wmat = mat
        else:
            wmat = world_mat[i - 1] * mat
        world_mat.append(wmat)
        world_pos = numpy.real((wmat * origin).getA1())
        jx[i] = world_pos[0]
        jy[i] = world_pos[1]

def calc_jacobian():
    pass

if __name__ == "__main__":
    lx = [0] * 4
    ly = [0] * 4
    calc_world_positions([1, 1, 2, 3], [cmath.pi / 6.0, -cmath.pi / 6.0, cmath.pi / 2.0, -cmath.pi / 2.0], lx, ly)
    for i in xrange(4):
        # print "%.2f, %.2f" % (lx[i], ly[i])
        print lx[i], ly[i]