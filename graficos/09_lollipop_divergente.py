"""Lollipop divergente: desvio de cada categoria em relação à média."""
from comum import COR, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Comparação", nome="Lollipop divergente",
            pergunta="Quais categorias têm nota acima ou abaixo da média da loja?",
            quando="Comparar muitas categorias contra uma referência; mais leve que barras quando os valores são parecidos.")


def gerar():
    d = olist_entregues().dropna(subset=["nota"])
    media = d.nota.mean()
    top = d.categoria_pt.value_counts().index[:20]
    t = d[d.categoria_pt.isin(top)].groupby("categoria_pt").nota.agg(["mean", "size", "std"])
    t["desvio"] = t["mean"] - media
    t["ep"] = t["std"] / np.sqrt(t["size"])
    t = t.sort_values("desvio")
    fig, ax = plt.subplots(figsize=(9, 7))
    y = np.arange(len(t))
    cores = [COR["destaque"] if v < 0 else COR["principal"] for v in t.desvio]
    ax.hlines(y, 0, t.desvio, color=cores, lw=2)
    ax.scatter(t.desvio, y, color=cores, s=55, zorder=3)
    ax.errorbar(t.desvio, y, xerr=1.96 * t.ep, fmt="none", ecolor=COR["texto2"], elinewidth=0.8, capsize=2, zorder=2)
    ax.axvline(0, color=COR["texto2"], lw=1)
    ax.set_yticks(y, t.index); ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"nota média da categoria − média geral ({br(media, 2)})")
    pior, melhor = t.index[0], t.index[-1]
    titulo(ax, f"{pior} tem a pior nota; {melhor}, a melhor",
           "20 categorias com mais pedidos · barra cinza = intervalo de confiança de 95%")
    salvar(fig, __file__, FONTES["olist"])
    signif = ((t.desvio.abs() - 1.96 * t.ep) > 0).sum()
    return (f"A nota média geral é {br(media, 2)}. {pior} fica {br(-t.desvio.iloc[0], 2)} ponto abaixo e {melhor}, "
            f"{br(t.desvio.iloc[-1], 2)} acima. Os intervalos de confiança importam: só {signif} das 20 categorias se afastam "
            "da média com segurança estatística. As outras diferenças são do tamanho do ruído.")


if __name__ == "__main__":
    print(gerar())
