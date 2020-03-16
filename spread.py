#
# Desenvolvido em 15 de março de 2020
# por Geraldo Rabelo  geraldo@selvadebits.com.br
#
import math

f=open("covid19.csv","w+")
f.write("\"weeks\",\"naive\",\"sick\",\"recovered\",\"hospitalized\",\"R0\"\n")

# R0 = [1.6,2.1,2.6,3.1,3.6,4.1] # Os dados observados pelos chineses sugerem um R0 variando de 1,6 a 4,1
R0 = [1.13,1.6,4.1] # pior e melhor cenários

z = .1 # teto estimado para o número de caso

for q in R0:
    vulneraveis         = 4000000*z
    semanas             = 0
    infectados          = 0
    graves              = 0
    recuperados         = 0
    novos_infectados    = 0

    # flag_vulneraveis    = False

    while (vulneraveis > 0 or graves > 1): # enquanto houver vuneráveis ou hospitalizados
        if vulneraveis > 0:
            novos_infectados = round(pow(q,semanas-1)) # progressão geométrica
            if novos_infectados > vulneraveis:
                novos_infectados = vulneraveis

            # if flag_vulneraveis:
            #     vulneraveis = 0

            c = vulneraveis - recuperados
            if c > 0: # número de vulneráveis
                vulneraveis -= recuperados
            else:
                vulneraveis = 0
                # flag_vulneraveis = True # tratamento para o caso em que o número de recuperados é maior que o número de vulneráveis


        else:
            novos_infectados = 0
        
        graves = round(infectados*.05)
        if semanas > 1:
            graves -= round(pow(q,semanas-3)*.03)
            if graves < 0:
                graves = 0
        recuperados = round(infectados*.95)
        infectados -= recuperados
        infectados += novos_infectados

        print(semanas,"\t\t%14d"%vulneraveis,"\t\t%14d"%infectados,"\t\t%14d"%recuperados,"\t\t%13.0f"%graves,"\t\t",q)
        f.write(f"{semanas},{vulneraveis},{infectados},{recuperados},{graves},{q}\n")
            
        semanas += 1