"""Ridgeline (joyplot): várias densidades sobrepostas em faixas."""
from scipy.stats import gaussian_kde

from comum import COR, SEQ, airbnb, br, np, plt, salvar, titulo, FONTES

META = dict(grupo="Distribuição", nome="Ridgeline",
            pergunta="Como o preço da diária do Airbnb varia entre os bairros de Buenos Aires?",
            quando="Comparar a forma da distribuição entre muitos grupos (8 a 20) sem gastar um painel por grupo.")


def gerar():
    d = airbnb()
    d = d[d.tipo == "Imóvel inteiro"]
    top = d.bairro.value_counts().index[:10]
    medianas = d[d.bairro.isin(top)].groupby("bairro").preco.median().sort_values()
    grade = np.linspace(np.log10(10_000), np.log10(200_000), 300)
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    for i, bairro in enumerate(medianas.index):
        x = np.log10(d.loc[d.bairro == bairro, "preco"])
        dens = gaussian_kde(x)(grade)
        dens = dens / dens.max() * 1.6  # altura comum: compara forma, não tamanho do bairro
        cor = SEQ(0.25 + 0.7 * i / (len(medianas) - 1))
        ax.fill_between(grade, i, i + dens, color=cor, alpha=0.9, lw=0, zorder=len(medianas) - i)
        ax.plot(grade, i + dens, color="white", lw=1, zorder=len(medianas) - i)
        ax.plot([np.log10(medianas[bairro])] * 2, [i, i + 0.25], color=COR["texto"], lw=1.4, zorder=50)
        ax.text(grade[0] - 0.02, i + 0.15, bairro, ha="right", fontsize=10, color=COR["texto"])
    ticks = [10_000, 20_000, 50_000, 100_000, 200_000]
    ax.set_xticks(np.log10(ticks), [br(t) for t in ticks]); ax.set_yticks([])
    ax.set_xlabel("preço da diária (pesos argentinos, escala log)"); ax.grid(axis="y", visible=False)
    ax.set_xlim(grade[0] - 0.55, grade[-1])
    caro, barato = medianas.index[-1], medianas.index[0]
    titulo(ax, f"{caro} cobra {br(medianas[caro] / medianas[barato], 1)}× a diária típica de {barato}",
           "Imóveis inteiros nos 10 bairros com mais anúncios · traço preto = mediana")
    salvar(fig, __file__, FONTES["airbnb"])
    return (f"Os bairros estão ordenados pela mediana: de {barato} (ARS {br(medianas[barato])}) a {caro} "
            f"(ARS {br(medianas[caro])}). As curvas se sobrepõem muito: o bairro desloca o preço, mas a variação "
            "dentro de cada bairro é maior que a diferença entre eles. A escala log é necessária porque preço é "
            "multiplicativo: sem ela, a cauda dos anúncios caros esmagaria todas as curvas à esquerda.")


if __name__ == "__main__":
    print(gerar())
