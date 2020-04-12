import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from pymongo import MongoClient

def logistic4(x, A, B, C, D):
    """4PL lgoistic equation."""
    return ((A-D)/(1.0+((x/C)**B))) + D

def residuals(p, y, x):
    """Deviations of data from fitted 4PL curve"""
    A,B,C,D = p
    err = y-logistic4(x, A, B, C, D)
    return err

def peval(x, p):
    """Evaluated value at x with current parameters."""
    A,B,C,D = p
    return logistic4(x, A, B, C, D)

# Make up some data for fitting and add noise
# In practice, y_meas would be read in from a file

client = MongoClient("mongodb://localhost:27017")
db = client['covid19']
fonte = db['dados']

dados = fonte.find({},{'UF':1,'casosAcumulados':1})

for estado in dados:
    s = len(estado['casosAcumulados'])
    x = np.linspace(0,s-1,s)
    y = []

    for d in estado['casosAcumulados']:
         y.append(float(d))    

    with open(estado['UF']+'.txt','w') as output:
        for i in y:
            if i > 0:
                output.write(str(i)+' ')


    p0 = [0, 1, 1, 1]

    try:

        # Fit equation using least squares optimization
        plsq = leastsq(residuals, p0, args=(y, x))

        # Plot results
        plt.plot(x,peval(x,plsq[0]),x,y,'o')
        plt.title('[Least Squares Optimization] Curva de Contágio COVID19 - '+estado['UF']+'\nPico: %.0f (dias);' % plsq[0][2]+' Teto: %.0f (casos);' % plsq[0][3]+' R Naught: %.2f' % plsq[0][1])
        plt.legend(['Ajuste', 'Reais'], loc='upper left')
        plt.savefig(estado['UF']+'.png')
        plt.close()

    except:
        print('erro em ',estado['UF'])