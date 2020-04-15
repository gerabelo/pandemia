'''
    Um modelo SIR basico desenvolvido por Geraldo Rabelo (geraldo@selvadebits.com.br)
    em marco de 2020

    v3:
        como não há informação de R, substituiremos por D
        utiliza dados no MongoDB

    v4:
        recovered data 15/04/2020

    uso:
        ./python SIR.py <N> <beta> <gama> <samples>
'''

import argparse, random, math
import numpy as np
from scipy.integrate import odeint
from pymongo import MongoClient
import matplotlib.pyplot as plt

def calcula_erro(vetor1,vetor2):
    '''
        esta funcao calcula a distancia euclidiana entre dois vetores e
        sera utilizada como funcao fitness, comparando a sequencia gerada pelo individuo com a sequencia desejada (entrada)
    '''
    r = 0
    s = len(vetor2)
    while s > 0:
        try:
            r += math.sqrt(pow((vetor1[s-1]-vetor2[s-1]),2.0))
        except:
            return -1
        s -= 1    
    return r
    

def gerar_individuo(N=200000):
    '''
        esta funcao retorna um vetor contendo dois valores (float) aleatorios como parametros beta e gama utilizados pelo modelo SIR
        como coeficientes de contagio/dia e cura/dia, um valor (int) como S0, e um erro relativo a funcao fitness

        [beta,gama,S0]
    '''
    return [
        random.random()*random.random()*random.random(),#       soma beta
        random.random()*random.random()*random.random(),#       subtrai beta
        random.random()*random.random()*random.random(),#       soma gama
        random.random()*random.random()*random.random(),#       subtrai gama
        random.random()*random.random()*random.random(),#       soma delta
        random.random()*random.random()*random.random(),#       subtrai delta
        N,                              #       S0_max*random.randint(1,9)*pow(10,random.randint(1,9)),
        0.0]

def aptidao(individuo,curva_I_desejada,curva_R_desejada,curva_D_desejada):
    N = individuo[6]
    I0, R0, D0 = 1, 0, 0
    S0 = N - I0 - R0 - D0
    t = np.linspace(0, len(curva_I_desejada), len(curva_I_desejada))
    y0 = S0, I0, R0, D0
    beta  = individuo[0]-individuo[1]
    gama  = individuo[2]-individuo[3]    
    delta = individuo[4]-individuo[5]
    ret = odeint(deriv, y0, t, args=(N, beta, gama, delta))
    S, I, R, D = ret.T
    #utilizo o tamanho do vetor 2 como parametro, na funcao calcula_erro
    return calcula_erro(curva_I_desejada,I) + calcula_erro(curva_R_desejada,R) + calcula_erro(curva_D_desejada,D)


def mutacao(individuo):
    individuo[random.randint(0,5)] -= random.random()
    individuo[7] = 0.0
    return individuo

def imprimir_resultado(dados):
    with open("output.txt", 'a') as outfile:
         outfile.write("\n["+str(dados[0]-dados[1])+","+str(dados[2]-dados[3])+","+str(dados[4]-dados[5])+","+str(dados[6])+","+str(dados[7])+","+args.UF+"]")

def imprimir(populacao):
    for i,individuo in enumerate(populacao):
        print(i,individuo)    

def carregar_amostras(input_file):
    r = []    
    with open(input_file, 'r') as infile:
        dados = infile.readline()   
    dados = dados.split(' ')
    for dado in dados:
        r.append(int(dado))
    return r

def deriv(y, t, N, beta, gamma, delta):
    S, I, R, D = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I - delta * I
    dRdt = gamma * I
    dDdt = delta * I
    return dSdt, dIdt, dRdt, dDdt

