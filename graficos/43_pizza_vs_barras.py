"""Errado × certo: pizza com muitas fatias contra barras ordenadas."""
from comum import CATEGORICAS, COR, br, np, olist, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Errado × certo", nome="Pizza × barras",
            pergunta="Qual a participação de cada categoria nos pedidos, e qual gráfico responde isso melhor?",
            quando="Barras ordenadas para comparar partes; pizza só com 2 ou 3 fatias muito diferentes, quando a mensagem é 'parte do todo'.")


def gerar():
    d = olist()
    d = d[d.status != "canceled"]
    part = d.categoria_pt.value_counts(normalize=True) * 100
    top = part.iloc[:8]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"width_ratios": [1, 1.2], "wspace": 0.45})
    ax = axes[0]
    cores = (CATEGORICAS + ["#9AA6A1", "#C7CFCB"])[:8]
    ax.pie(top.values, colors=cores, startangle=90, counterclock=False, wedgeprops=dict(edgecolor="white", lw=1.5))
    ax.set_title("Errado: 8 fatias parecidas", fontsize=11, pad=8, color=COR["destaque"])
    ax.legend(top.index, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2, fontsize=8.5)
    ax = axes[1]
    y = np.arange(len(top))[::-1]
    ax.barh(y, top.values, color=COR["principal"], height=0.65)
    for yi, v in zip(y, top.values):
        ax.text(v + 0.15, yi, f"{br(v, 1)}%", va="center", fontsize=9.5, color=COR["texto"])
    ax.set_yticks(y, top.index); ax.grid(axis="y", visible=False); ax.set_xlabel("% dos pedidos")
    ax.set_title("Certo: barras ordenadas, com valores", fontsize=11, pad=8, color=COR["principal"])
    a, b = top.index[2], top.index[3]
    titulo_figura(fig, f"Na pizza, não dá para saber se {a} é maior que {b}; nas barras, é óbvio",
                  "As 8 categorias com mais pedidos, em % de todos os pedidos · mesmos dados nos dois gráficos", y=0.96)
    salvar(fig, __file__, FONTES["olist"])
    return (f"As oito fatias têm tamanhos parecidos (de {br(top.min(), 1)}% a {br(top.max(), 1)}%), e o olho humano compara ângulos "
            f"e áreas muito pior que comprimentos alinhados. Na pizza, {a} ({br(top[a], 1)}%) e {b} ({br(top[b], 1)}%) parecem "
            "iguais; nas barras, a ordem é imediata. A pizza ainda gasta oito cores e obriga o leitor a ir e voltar da legenda. "
            "Ela só funciona com duas ou três fatias bem diferentes, quando a mensagem é 'a maioria'.")


if __name__ == "__main__":
    print(gerar())
