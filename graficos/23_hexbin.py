"""Hexbin: dispersão para dezenas de milhares de pontos."""
from comum import COR, SEQ, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Relação", nome="Hexbin",
            pergunta="Quanto o frete pesa em relação ao valor do produto, pedido a pedido?",
            quando="Mostrar a relação entre duas variáveis contínuas com muitos pontos, onde um scatter vira uma mancha sem densidade.")


def gerar():
    d = olist_entregues().dropna(subset=["valor_itens", "frete"])
    d = d[(d.valor_itens > 0) & (d.frete > 0)]
    fig, ax = plt.subplots(figsize=(9, 6))
    hb = ax.hexbin(d.valor_itens, d.frete, xscale="log", yscale="log", gridsize=45, cmap=SEQ, mincnt=3, bins="log")
    for prop, rot in [(1.0, "frete = 100% do produto"), (0.2, "20%")]:
        x = np.logspace(0.5, 3.8, 50)
        ax.plot(x, x * prop, color=COR["destaque"], lw=1.2, ls="--")
        ax.text(x[-12], x[-12] * prop * 1.15, rot, color=COR["destaque"], fontsize=9, rotation=0)
    cb = fig.colorbar(hb, ax=ax, shrink=0.75); cb.set_label("pedidos por hexágono (escala log)")
    ax.set_xlabel("valor dos itens (R$, escala log)"); ax.set_ylabel("frete (R$, escala log)"); ax.grid(False)
    razao = d.frete / d.valor_itens
    caro = (razao > 1).mean()
    baratos = d[d.valor_itens < 50]
    titulo(ax, f"Abaixo de R$ 50, o frete custa, na mediana, {br((baratos.frete / baratos.valor_itens).median() * 100)}% do produto",
           f"{br(len(d))} pedidos entregues · cada hexágono conta os pedidos naquela faixa de valor e frete")
    salvar(fig, __file__, FONTES["olist"])
    acima = d[d.valor_itens > 500]
    return (f"O frete cresce bem menos que o valor: abaixo de R$ 50 ele é, na mediana, "
            f"{br((baratos.frete / baratos.valor_itens).median() * 100)}% do produto; acima de R$ 500, "
            f"{br((acima.frete / acima.valor_itens).median() * 100)}%. Em {br(caro * 100, 1)}% dos pedidos o frete custa mais que o produto. "
            f"Com {br(len(d))} pontos, um gráfico de dispersão comum viraria uma mancha; o hexbin conta os pontos e mostra onde está "
            "a massa dos pedidos.")


if __name__ == "__main__":
    print(gerar())
