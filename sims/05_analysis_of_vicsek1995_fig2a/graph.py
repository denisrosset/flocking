import math
import pylab
from scipy import *
import scipy.optimize
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
colors = {40:'k', 100:'r', 400:'g', 1000:'b'}
symbol = {40:'x', 100:'v', 400:'o', 1000:'+'}
lines = load_file('32_analysis.txt')
for N in Ns:
    if N == 40:
        continue
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    d = [line[2] for line in selected]
    err = [line[3] for line in selected]
    pylab.errorbar(etas, d, yerr = err, fmt = symbol[N], color = colors[N], label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Distance $\\widetilde{\\delta}$')
pylab.savefig('graph/distance.eps')

lines = load_file('31_analysis.txt')
pylab.clf()
def floorzero(x):
    return (abs(x) + x)/2.0
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    mean_ = [line[2] for line in selected]
    pylab.plot(etas, mean_, symbol[N], color = colors[N], label = '$N = %d$' % int(N))
    pylab.plot([0, 1], [7.0/8/sqrt(N), 7.0/8/sqrt(N)], '--', color = colors[N])
pylab.legend(loc = 'best')
pylab.ylim([0, 1])
pylab.xlim([0, 1])
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Order parameter $\\eta$')
pylab.savefig('graph/mean.eps')

pylab.clf()
Ls = []
chi_maxs = []
eta_cs = []
print 'N', 'eta_c', 'chi_max'
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    var_ = [line[3] for line in selected]
    p0 = [15.0/64, 100, max(zip(var_, etas))[1], 0.1]
    fitfunc = lambda p, x: p[0] + p[1] * exp(-(x - p[2])**2/(2*p[3]**2))
    errfunc = lambda p, x, y: fitfunc(p, x) - y
    p, success = scipy.optimize.leastsq(errfunc, p0[:], args = (etas, var_))
    Ls.append(sqrt(N/4.0))
    chi_maxs.append(fitfunc(p, p[2]))
    eta_cs.append(p[2])
    print N, p[2], fitfunc(p, p[2])
    pylab.plot(etas, var_, symbol[N], color = colors[N], label = '$N = %d$' % int(N))
    pylab.plot(arange(0, 1, 0.01), fitfunc(p, arange(0, 1, 0.01)), ':', color = colors[N])
pylab.legend(loc = 'best')
pylab.xlim([0, 1])
pylab.plot([0,1],[15.0/64, 15.0/64], '--k')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Fluctuations $\\sigma$')
pylab.savefig('graph/var.eps')
Ls = array(Ls)
fitfunc = lambda p, x: p[0] + x * p[1]
errfunc = lambda p, x, y: fitfunc(p, x) - y
p0 = [1,1]
p, success = scipy.optimize.leastsq(errfunc, p0[:], args = (log(Ls), log(chi_maxs)))
exponent = p[1]
p0 = array([1])
fitfunc1 = lambda p, x: p[0] * x**exponent
errfunc1 = lambda p, x, y: fitfunc1(p, x) - y
p, success = scipy.optimize.leastsq(errfunc1, p0[:], args = (Ls, chi_maxs))
p = [p]
print exponent
pylab.clf()
pylab.loglog(Ls, chi_maxs, 'xk')
pylab.loglog(Ls, fitfunc1(p, Ls), '-k')
pylab.xlabel('System size $L$')
pylab.ylabel('Fluctuations at critical point $\\chi_{max}$')
pylab.savefig('graph/fitvar.eps')

pylab.clf()
fitfunc = lambda p, x: p[0] + x * p[1]
errfunc = lambda p, x, y: fitfunc(p, x) - y
p0 = [0.5,0.3]
ILs = array([1/sqrt(L) for L in Ls])
eta_cs = array(eta_cs)
p, cov_x, infodict, mesg, ier = scipy.optimize.leastsq(errfunc, p0[:], args = (ILs, eta_cs), full_output = True)
chisq=sum(infodict["fvec"]*infodict["fvec"])
dof=len(ILs)-len(p)
pylab.clf()
pylab.plot(ILs, eta_cs, 'xk')
pylab.plot([0, max(ILs)], fitfunc(p, array([0, max(ILs)])), '-k')
print 'Eta_c', p[0], sqrt(cov_x[0][0])*sqrt(chisq/dof)
pylab.xlabel('$L^{-\\frac{1}{2}}$')
pylab.ylabel('Critical noise $\\eta_{c}$')
pylab.savefig('graph/fitetac.eps')


pylab.clf()
for N in Ns:
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    binder = [line[4] for line in selected]
    pylab.plot(etas, binder, symbol[N], color = colors[N], label = '$N = %d$' % int(N))
pylab.plot([0, 1],[1/3.0, 1/3.0], '--', label = 'At $\\eta \\rightarrow 1$')
pylab.legend(loc = 'best')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Binder cumulant $U_L$')
pylab.axis([0, 1, 0.3, 0.7])
pylab.savefig('graph/binder.eps')

lines = load_file('33_analysis.txt')
pylab.clf()
for N in Ns:
    if N == 40:
        continue
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    rho = [line[2] for line in selected]
    pylab.plot(etas, rho, symbol[N], color = colors[N], label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Local density $\\widetilde{\\rho}$')
pylab.savefig('graph/rho.eps')
pylab.clf()

for N in Ns:
    if N == 40:
        continue
    selected = [line for line in lines if line[0] == N]
    etas = [line[1] for line in selected]
    kappa = [line[3] for line in selected]
    pylab.semilogy(etas[1:], kappa[1:], symbol[N], color = colors[N], label = '$N = %d$' % int(N))
pylab.legend(loc = 'best')
pylab.ylim([1, 1000])
pylab.xlabel('Noise $\\eta$')
pylab.ylabel('Interaction time $\\kappa$')
pylab.savefig('graph/kappa.eps')
