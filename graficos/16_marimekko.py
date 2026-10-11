"""Marimekko (mosaico): largura e altura codificam duas proporções."""
from comum import CATEGORICAS, COR, PAGAMENTO_PT, br, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Composição", nome="Marimekko",
            pergunta="A forma de pagamento muda entre as regiões, levando em conta o tamanho de cada região?",
            quando="Mostrar duas variáveis categóricas ao mesmo tempo: a largura é o peso do grupo, a altura é a composição interna.")


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & d.pagamento.isin(["credit_card", "boleto", "voucher", "debit_card"])]
    tab = d.groupby(["regiao", "pagamento"]).size().unstack(fill_value=0)
    tab = tab.loc[tab.sum(axis=1).sort_values(ascending=False).index, ["credit_card", "boleto", "voucher", "debit_card"]]
    largura = tab.sum(axis=1) / tab.values.sum()
    comp = tab.div(tab.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = 0
    for reg in tab.index:
        y = 0
        for j, metodo in enumerate(tab.columns):
            h = comp.loc[reg, metodo]
            ax.add_patch(plt.Rectangle((x, y), largura[reg], h, facecolor=CATEGORICAS[j], edgecolor="white", lw=1.5))
            if h > 0.06 and largura[reg] > 0.04:
                ax.text(x + largura[reg] / 2, y + h / 2, f"{br(h * 100)}%", ha="center", va="center", fontsize=9, color="white")
            y += h
        if largura[reg] > 0.1:
            ax.text(x + largura[reg] / 2, -0.04, f"{reg}\n{br(largura[reg] * 100)}% dos pedidos", ha="center", va="top",
                    fontsize=9, color=COR["texto"])
        else:  # colunas estreitas: rótulo na vertical para não colidir
            ax.text(x + largura[reg] / 2, -0.02, f"{reg} ({br(largura[reg] * 100)}%)", ha="center", va="top", rotation=90,
                    fontsize=8.5, color=COR["texto"])
        x += largura[reg]
    for j, metodo in enumerate(tab.columns):
        ax.add_patch(plt.Rectangle((1.02, 0.85 - j * 0.09), 0.025, 0.05, color=CATEGORICAS[j], clip_on=False))
        ax.text(1.055, 0.875 - j * 0.09, PAGAMENTO_PT[metodo], va="center", fontsize=9.5, color=COR["texto"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    boleto = comp.boleto.sort_values()
    titulo(ax, f"O boleto pesa mais no {boleto.index[-1]} ({br(boleto.iloc[-1] * 100)}%) do que no {boleto.index[0]} ({br(boleto.iloc[0] * 100)}%)",
           "Largura = participação da região nos pedidos · altura = mistura de formas de pagamento")
    salvar(fig, __file__, FONTES["olist"], y_fonte=-0.2)
    return (f"A largura mostra que o Sudeste domina os pedidos ({br(largura['Sudeste'] * 100)}%); a altura mostra a composição de "
            f"cada região. O boleto vai de {br(boleto.iloc[0] * 100)}% no {boleto.index[0]} a {br(boleto.iloc[-1] * 100)}% no "
            f"{boleto.index[-1]}. A diferença é pequena: a forma de pagamento quase não depende da região, e o gráfico deixa isso "
            "visível sem esconder que as regiões pequenas pesam pouco no total.")


if __name__ == "__main__":
    print(gerar())
