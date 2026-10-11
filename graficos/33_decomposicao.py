"""Decomposição clássica de série temporal: tendência + sazonalidade semanal + resíduo."""
from comum import COR, br, np, olist, pd, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Tempo", nome="Decomposição de série temporal",
            pergunta="Quanto da variação diária das vendas é tendência, quanto é dia da semana e quanto é imprevisível?",
            quando="Separar os componentes de uma série antes de modelar ou de interpretar picos e quedas.")


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & (d.compra >= "2017-03-01") & (d.compra < "2018-08-01")]
    y = d.groupby(d.compra.dt.normalize()).size().asfreq("D", fill_value=0).astype(float)
    # Decomposição multiplicativa clássica, implementada passo a passo:
    tendencia = y.rolling(7, center=True).mean()                                   # 1) média móvel centrada de 7 dias
    razao = y / tendencia                                                          # 2) remove a tendência
    sazonal_dia = razao.groupby(razao.index.dayofweek).mean()                      # 3) média por dia da semana
    sazonal_dia = sazonal_dia / sazonal_dia.mean()                                 #    normalizada para média 1
    sazonal = pd.Series(y.index.dayofweek.map(sazonal_dia), index=y.index)
    residuo = y / (tendencia * sazonal)                                            # 4) o que sobra
    fig, axes = plt.subplots(4, 1, figsize=(11, 8), sharex=True, gridspec_kw={"hspace": 0.35})
    paineis = [(y, "Observado (pedidos/dia)", COR["texto"]), (tendencia, "Tendência (média de 7 dias)", COR["principal"]),
               (sazonal, "Fator do dia da semana", COR["destaque"]), (residuo, "Resíduo (1 = previsto)", COR["texto2"])]
    for ax, (s, nome, cor) in zip(axes, paineis):
        ax.plot(s.index, s.values, color=cor, lw=1.1 if s is not sazonal else 0.8)
        ax.set_title(nome, fontsize=10.5, pad=4)
    axes[3].axhline(1, color=COR["texto"], lw=0.8)
    extremo = (residuo - 1).abs().idxmax()
    axes[3].annotate(f"{extremo:%d/%m/%y}", (extremo, residuo[extremo]), xytext=(10, 0), textcoords="offset points", fontsize=9)
    axes[-1].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b/%y"))
    nomes = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    melhor, pior = sazonal_dia.idxmax(), sazonal_dia.idxmin()
    titulo_figura(fig, f"{nomes[melhor].capitalize()} vende {br((sazonal_dia[melhor] - 1) * 100)}% acima da média da semana; "
                       f"{nomes[pior]}, {br((1 - sazonal_dia[pior]) * 100)}% abaixo",
                  "Decomposição multiplicativa das vendas diárias, mar/2017 a jul/2018", y=0.93)
    salvar(fig, __file__, FONTES["olist"])
    var_res = np.log(residuo.dropna()).var() / np.log(y[y > 0]).var()
    return (f"A decomposição separa a série em três partes que se multiplicam. A tendência mostra o crescimento até o fim de 2017 e "
            f"a estabilização em 2018. O fator semanal é forte: {nomes[melhor]} vende {br((sazonal_dia[melhor] - 1) * 100)}% acima da "
            f"média e {nomes[pior]} {br((1 - sazonal_dia[pior]) * 100)}% abaixo. O resíduo é pequeno na maior parte do tempo (fica com "
            f"cerca de {br(var_res * 100)}% da variância do log das vendas) e tem o maior desvio em {extremo:%d/%m/%Y}, a Black Friday. "
            "Implementar a decomposição à mão (sem statsmodels) mostra que ela é só médias móveis e médias por grupo.")


if __name__ == "__main__":
    print(gerar())
