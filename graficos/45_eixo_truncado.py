"""Errado × certo: barras com eixo que não começa no zero."""
from comum import COR, br, np, olist_entregues, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Errado × certo", nome="Eixo truncado",
            pergunta="A nota média muda muito entre as regiões?",
            quando="Barras sempre começam no zero, porque o comprimento é a mensagem. Para destacar diferenças pequenas, use pontos com eixo ajustado e diga isso.")


def gerar():
    d = olist_entregues().dropna(subset=["nota"])
    t = d.groupby("regiao").nota.mean().sort_values()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), gridspec_kw={"wspace": 0.55})
    cores = [COR["destaque"]] + [COR["contexto"]] * (len(t) - 2) + [COR["principal"]]
    ax = axes[0]
    ax.barh(t.index, t.values, color=cores, height=0.6); ax.set_xlim(3.8, 4.2)
    ax.set_title("Errado: barras com eixo cortado", fontsize=11, pad=8, color=COR["destaque"])
    ax = axes[1]
    ax.barh(t.index, t.values, color=cores, height=0.6); ax.set_xlim(0, 5)
    for i, v in enumerate(t.values):
        ax.text(v + 0.05, i, br(v, 2), va="center", fontsize=9.5)
    ax.set_title("Certo: barras a partir do zero", fontsize=11, pad=8, color=COR["principal"])
    ax = axes[2]
    ep = d.groupby("regiao").nota.sem().reindex(t.index)
    ax.errorbar(t.values, range(len(t)), xerr=1.96 * ep.values, fmt="none", ecolor=COR["texto2"], capsize=3)
    ax.scatter(t.values, range(len(t)), color=cores, s=60, zorder=3)
    ax.set_yticks(range(len(t)), t.index); ax.set_xlim(3.8, 4.25)
    ax.set_title("Certo: pontos com IC, eixo ajustado", fontsize=11, pad=8, color=COR["principal"])
    for a in axes:
        a.grid(axis="y", visible=False)
        a.set_xlabel("nota média (1 a 5)")
    diff = t.iloc[-1] - t.iloc[0]
    fator = (t.iloc[-1] - 3.8) / (t.iloc[0] - 3.8)
    titulo_figura(fig, f"A diferença entre a melhor e a pior região é de {br(diff, 2)} ponto: real, mas não de {br(fator, 1)} vezes",
                  "Nota média por região do cliente · mesmos dados nos três painéis", y=0.98)
    salvar(fig, __file__, FONTES["olist"])
    fator = (t.iloc[-1] - 3.8) / (t.iloc[0] - 3.8)
    return (f"No primeiro painel, o eixo começa em 3,8 e a barra do {t.index[-1]} parece {br(fator, 1)}× maior que a do {t.index[0]}, "
            f"quando a diferença real é de {br(diff, 2)} ponto ({br(diff / t.iloc[0] * 100, 1)}%). Barras codificam valor pelo comprimento, "
            "então cortar o eixo distorce a comparação. Se a diferença pequena importa, o gráfico de pontos com intervalo de confiança "
            "pode usar um eixo ajustado sem enganar, porque a posição, e não o comprimento, carrega o valor, e o intervalo mostra que a "
            "diferença é estatisticamente real.")


if __name__ == "__main__":
    print(gerar())
