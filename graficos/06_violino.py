"""Violino com caixa interna."""
from comum import CATEGORICAS, COR, br, np, plt, salvar, telco, titulo, FONTES

META = dict(grupo="Distribuição", nome="Violino",
            pergunta="Há quanto tempo estão na operadora os clientes de cada tipo de contrato?",
            quando="Comparar distribuições com formas diferentes (bimodais, truncadas), que um box plot faria parecer iguais.")


def gerar():
    d = telco()
    ordem = ["Mensal", "1 ano", "2 anos"]
    dados = [d.loc[d.contrato == c, "tenure"].to_numpy() for c in ordem]
    fig, ax = plt.subplots(figsize=(9, 5))
    partes = ax.violinplot(dados, showextrema=False, widths=0.8, bw_method=0.15)
    for corpo, cor in zip(partes["bodies"], CATEGORICAS):
        corpo.set_facecolor(cor); corpo.set_alpha(0.55); corpo.set_edgecolor("none")
    ax.boxplot(dados, widths=0.12, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor="white", edgecolor=COR["texto"]), medianprops=dict(color=COR["texto"], lw=2))
    medianas = [np.median(x) for x in dados]
    for i, m in enumerate(medianas, start=1):
        ax.text(i + 0.1, m, f"{br(m)} meses", va="center", fontsize=9.5, color=COR["texto"])
    ax.set_xticks([1, 2, 3], [f"{c}\n({br(len(x))} clientes)" for c, x in zip(ordem, dados)])
    ax.set_ylabel("meses como cliente"); ax.set_ylim(0, 75); ax.grid(axis="x", visible=False)
    curtos = (dados[0] <= 6).mean()
    titulo(ax, f"{br(curtos * 100)}% dos contratos mensais têm até 6 meses; os de 2 anos se acumulam no topo",
           "Tempo de casa por tipo de contrato · violino = densidade, caixa = quartis")
    salvar(fig, __file__, FONTES["telco"])
    return (f"Os três grupos têm formas opostas: o contrato mensal concentra clientes novos (mediana de {br(medianas[0])} meses), "
            f"o de 2 anos concentra clientes antigos (mediana de {br(medianas[2])} meses, encostando no limite de 72 da base), "
            "e o de 1 ano é quase uniforme. Isso alerta para um viés: comparar churn por contrato mistura o efeito do contrato "
            "com o tempo de casa.")


if __name__ == "__main__":
    print(gerar())
