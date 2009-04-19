import pylab
def load_file(filename):
    lines = open(filename, 'rt').readlines()
    lines = [line.split(' ') for line in lines if line.find('nan') == -1 and line.find('N') == -1]
    lines = [[float(el) for el in line] for line in lines]
    return lines
Ns = [40, 100, 400, 1000]

lines = load_file('32_analysis.txt')
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    d = [line[2] for line in selected]
    err = [line[3] for line in selected]
    pylab.errorbar(etas, d, yerr = err, fmt = '.', label = str(N))
pylab.legend(loc = 'best')
pylab.savefig('graph/distance.png')

lines = load_file('31_analysis.txt')
pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    mean_ = [line[2] for line in selected]
    pylab.plot(etas, mean_, '.', label = str(N))
pylab.legend(loc = 'best')
pylab.savefig('graph/mean.png')

pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    var_ = [line[3] for line in selected]
    pylab.plot(etas, var_, '.', label = str(N))
pylab.legend(loc = 'best')
pylab.savefig('graph/var.png')

pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    binder = [line[4] for line in selected]
    pylab.plot(etas, binder, '.', label = str(N))
pylab.legend(loc = 'best')
pylab.savefig('graph/binder.png')

lines = load_file('33_analysis.txt')
pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    rho = [line[2] for line in selected]
    pylab.plot(etas, rho, '.', label = str(N))
pylab.legend(loc = 'best')
pylab.savefig('graph/rho.png')
pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    kappa = [line[3] for line in selected]
    pylab.semilogy(etas, kappa, '.', label = str(N))
pylab.legend(loc = 'best')
pylab.savefig('graph/kappa.png')
