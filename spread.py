# Curvas de Contágio por SARS-CoV-2/MERS-CoV
# Desenvolvido em 15 de março de 2020
# por Geraldo Rabelo  geraldo@selvadebits.com.br
#
# As estimativas iniciais de R0 para o SARS-CoV-2 variam de 1,6 a 4,1
# http://cadernos.ensp.fiocruz.br/csp/artigo/999/emergncia-do-novo-coronavrus-sars-cov-2-e-o-papel-de-uma-vigilncia-nacional-em-sade-oportuna-e-efetiva
#
# 2020: o Amazonas possui aproximadamente 1400 leitos UTI
# 2020: Manaus possui aproximadamente 2 milhões de habitantes

f=open("covid19.csv","w+")
f.write("\"weeks\",\"naive\",\"sick\",\"recovered\",\"hospitalized\",\"R0\"\n")

# R0 = [1.6,2.1,2.6,3.1,3.6,4.1] # Os dados observados pelos chineses sugerem um R0 variando de 1,6 a 4,1
R0 = [1.029,1.6,4.1] # cenários desejável, com contenção e sem contenção

z = 1 # 100% da população

for q in R0:
    naive         = 2000000*z   # vulneráveis
    week          = 0
    sick          = 0
    hospitalized  = 0
    recovered     = 0           # imunes
    new_cases     = 0

    while (naive > 0 or hospitalized > 1): # enquanto houver vuneráveis ou hospitalizados
        if naive > 0:
            new_cases = round(pow(q,week-1)) # progressão geométrica
            if new_cases > naive:
                new_cases = naive

            c = naive - recovered
            if c > 0: # número de vulneráveis
                naive -= recovered
            else:
                naive = 0


        else:
            new_cases = 0
        
        hospitalized = round(sick*.05)
        # -- liberação de leitos por óbito
        if week > 1:
            hospitalized -= round(pow(q,week-3)*.03) 
            if hospitalized < 0:
                hospitalized = 0
        # --
        recovered = round(sick*.95)
        sick -= recovered
        sick += new_cases

        print(week,"\t\t%14d"%naive,"\t\t%14d"%sick,"\t\t%14d"%recovered,"\t\t%13.0f"%hospitalized,"\t\t",q)
        f.write(f"{week},{naive},{sick},{recovered},{hospitalized},{q}\n")
            
        week += 1