"""Gráfico de bolhas: três medidas por estado."""
from comum import CATEGORICAS, COR, REGIAO, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Relação", nome="Bolhas",
            pergunta="Estados com entrega mais demorada dão notas mais baixas?",
            quando="Relacionar duas medidas por categoria e mostrar uma terceira (volume) no tamanho, sem esconder os grupos pequenos.")


def gerar():
    d = olist_entregues().dropna(subset=["nota"])
    t = d.groupby("uf_cliente").agg(dias=("dias_entrega", "median"), nota=("nota", "mean"), pedidos=("nota", "size"),
                                    atraso=("atraso", "mean"))
    t["regiao"] = t.index.map(REGIAO)
    regioes = ["Sudeste", "Sul", "Centro-Oeste", "Nordeste", "Norte"]
    cor = dict(zip(regioes, CATEGORICAS))
    fig, ax = plt.subplots(figsize=(10, 6))
    for reg in regioes:
        s = t[t.regiao == reg]
        ax.scatter(s.dias, s.nota, s=20 + s.pedidos / t.pedidos.max() * 2500, color=cor[reg], alpha=0.65, edgecolor="white",
                   label=reg)
    for uf, r in t.iterrows():
        ax.text(r.dias, r.nota, uf, ha="center", va="center", fontsize=8, color=COR["texto"])
    incl, inter = np.polyfit(t.dias, t.nota, 1, w=np.sqrt(t.pedidos))
    xs = np.linspace(t.dias.min(), t.dias.max(), 10)
    ax.plot(xs, inter + incl * xs, color=COR["texto2"], lw=1.2, ls="--")
    ax.set_xlabel("dias de entrega (mediana)"); ax.set_ylabel("nota média")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=cor[r], ms=9, alpha=0.8, label=r) for r in regioes],
              loc="lower left")
    titulo(ax, f"Cada dia a mais de entrega custa cerca de {br(-incl, 2)} ponto na nota média do estado",
           "Estados do cliente · tamanho da bolha = número de pedidos · linha = regressão ponderada pelo volume")
    salvar(fig, __file__, FONTES["olist"])
    r = np.corrcoef(t.dias, t.nota)[0, 1]
    return (f"A correlação entre a mediana de dias de entrega e a nota média dos estados é {br(r, 2)}. A regressão ponderada pelo "
            f"volume sugere {br(-incl, 2)} ponto a menos por dia de espera. As bolhas evitam um engano comum: os estados mais "
            "extremos são os menores, e sem o tamanho eles pareceriam tão importantes quanto SP. Correlação entre estados não prova "
            "o efeito em cada pedido (falácia ecológica); a análise pedido a pedido está no projeto de previsão de demanda.")


if __name__ == "__main__":
    print(gerar())
