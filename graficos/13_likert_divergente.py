"""Barras divergentes (escala Likert): notas de 1 a 5 centradas no neutro."""
from comum import COR, DIV, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Comparação", nome="Barras divergentes (Likert)",
            pergunta="Como se distribuem as notas de 1 a 5 em cada categoria, e onde estão as insatisfeitas?",
            quando="Mostrar respostas em escala ordinal (pesquisas, notas) separando o lado negativo do positivo.")


def gerar():
    d = olist_entregues().dropna(subset=["nota"])
    d = d[d.nota.isin([1, 2, 3, 4, 5])]
    top = d.categoria_pt.value_counts().index[:12]
    t = pd_crosstab(d[d.categoria_pt.isin(top)])
    t = t.loc[(t[1] + t[2]).sort_values().index]
    cores = {1: DIV(0.0), 2: DIV(0.25), 3: "#D9DEDB", 4: DIV(0.75), 5: DIV(1.0)}
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(t))
    # O lado negativo começa no meio da nota 3 e vai para a esquerda; o positivo, para a direita
    esquerda = -(t[3] / 2 + t[2] + t[1])
    for nota in [1, 2, 3, 4, 5]:
        ax.barh(y, t[nota], left=esquerda, color=cores[nota], height=0.7, label=f"nota {nota}", edgecolor="white", lw=0.5)
        esquerda = esquerda + t[nota]
    for yi, (cat, r) in zip(y, t.iterrows()):
        ax.text(-(r[3] / 2 + r[2] + r[1]) - 1, yi, f"{br(r[1] + r[2])}%", va="center", ha="right", fontsize=9, color=COR["texto"])
    ax.axvline(0, color=COR["texto2"], lw=0.8)
    ax.set_yticks(y, t.index); ax.grid(axis="y", visible=False); ax.set_xlim(-40, 100)
    ax.set_xlabel("% das avaliações (o centro é o meio da nota 3)")
    ax.legend(ncol=5, loc="lower right", bbox_to_anchor=(1, -0.2), fontsize=9)
    pior = t.index[-1]
    titulo(ax, f"{pior} tem a maior fatia de notas 1 e 2 ({br(t.loc[pior, 1] + t.loc[pior, 2])}%)",
           "Distribuição das notas por categoria · número à esquerda = % de notas 1 e 2")
    salvar(fig, __file__, FONTES["olist"], y_fonte=-0.12)
    melhor = t.index[0]
    return (f"Centralizar no neutro deixa o lado insatisfeito todo à esquerda, comparável entre categorias. {pior} tem "
            f"{br(t.loc[pior, 1] + t.loc[pior, 2])}% de notas 1 e 2; {melhor}, {br(t.loc[melhor, 1] + t.loc[melhor, 2])}%. "
            "Uma média de nota esconderia isso: duas categorias com média parecida podem ter fatias de insatisfeitos bem diferentes.")


def pd_crosstab(d):
    import pandas as pd
    return pd.crosstab(d.categoria_pt, d.nota, normalize="index") * 100


if __name__ == "__main__":
    print(gerar())
