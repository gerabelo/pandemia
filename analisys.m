%   Criado por Geraldo Rabelo em 11 de abril de 2020
%   geraldo@selvadebits.com.br
%   os arquivos .txt de entrada são gerados pelo analisys.py

clearvars;close all;clc;

estados = ['AC'; 'AL'; 'AM'; 'AP'; 'BA'; 'CE'; 'DF'; 'ES'; 'GO'; 'MA'; 'MG'; 'MS'; 'MT'; 'PA'; 'PB'; 'PE'; 'PI'; 'PR'; 'RJ'; 'RN'; 'RS'; 'RO'; 'RR'; 'SC'; 'SE'; 'SP'; 'TO'];

for i=1:length(estados)
    file = [estados(i,:) '.txt'];
    y = importdata(file);

    x = (0: 1: length(y)-1);
    x_log = (0: 1: 2*(length(y)-1));
    [ Qpre, p, sm, varcov] = fit_logistic(x,y);
    l = p(2)./(1 + exp(-p(3)*(x_log-p(1))));

    x_4pl = (0: 1:3*length(y));
    f_4pl = L4P(x',y')

    fig_4pl = figure('NumberTitle', 'off', 'Name', '[COVID19] Regressão 4PL para a curva de contágio - geraldo@selvadebits.com.br');
    plot(x,y,'o',x_4pl,f_4pl(x_4pl),'r');
    xlabel("dias [pico: "+ceil(f_4pl.C)+", Slope: "+f_4pl.B+"]");
    ylabel("infectados [teto: "+ceil(f_4pl.D)+"]");
    grid on;
    grid minor;
    saveas(fig_4pl,['img\' estados(i,:) '_4PL.png']);
    close(fig_4pl)

    fig_log = figure('NumberTitle', 'off', 'Name', '[COVID19] Regressão Logística para a curva de contágio - geraldo@selvadebits.com.br');
    plot(x,y,'o',x_log,l,'r');
    xlabel("dias [pico: "+ceil(p(1))+", Slope: "+inv(p(3))+"]");
    ylabel("infectados [teto: "+ceil(p(2))+"]");
    grid on;
    grid minor;
    saveas(fig_log,['img\' estados(i,:) '.png']);
    close(fig_log)
end