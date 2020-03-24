# Curvas de Contágio por SARS-CoV-2/MERS-CoV
# Desenvolvido em 15 de março de 2020
# por Geraldo Rabelo  geraldo@selvadebits.com.br
#
# As estimativas iniciais de R0 para o SARS-CoV-2 variam de 1,6 a 4,1
# http://cadernos.ensp.fiocruz.br/csp/artigo/999/emergncia-do-novo-coronavrus-sars-cov-2-e-o-papel-de-uma-vigilncia-nacional-em-sade-oportuna-e-efetiva
#
# 2020: o estado do Amazonas possui aproximadamente 1400 leitos UTI (particulares e SUS)
# 2020: a cidade de Manaus possui aproximadamente 2 milhões de habitantes

import math
import json, argparse

def write_json(data, filename='data.json'): 
    with open(filename,'w+') as f: 
        json.dump(data, f, indent=4) 


# casos = '{"pior": [{ "t":"","vulneraveis":"","doentes":"","recuperados":"","graves":""}],"melhor":[{"t":"","vulneraveis":"","doentes":"","recuperados":"","graves":""}]}'
casos = '{"action":[],"noaction":[]}'
j = json.loads(casos)

def coeficiente_contagio(t):
    global t1
    global t2
    global R0
    global Rt

    if t < t1:
        return R0
    elif t > t2:
        return Rt
    else:
        return (R0-Rt)*(.5*math.cos((math.pi/(t2-t1))*(t-t1))+.5)+Rt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='COVID-19 Curva de Contágio')
    parser.add_argument('t1', help='início da intervenção (em semanas)')
    parser.add_argument('t2', help='início do efeito máximo da intervenção (em semanas)')
    parser.add_argument('R0', help='coeficiente de contágio sem intervenção')
    parser.add_argument('Rt', help='coeficiente de contágio desejado')
    parser.add_argument('H', help='capacidade hospitalar')
    parser.add_argument('O', help='output file')

    args = parser.parse_args()

    t1 = int(args.t1)
    t2 = int(args.t2)
    R0 = float(args.R0)
    Rt = float(args.Rt)
    capacidade_hospitalar = int(args.H)
    output = args.O

    z = .1 # limite de contágio da população. variar de .01 a 1
    vulneraveis     = 2000000*z   # vulneráveis
    t               = 0
    doentes         = 1
    mortos          = 0
    doentes_old     = 0
    graves  = 0
    recuperados     = 0           # imunes
    novos_casos     = 0

    while (vulneraveis > 0 or doentes > 1): # enquanto houver vuneráveis ou graves não para a simulação
        q = coeficiente_contagio(t)
        if vulneraveis > 0:
            novos_casos = doentes*q#round(pow(q,t-1)) # progressão geométrica
            if novos_casos > vulneraveis:
                novos_casos = vulneraveis

            c = vulneraveis - recuperados
            if c > 0: # número de vulneráveis
                vulneraveis -= recuperados
            else:
                vulneraveis = 0

        else:
            novos_casos = 0
        
        graves = round(doentes*.05)

        # -- liberação de leitos por óbito
        if t > 1:
            if doentes < capacidade_hospitalar:
                mortos += round(doentes_old*.03)
                graves -= round(doentes_old*.03)
            else:
                mortos += round(doentes_old*.06)
                graves -= round(doentes_old*.06)
            if graves < 0:
                graves = 0
        # --

        recuperados = round(doentes*.95)
        doentes_old = doentes
        doentes -= recuperados
        doentes += novos_casos

        print(t,"\t\t%14d"%vulneraveis,"\t\t%14d"%novos_casos,"\t\t%14d"%doentes,"\t\t%14d"%recuperados,"\t\t%13.0f"%graves,"\t\t",q)
        # print(t,"\t\t%14d"%doentes)
        
        j['action'].append({
            "t" : t,
            "vulneraveis" : vulneraveis,
            "doentes" : doentes,
            "recuperados" : recuperados,
            "graves" : graves,
            "mortos": mortos
        })        

        t += 1
        



    vulneraveis     = 2000000*z   # vulneráveis
    t               = 0
    doentes         = 1
    doentes_old     = 0
    graves          = 0
    mortos          = 0
    recuperados     = 0           # imunes
    novos_casos     = 0

    while (vulneraveis > 0 or doentes > 1): # enquanto houver vuneráveis ou graves não para a simulação
        q = R0
        if vulneraveis > 0:
            novos_casos = doentes*q#round(pow(q,t-1)) # progressão geométrica
            if novos_casos > vulneraveis:
                novos_casos = vulneraveis

            c = vulneraveis - recuperados
            if c > 0: # número de vulneráveis
                vulneraveis -= recuperados
            else:
                vulneraveis = 0

        else:
            novos_casos = 0
        
        graves = round(doentes*.1)

        # -- liberação de leitos por óbito
        if t > 1:
            if doentes < capacidade_hospitalar:
                mortos += round(doentes_old*.03)
                graves -= round(doentes_old*.03)
            else:
                mortos += round(doentes_old*.06)
                graves -= round(doentes_old*.06)
            if graves < 0:
                graves = 0
        # --

        recuperados = round(doentes*.95)
        doentes -= recuperados
        doentes += novos_casos

        print(t,"\t\t%14d"%vulneraveis,"\t\t%14d"%novos_casos,"\t\t%14d"%doentes,"\t\t%14d"%recuperados,"\t\t%13.0f"%graves,"\t\t",q)
        # print(t,"\t\t%14d"%doentes)
        
        j['noaction'].append({
            "t" : t,
            "vulneraveis" : vulneraveis,
            "doentes" : doentes,
            "recuperados" : recuperados,
            "graves" : graves,
            "mortos" : mortos
        })        

        t += 1

    write_json(j,output)