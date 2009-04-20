import math
import pylab
fig_width_pt = 380.0  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
golden_mean = (math.sqrt(5)-1.0)/2.0         # Aesthetic ratio
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width*golden_mean      # height in inches
fig_size =  [fig_width,fig_height]
params = {'backend': 'ps',
          'axes.labelsize': 10,
          'text.fontsize': 10,
          'legend.fontsize': 10,
          'xtick.labelsize': 8,
          'ytick.labelsize': 8,
          'text.usetex': True,
          'figure.figsize': fig_size}
pylab.rcParams.update(params)

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
    pylab.errorbar(etas, d, yerr = err, fmt = '.', label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Distance $\\widetilde{\\delta}$')
pylab.savefig('graph/distance.eps')

lines = load_file('31_analysis.txt')
pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    mean_ = [line[2] for line in selected]
    pylab.plot(etas, mean_, '.', label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.ylim([0, 1])
pylab.xlim([0, 1])
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Order parameter $\\eta$')
pylab.savefig('graph/mean.eps')

pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    var_ = [line[3] for line in selected]
    pylab.plot(etas, var_, '.', label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.xlim([0, 1])
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Fluctuations $\\sigma$')
pylab.savefig('graph/var.eps')

pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    binder = [line[4] for line in selected]
    pylab.plot(etas, binder, '.', label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Binder cumulant $U_L$')
pylab.axis([0, 1, 0, 1])
pylab.savefig('graph/binder.eps')

lines = load_file('33_analysis.txt')
pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    rho = [line[2] for line in selected]
    pylab.plot(etas, rho, '.', label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Local density $\\widetilde{\\rho}$')
pylab.savefig('graph/rho.eps')
pylab.clf()

for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    kappa = [line[3] for line in selected]
    pylab.semilogy(etas, kappa, '.', label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Interaction time $\\kappa$')
pylab.savefig('graph/kappa.eps')
