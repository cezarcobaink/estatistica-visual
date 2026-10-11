"""O que um intervalo de confiança de 95% significa: 100 amostras da mesma população."""
from comum import COR, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Incerteza", nome="Cobertura de intervalos de confiança",
            pergunta="Se repetíssemos uma pesquisa 100 vezes, quantos intervalos de 95% conteriam o valor verdadeiro?",
            quando="Explicar incerteza amostral para não estatísticos; mostra que o 95% é sobre o método, não sobre um intervalo específico.")


def gerar():
    pop = olist_entregues().dias_entrega.dropna().to_numpy()
    verdade = pop.mean()
    rng = np.random.default_rng(4)
    n, R = 40, 100
    amostras = rng.choice(pop, size=(R, n))
    medias = amostras.mean(axis=1)
    from scipy import stats
    t = stats.t.ppf(0.975, n - 1)
    ep = amostras.std(axis=1, ddof=1) / np.sqrt(n)
    lo, hi = medias - t * ep, medias + t * ep
    erra = (lo > verdade) | (hi < verdade)
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for i in range(R):
        cor = COR["destaque"] if erra[i] else COR["contexto"]
        ax.plot([lo[i], hi[i]], [i, i], color=cor, lw=1.8 if erra[i] else 1.2)
        ax.scatter(medias[i], i, s=8, color=COR["texto"] if erra[i] else COR["texto2"], zorder=3)
    ax.axvline(verdade, color=COR["principal"], lw=2)
    ax.text(verdade, R + 2, f"média verdadeira: {br(verdade, 1)} dias", ha="center", fontsize=10, color=COR["principal"])
    ax.set_yticks([]); ax.set_xlabel("dias de entrega"); ax.set_ylim(-2, R + 6); ax.grid(axis="y", visible=False)
    titulo(ax, f"{erra.sum()} dos 100 intervalos de 95% não contêm a média verdadeira",
           f"100 amostras de {n} pedidos sorteadas dos {br(len(pop))} entregues · cada linha é o IC de 95% de uma amostra (t de Student)")
    salvar(fig, __file__, FONTES["olist"])
    return (f"Aqui a população é conhecida (todos os {br(len(pop))} pedidos), então dá para conferir: dos 100 intervalos calculados "
            f"com amostras de {n} pedidos, {erra.sum()} não contêm a média verdadeira de {br(verdade, 1)} dias. O \"95%\" descreve o "
            "método ao longo de muitas repetições; um intervalo específico acerta ou erra. Neste sorteio, "
            f"{((hi < verdade)).sum()} dos {erra.sum()} erros ficaram à esquerda da verdade: com dias de entrega assimétricos, as amostras sem "
            "nenhum pedido muito atrasado subestimam a média, e o intervalo t, que supõe simetria, não compensa.")


if __name__ == "__main__":
    print(gerar())
