"""Histograma: a escolha dos bins muda a história."""
from comum import COR, airbnb, br, np, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Distribuição", nome="Histograma e a escolha de bins",
            pergunta="Qual é a forma da distribuição dos preços do Airbnb, e quanto a escolha dos intervalos interfere?",
            quando="Mostrar a forma de uma variável contínua, sempre justificando a regra de bins (Freedman-Diaconis é robusta a caudas).")


def gerar():
    x = airbnb().preco.to_numpy() / 1000
    regras = [("Sturges", "sturges"), ("Freedman-Diaconis", "fd")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=False, gridspec_kw={"wspace": 0.25})
    n_bins = {}
    for ax, (nome, regra) in zip(axes, regras):
        bordas = np.histogram_bin_edges(x, bins=regra)
        n_bins[nome] = len(bordas) - 1
        ax.hist(x, bins=bordas, color=COR["principal"] if regra == "fd" else COR["contexto"], edgecolor="white", lw=0.3)
        ax.axvline(np.median(x), color=COR["destaque"], lw=1.4, ls="--")
        ax.set_title(f"{nome}: {n_bins[nome]} intervalos", fontsize=11, pad=8)
        ax.set_xlabel("preço da diária (mil pesos argentinos)"); ax.set_xlim(0, 150); ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("anúncios")
    titulo_figura(fig, "Com poucos intervalos, a forma dos preços se perde; a regra de Freedman-Diaconis a revela",
                  "Mesmos 33 mil anúncios do Airbnb em Buenos Aires · linha tracejada = mediana")
    salvar(fig, __file__, FONTES["airbnb"])
    return (f"A regra de Sturges ({n_bins['Sturges']} intervalos) foi pensada para dados normais e pequenos; aqui ela alisa "
            f"demais. Freedman-Diaconis ({n_bins['Freedman-Diaconis']} intervalos) usa o intervalo interquartil e revela a "
            "assimetria forte, com a moda bem à esquerda da mediana e uma cauda longa de anúncios caros. "
            "Sem justificar a regra de bins, um histograma pode contar a história que o autor quiser.")


if __name__ == "__main__":
    print(gerar())
