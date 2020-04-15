'''
    Um modelo SIR básico desenvolvido por Geraldo Rabelo (geraldo@selvadebits.com.br)
    em março de 2020

    uso:
        ./python SIR.py <N> <beta> <gama> <samples>
            N           (int)       população
            beta        (float)     coeficiente de infecção
            gama        (float)     coeficiente de cura
            samples     (int)       número de amostras/dias
'''
import argparse
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

def deriv(y, t, N, beta, gamma, delta):
    S, I, R, D = y
    dSdt = -beta * S * I / N                            # susceptible
    dIdt = beta * S * I / N - delta*I - gamma * I       # infected
    dRdt = gamma * I                                    # recovered
    dDdt = delta * I                                    # death
    return dSdt, dIdt, dRdt, dDdt


if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='SIR Model')
    parser.add_argument('N', help='Population')
    parser.add_argument('beta', help='the infection\'s daily coefficient')
    parser.add_argument('gama', help='the cure\'s daily coefficient')
    parser.add_argument('delta', help='the death\'s daily coefficient')
    parser.add_argument('samples', help='the number of days')
    args = parser.parse_args()

    N = int(args.N)
    I0, R0, D0 = 1, 0, 0
    S0 = N - I0 - R0 - D0
    beta, gamma, delta = float(args.beta), float(args.gama), float(args.delta)
    t = np.linspace(0, int(args.samples), int(args.samples))

    y0 = S0, I0, R0, D0
    ret = odeint(deriv, y0, t, args=(N, beta, gamma, delta))
    S, I, R, D = ret.T

    print(ret.T)

    fig = plt.figure(facecolor='w')
    ax = fig.add_subplot(111, axisbelow=True)
    ax.plot(t, S/N, 'b', alpha=0.5, lw=2, label='Suscetíveis')
    ax.plot(t, I/N, 'r', alpha=0.5, lw=2, label='Infectados')
    ax.plot(t, R/N, 'g', alpha=0.5, lw=2, label='Recuperados')
    ax.plot(t, D/N, 'k', alpha=0.5, lw=2, label='Mortos')
    ax.set_xlabel('Tempo /dias')
    ax.set_ylabel(f'População ({N})')
    ax.set_ylim(0,1.1)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)

    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)

    plt.show()