"""Slope chart: mudança entre dois momentos."""
from comum import CATEGORICAS, COR, br, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Comparação", nome="Slope chart",
            pergunta="A participação de cada região nos pedidos mudou entre 2017 e 2018?",
            quando="Mostrar a mudança de várias categorias entre dois momentos, destacando quem subiu e quem caiu.")


def gerar():
    d = olist()
    d = d[d.status != "canceled"]
    sem = {"1º sem. 2017": d[(d.compra >= "2017-01-01") & (d.compra < "2017-07-01")],
           "1º sem. 2018": d[(d.compra >= "2018-01-01") & (d.compra < "2018-07-01")]}
    part = {k: v.regiao.value_counts(normalize=True) * 100 for k, v in sem.items()}
    a, b = part["1º sem. 2017"], part["1º sem. 2018"]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for i, reg in enumerate(a.sort_values(ascending=False).index):
        sub = b[reg] > a[reg]
        cor = COR["principal"] if sub else COR["destaque"]
        ax.plot([0, 1], [a[reg], b[reg]], color=cor, lw=2.4, marker="o")
        ax.text(-0.04, a[reg], f"{reg} {br(a[reg], 1)}%", ha="right", va="center", fontsize=10, color=COR["texto"])
        ax.text(1.04, b[reg], f"{br(b[reg], 1)}% ({'+' if sub else ''}{br(b[reg] - a[reg], 1)} p.p.)", ha="left", va="center",
                fontsize=10, color=cor)
    ax.set_xlim(-0.6, 1.6); ax.set_xticks([0, 1], list(sem)); ax.set_yticks([]); ax.grid(False)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(plt.NullLocator()); ax.yaxis.set_minor_locator(plt.NullLocator())
    mudanca = (b - a).sort_values()
    titulo(ax, f"Com a expansão da Olist, o {mudanca.index[-1]} ganhou peso e o {mudanca.index[0]} perdeu",
           "Participação de cada região nos pedidos (escala log para separar as regiões pequenas)")
    salvar(fig, __file__, FONTES["olist"])
    return (f"O Sudeste segue dominante ({br(b['Sudeste'], 1)}% em 2018), mas as linhas mostram a direção: "
            f"{mudanca.index[-1]} {'+' if mudanca.iloc[-1] > 0 else ''}{br(mudanca.iloc[-1], 1)} p.p. e {mudanca.index[0]} {br(mudanca.iloc[0], 1)} p.p. " +
            "A escala log deixa visíveis as regiões pequenas; numa escala linear, Norte e Centro-Oeste ficariam espremidos no rodapé.")


if __name__ == "__main__":
    print(gerar())
