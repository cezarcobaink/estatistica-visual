"""ECDF: distribuição acumulada empírica, sem escolher bins."""
from comum import CATEGORICAS, COR, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Distribuição", nome="Distribuição acumulada (ECDF)",
            pergunta="Em quantos dias a Olist consegue entregar 90% dos pedidos em cada região?",
            quando="Ler percentis direto no gráfico e comparar grupos sem depender da escolha de bins de um histograma.")

REGIOES = ["Sudeste", "Sul", "Nordeste", "Norte"]


def gerar():
    d = olist_entregues()
    fig, ax = plt.subplots(figsize=(9.5, 5))
    p90 = {}
    for reg, cor in zip(REGIOES, CATEGORICAS):
        x = np.sort(d.loc[d.regiao == reg, "dias_entrega"].to_numpy())
        y = np.arange(1, len(x) + 1) / len(x)
        p90[reg] = np.quantile(x, 0.9)
        ax.step(x, y * 100, where="post", color=cor, lw=2.2, label=f"{reg} · 90% até {br(p90[reg])} dias")
        ax.plot(p90[reg], 90, "o", color=cor, ms=6)
    ax.legend(loc="lower right")
    ax.axhline(90, color=COR["texto2"], lw=1, ls="--")
    ax.set_xlim(0, 60); ax.set_ylim(0, 101)
    ax.set_xlabel("dias entre a compra e a entrega"); ax.set_ylabel("% dos pedidos entregues até esse dia")
    titulo(ax, f"Para cumprir 90% das entregas, o Norte precisa de {br(p90['Norte'] - p90['Sudeste'])} dias a mais que o Sudeste",
           "Distribuição acumulada empírica dos dias de entrega · ponto = percentil 90")
    salvar(fig, __file__, FONTES["olist"])
    apos_media = (d.dias_entrega > d.dias_entrega.mean()).mean()
    return (f"Cada curva responde \"qual fração dos pedidos chegou até o dia X\". O percentil 90 é {br(p90['Sudeste'])} dias no Sudeste, "
            f"{br(p90['Sul'])} no Sul, {br(p90['Nordeste'])} no Nordeste e {br(p90['Norte'])} no Norte. É o número certo para "
            f"definir um prazo prometido: prometer pela média faria {br(apos_media * 100)}% dos pedidos chegarem depois.")


if __name__ == "__main__":
    print(gerar())
