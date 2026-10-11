"""Bump chart: evolução de rankings."""
from comum import CATEGORICAS, COR, np, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Comparação", nome="Bump chart",
            pergunta="Como mudou, trimestre a trimestre, o ranking das categorias que mais faturam?",
            quando="Acompanhar posições num ranking ao longo do tempo, quando a ordem importa mais que o valor.")


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & (d.compra >= "2017-01-01") & (d.compra < "2018-07-01")].copy()
    d["tri"] = d.compra.dt.to_period("Q").astype(str).str.replace("Q", "T")
    receita = d.groupby(["tri", "categoria_pt"]).valor_itens.sum().reset_index()
    receita["pos"] = receita.groupby("tri").valor_itens.rank(ascending=False, method="first")
    top = receita.groupby("categoria_pt").valor_itens.sum().sort_values(ascending=False).index[:8]
    trimestres = sorted(receita.tri.unique())
    fig, ax = plt.subplots(figsize=(10, 5.6))
    destaque = {}
    for i, cat in enumerate(top):
        r = receita[receita.categoria_pt == cat].set_index("tri").reindex(trimestres)
        destaque[cat] = r.pos.iloc[0] - r.pos.iloc[-1]
    subiu = max(destaque, key=destaque.get)
    caiu = min(destaque, key=destaque.get)
    for cat in top:
        r = receita[receita.categoria_pt == cat].set_index("tri").reindex(trimestres)
        cor = COR["principal"] if cat == subiu else COR["destaque"] if cat == caiu else COR["contexto"]
        lw = 3 if cor != COR["contexto"] else 1.8
        ax.plot(range(len(trimestres)), r.pos, color=cor, lw=lw, marker="o", ms=9, zorder=3 if lw == 3 else 2)
        ax.text(len(trimestres) - 1 + 0.15, r.pos.iloc[-1], f"{cat}", va="center", fontsize=9.5,
                color=COR["texto"] if lw == 3 else COR["texto2"])
        ax.text(-0.15, r.pos.iloc[0], f"{int(r.pos.iloc[0])}º", va="center", ha="right", fontsize=9, color=COR["texto2"])
    ax.invert_yaxis(); ax.set_yticks([]); ax.set_xticks(range(len(trimestres)), [t.replace("T", " T") for t in trimestres])
    ax.set_xlim(-0.6, len(trimestres) + 1.6); ax.grid(axis="y", visible=False)
    titulo(ax, f"{subiu} subiu {int(destaque[subiu])} posições; {caiu} caiu {int(-destaque[caiu])}",
           "Posição no ranking de faturamento por trimestre · as 8 categorias que mais faturaram no período")
    salvar(fig, __file__, FONTES["olist"])
    return (f"O bump chart troca o valor pela posição, e com isso mostra trocas de liderança que um gráfico de linhas de faturamento "
            f"esconderia sob a escala. {subiu} ganhou {int(destaque[subiu])} posições entre o início de 2017 e meados de 2018; "
            f"{caiu} perdeu {int(-destaque[caiu])}. A limitação: um salto de posição pode significar uma diferença pequena de "
            "receita, então o gráfico deve vir acompanhado dos valores quando a decisão depender deles.")


if __name__ == "__main__":
    print(gerar())
