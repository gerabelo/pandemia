# Pandemia  
Este repositório contem algumas simulações simples da dinamica de contágio influenciada por variações na mobilidade dos indivíduos bem como na agilidade com a qual medidas contentoras são adotadas. 
    
  
  
## Demonstração da importância do distanciamento social por colisão entre particulas com mobilidade variável  

`./python simulation_v2.py 30`  

Quando infectados (vermelho) e suscetíveis (branco) interagem, uma parcela é removida da categoria suscetíveis e colocada na categoria infectados.
Parte dos infectados se curam em um dado intervalo de tempo. Estes são removidos da categoria infectados e colocados na categoria recuperados (verde).  
Outra parte dos infectados morrem devido à doença. Estes são removidos da categoria infectados e colocados na categoria mortos (preto).
Os curados desenvolvem imunidade e, portanto, não são colocados de volta na categoria suscetível.  
  
Exemplos de saída:  

<img width="400" alt="sem contenção" src="https://selvadebits.com.br/img/20200322-144938.png"><img width="400" alt="com contenção" src="https://selvadebits.com.br/img/20200322-215704.png">
  
  
  
## Simulação simples por progreção geométrica com base nos coeficientes de contágios chineses  

`./python spread_v3.py 2 3 4.1 1.2 1400 data.json`
  
Visualização: curva.html  

<img width="400" alt="1 semana de atraso na contenção" src="https://selvadebits.com.br/img/1semana.png"><img width="400" alt="6 semanas de atraso na contenção" src="https://selvadebits.com.br/img/6semanas.png">  
  
  
  
##  Licença  
Todos os arquivos estão disponíveis sob a Licença BSD 3-Clause License.    
  
  
## Colaboradores
geraldo@selvadebits.com.br