def matar(i):
    i[7] = 9e+9

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='SIR Model')
    parser.add_argument('N', help='max population')
    parser.add_argument('G', help='max generations')
    parser.add_argument('UF', help='unidade federativa')
    parser.add_argument('S', help='susceptible population')
    # parser.add_argument('input_R', help='input file for Recovereds')
    args = parser.parse_args()

    client = MongoClient("mongodb://localhost:27017")
    db = client['covid19']
    dados = db['dados']

    populacao = []

    dados = dados.find_one({'UF':args.UF},{'obitosAcumulados':1,'obitosNovos':1,'casosNovos':1,'casosAcumulados':1,'_id':0})

    amostras_I = []
    amostras_R = []
    amostras_D = []

    l = 0

    while l < len(dados["casosNovos"]):
        amostras_I.append(int(dados['casosNovos'][l]))
        amostras_D.append(int(dados['obitosAcumulados'][l]))
        amostras_R.append(int(dados['casosAcumulados'][l])-int(dados['obitosNovos'][l])-int(dados['casosNovos'][l]))
        l += 1

    
    # povoando...
    c = 0
    while c<int(args.N):
        populacao.append(gerar_individuo(int(args.S)))
        c += 1
    
    g = int(args.G)
    while g > 0:
        # aptidao
        for individuo in populacao:
            a = aptidao(individuo,amostras_I,amostras_R,amostras_D)
            if a < 0:
                matar(individuo)
            individuo[7] = a
        # selecionar 20% mais aptos
        populacao.sort(key=lambda x: x[7]) #populacao.sort(key=lambda x: x[3], reverse=True)
        if populacao[0][7] < 900.0:
            break
        s = len(populacao)
        l = int(s*.1) #preserva elite
        while l < s:
            if random.randint(0,9) < 2:
                #mutacao
                populacao[l] = mutacao(populacao[l])
            else:
                #cruzamento
                populacao[l][0] = populacao[random.randint(0,l)][0]+random.random()
                populacao[l][1] = populacao[random.randint(0,l)][1]+random.random()
                populacao[l][2] = populacao[random.randint(0,l)][2]+random.random()
                populacao[l][3] = populacao[random.randint(0,l)][3]+random.random()
                populacao[l][4] = populacao[random.randint(0,l)][4]+random.random()
                populacao[l][5] = populacao[random.randint(0,l)][5]+random.random()
                # populacao[l][2] = populacao[random.randint(0,l)][2]
                populacao[l][7] = 0.0
            l += 1
        g-=1
        print(str(populacao[0][0]-populacao[0][1])+","+str(populacao[0][2]-populacao[0][3])+","+str(populacao[0][4]-populacao[0][5])+","+str(populacao[0][6])+","+str(populacao[0][7])+","+args.UF)
        # print(g,populacao[0])

    imprimir_resultado(populacao[0])

    
    # imprimir(populacao)
    # mutacao(populacao)
    # imprimir(populacao)


    # N = int(args.N)
    # I0, R0 = 1, 0
    # S0 = N - I0 - R0
    # beta, gamma = float(args.beta), float(args.gama)
    # t = np.linspace(0, int(args.samples), int(args.samples))

    # y0 = S0, I0, R0
    # ret = odeint(deriv, y0, t, args=(N, beta, gamma))
    # S, I, R = ret.T

    # print(ret.T)

    # fig = plt.figure(facecolor='w')
    # ax = fig.add_subplot(111, axisbelow=True)
    # ax.plot(t, S/N, 'b', alpha=0.5, lw=2, label='Suscetiveis')
    # ax.plot(t, I/N, 'r', alpha=0.5, lw=2, label='Infectados')
    # ax.plot(t, R/N, 'g', alpha=0.5, lw=2, label='Recuperados')
    # ax.set_xlabel('Tempo /dias')
    # ax.set_ylabel(f'Populacao ({N})')
    # ax.set_ylim(0,1.2)
    # ax.yaxis.set_tick_params(length=0)
    # ax.xaxis.set_tick_params(length=0)
    # ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    # legend = ax.legend()
    # legend.get_frame().set_alpha(0.5)

    # for spine in ('top', 'right', 'bottom', 'left'):
    #     ax.spines[spine].set_visible(False)

    # plt.show()