"""Distribuição de bootstrap: incerteza de uma estatística sem fórmula pronta."""
from comum import COR, airbnb, br, np, plt, salvar, titulo, FONTES

META = dict(grupo="Incerteza", nome="Distribuição de bootstrap",
            pergunta="Quanto um imóvel inteiro custa a mais que um quarto privativo, e com que precisão sabemos isso?",
            quando="Obter intervalo de confiança para medianas, razões ou qualquer estatística sem fórmula simples de erro-padrão.")


def gerar():
    d = airbnb()
    inteiro = d.loc[d.tipo == "Imóvel inteiro", "preco"].to_numpy()
    quarto = d.loc[d.tipo == "Quarto privativo", "preco"].to_numpy()
    def razao(a, b):
        """Razão das médias geométricas: o 'preço típico' em escala multiplicativa, menos travado que a mediana."""
        return np.exp(np.log(a).mean() - np.log(b).mean())

    observada = razao(inteiro, quarto)
    rng = np.random.default_rng(0)
    B = 5000
    # Reamostra cada grupo com reposição e recalcula a razão das medianas
    reps = np.array([razao(rng.choice(inteiro, len(inteiro)), rng.choice(quarto, len(quarto))) for _ in range(B)])
    lo, hi = np.percentile(reps, [2.5, 97.5])
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.hist(reps, bins=60, color=COR["contexto"], edgecolor="white", lw=0.3)
    dentro = (reps >= lo) & (reps <= hi)
    ax.hist(reps[dentro], bins=np.histogram_bin_edges(reps, 60), color=COR["principal"], edgecolor="white", lw=0.3)
    ax.axvline(observada, color=COR["destaque"], lw=2)
    ax.text(hi, ax.get_ylim()[1] * 0.95, f"  observada: {br(observada, 2)}×", color=COR["destaque"], fontsize=10, va="top")
    ax.set_xlabel("diária típica (média geométrica) do imóvel inteiro ÷ a do quarto privativo"); ax.set_ylabel("reamostragens")
    ax.grid(axis="x", visible=False)
    titulo(ax, f"O imóvel inteiro custa {br(observada, 2)}× o quarto privativo (IC 95%: {br(lo, 2)} a {br(hi, 2)})",
           f"{br(B)} reamostragens bootstrap da razão entre médias geométricas · em verde, os 95% centrais")
    salvar(fig, __file__, FONTES["airbnb"])
    med = [np.median(rng.choice(inteiro, len(inteiro))) / np.median(rng.choice(quarto, len(quarto))) for _ in range(300)]
    return (f"Não há fórmula simples para o erro-padrão de uma razão entre médias geométricas, mas o bootstrap resolve: reamostrar os anúncios "
            f"com reposição {br(B)} vezes mostra quanto a estatística variaria em outras amostras. A diária típica de um imóvel "
            f"inteiro é {br(observada, 2)}× a de um quarto privativo, com intervalo de 95% de {br(lo, 2)} a {br(hi, 2)}. Um detalhe que só "
            f"aparece fazendo: a razão entre medianas daria um intervalo degenerado ({br(np.percentile(med, 2.5), 2)} a "
            f"{br(np.percentile(med, 97.5), 2)}), porque os preços se repetem muito e a mediana fica presa no mesmo valor. A média "
            "geométrica, calculada em log, usa todos os dados e varia de forma contínua.")


if __name__ == "__main__":
    print(gerar())
