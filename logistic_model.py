import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from sklearn.metrics import mean_squared_error
from scipy.optimize import curve_fit
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
#%matplotlib inline

def exponential_model(x,a,b,c):
    return a*np.exp(b*(x-c))

def logistic_model(x,a,b,c):
    return c/(1+np.exp(-(x-b)/a))

url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
df = pd.read_csv(url)

df = df.loc[:,['data','totale_casi']]
FMT = '%Y-%m-%dT%H:%M:%S'
date = df['data']
df['data'] = date.map(lambda x : (datetime.strptime(x, FMT) - datetime.strptime("2020-01-01T00:00:00", FMT)).days  )

x = list(df.iloc[:,0])
y = list(df.iloc[:,1])
print(x)
print(y)
print(df['totale_casi'])
fit = curve_fit(logistic_model,x,y,p0=[2,100,20000])

# exp_fit = curve_fit(exponential_model,x,y,p0=[1,1,1])

# errors = [np.sqrt(fit[1][i][i]) for i in [0,1,2]]
a = 3.54
b = 68.00
c = 15968.38
sol = int(fsolve(lambda x : logistic_model(x,a,b,c) - int(c),b))

pred_x = list(range(max(x),sol))

ax = plt.subplot()
ax.margins(0.05) 
plt.rcParams['figure.figsize'] = [7, 7]
plt.rc('font', size=14)
# Real data
plt.scatter(x,y,label="dados reais",color="red")
# Predicted logistic curve
plt.plot(x+pred_x, [logistic_model(i,fit[0][0],fit[0][1],fit[0][2]) for i in x+pred_x], label="modelo logístico" )
# Predicted exponential curve
# plt.plot(x+pred_x, [exponential_model(i,exp_fit[0][0],exp_fit[0][1],exp_fit[0][2]) for i in x+pred_x], label="Exponential model" )
plt.legend()
plt.xlabel("# de dias desde 1 de janeiro 2020")
plt.ylabel("# de infectados")
plt.ylim((min(y)*0.9,c*1.1))
plt.axis([0,150,0,130000])
plt.show()