"""Raincloud: densidade, caixa e pontos no mesmo gráfico."""
from comum import COR, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Distribuição", nome="Raincloud",
            pergunta="Quanto tempo leva uma entrega da Olist em cada região do país?",
            quando="Comparar distribuições inteiras entre poucos grupos, mostrando forma, resumo e os dados brutos de uma vez.")

ORDEM = ["Sudeste", "Sul", "Centro-Oeste", "Nordeste", "Norte"]


def gerar():
    d = olist_entregues()
    d = d[d.dias_entrega.between(0, 60)]
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(10, 5.4))
    medianas = {}
    for i, reg in enumerate(ORDEM):
        x = d.loc[d.regiao == reg, "dias_entrega"].to_numpy()
        medianas[reg] = np.median(x)
        # 1) "nuvem": densidade (metade de um violino) acima da linha do grupo
        v = ax.violinplot(x, positions=[i], orientation="horizontal", showextrema=False, widths=0.8)
        corpo = v["bodies"][0]
        caminho = corpo.get_paths()[0].vertices
        caminho[:, 1] = np.clip(caminho[:, 1], i, None)  # corta a metade de baixo
        corpo.set_facecolor(COR["principal"]); corpo.set_alpha(0.55); corpo.set_edgecolor("none")
        # 2) caixa estreita com mediana e quartis
        ax.boxplot(x, positions=[i - 0.08], orientation="horizontal", widths=0.08, showfliers=False, patch_artist=True,
                   boxprops=dict(facecolor="white", edgecolor=COR["texto"]), medianprops=dict(color=COR["destaque"], lw=2),
                   whiskerprops=dict(color=COR["texto2"]), capprops=dict(color=COR["texto2"]))
        # 3) "chuva": amostra dos pontos, com ruído vertical para não empilhar
        amostra = rng.choice(x, size=min(600, len(x)), replace=False)
        ax.scatter(amostra, i - 0.28 + rng.uniform(-0.08, 0.08, len(amostra)), s=3, color=COR["texto2"], alpha=0.35, lw=0)
        ax.text(medianas[reg], i + 0.42, f"mediana {br(medianas[reg], 1)} d", fontsize=8.5, color=COR["texto"], ha="center")
    ax.set_yticks(range(len(ORDEM)), ORDEM); ax.set_ylim(-0.5, len(ORDEM) - 0.2)
    ax.set_xlim(0, 60); ax.set_xlabel("dias entre a compra e a entrega"); ax.grid(axis="y", visible=False)
    razao = medianas["Norte"] / medianas["Sudeste"]
    titulo(ax, f"No Norte, a entrega típica leva {br(razao, 1)}× o tempo do Sudeste",
           "Dias de entrega por região do cliente · densidade, caixa (quartis) e amostra de 600 pedidos por região")
    salvar(fig, __file__, FONTES["olist"])
    p90 = d.groupby("regiao").dias_entrega.quantile(0.9)
    return (f"A mediana vai de {br(medianas['Sudeste'], 1)} dias no Sudeste a {br(medianas['Norte'], 1)} no Norte. "
            f"A cauda também muda: 10% dos pedidos do Norte levam mais de {br(p90['Norte'], 0)} dias, contra "
            f"{br(p90['Sudeste'], 0)} no Sudeste. Um box plot sozinho esconderia que todas as distribuições são "
            "assimétricas à direita, com caudas longas.")


if __name__ == "__main__":
    print(gerar())
