import numpy
import cmath

def solve(l, theta, t, max_iter=10, epsilon=1e-3):
    n = len(l)
    jx = [0] * n
    jy = [0] * n
    opt_theta = numpy.matrix(theta).reshape(n, 1)
    
    step = 1.0
    i = 0
    while i < max_iter:
        #print "step %d" % i
        calc_world_positions(l, opt_theta.getA1(), jx, jy)
        #print "positions:"
        #print jx
        #print jy
        e = (t[0] - jx[-1], t[1] - jy[-1])
        e = numpy.matrix([[e[0]], [e[1]]])
        #print "error:"
        #print numpy.linalg.norm(e)
        if numpy.linalg.norm(e) < epsilon:
            break
        j = calc_jacobian(jx, jy)
        j_val = calc_jacobian_numerical(lambda _theta, _jx, _jy: calc_world_positions(l, _theta, _jx, _jy), opt_theta.getA1(), 1e-2)
        #print "jacobian"
        #print j
        #print "gradient checking"
        #print j_val
        jinv = numpy.linalg.pinv(j)
        dtheta = jinv * e
        #print "dtheta"
        #print dtheta
        #print "verify dtheta"
        #print j * dtheta - e
        opt_theta += step * dtheta
        #print "new theta=", opt_theta
        i += 1
    return opt_theta.getA1(), jx, jy
    
def calc_world_positions(l, theta, jx, jy):
    world_mat = []
    n = len(l)
    origin = numpy.matrix([[0], [0], [1]])
    for i in xrange(n):
        c = cmath.cos(theta[i])
        s = cmath.sin(theta[i])
        mat = numpy.matrix([
            [c, -s, l[i] * c],
            [s, c, l[i] * s],
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

# returns: 2 x n jacobian matrix
def calc_jacobian(jx, jy):
    s = (jx[-1], jy[-1])
    n = len(jx)
    j = []
    for i in xrange(n):
        if i == 0:
            x = s[0]
            y = s[1]
        else:
            x = s[0] - jx[i - 1]
            y = s[1] - jy[i - 1]
        j.append(-y)
        j.append(x)
    j = numpy.matrix(j).reshape(n, 2).T
    return j

# sort of gradient checking
def calc_jacobian_numerical(f, theta, epsilon):
    j = []
    n = len(theta)
    pjx = [0] * n
    pjy = [0] * n
    njx = [0] * n
    njy = [0] * n
    for i in xrange(len(theta)):
        ptheta = list(theta)
        ptheta[i] += epsilon
        f(ptheta, pjx, pjy)
        ntheta = list(theta)
        ntheta[i] -= epsilon
        f(ntheta, njx, njy)
        j.append((pjx[-1] - njx[-1]) / (2 * epsilon))
        j.append((pjy[-1] - njy[-1]) / (2 * epsilon))
    j = numpy.matrix(j).reshape(n, 2).T
    return j
        
if __name__ == "__main__":
    lx = [0] * 4
    ly = [0] * 4
    l = [1, 1, 2, 3]
    t = (0, 4)
    theta = [cmath.pi / 6.0, -cmath.pi / 6.0, cmath.pi / 2.0, -cmath.pi / 2.0]
    calc_world_positions(l, theta, lx, ly)
    for i in xrange(4):
        # print "%.2f, %.2f" % (lx[i], ly[i])
        print lx[i], ly[i]
    j = calc_jacobian(lx, ly)
    print j
    print "pseudo inverse of Jacobian:"
    print numpy.linalg.pinv(j)
    print "start solving ik:"
    opt_theta, jx, jy = solve(l, theta, t, max_iter=10, epsilon=1e-2)
    print "final positions:"
    print jx
    print jy
    print "verify theta:"
    calc_world_positions(l, opt_theta, lx, ly)
    for i in xrange(4):
        # print "%.2f, %.2f" % (lx[i], ly[i])
        print lx[i], ly[i]    