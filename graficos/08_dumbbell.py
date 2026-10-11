"""Dumbbell: duas medidas por categoria ligadas por uma barra."""
from comum import COR, br, np, olist_entregues, plt, salvar, titulo, FONTES

META = dict(grupo="Comparação", nome="Dumbbell",
            pergunta="Em cada estado, quanto o prazo prometido pela Olist difere do prazo real de entrega?",
            quando="Comparar dois valores por categoria (antes/depois, meta/real) quando o que importa é a distância entre eles.")


def gerar():
    d = olist_entregues()
    t = d.groupby("uf_cliente").agg(real=("dias_entrega", "median"), prometido=("dias_prometidos", "median"),
                                    pedidos=("dias_entrega", "size"))
    t["folga"] = t.prometido - t.real
    t = t.sort_values("folga")
    fig, ax = plt.subplots(figsize=(9, 8))
    y = np.arange(len(t))
    ax.hlines(y, t.real, t.prometido, color=COR["contexto"], lw=3)
    ax.scatter(t.real, y, color=COR["principal"], s=45, zorder=3, label="prazo real (mediana)")
    ax.scatter(t.prometido, y, color=COR["destaque"], s=45, zorder=3, label="prazo prometido (mediana)")
    for yi, (uf, r) in zip(y, t.iterrows()):
        ax.text(r.prometido + 0.6, yi, f"+{br(r.folga)} d", va="center", fontsize=8.5, color=COR["texto2"])
    ax.set_yticks(y, t.index); ax.set_xlabel("dias desde a compra"); ax.set_xlim(0, 60)
    ax.grid(axis="y", visible=False); ax.legend(loc="lower right")
    maior, menor = t.index[-1], t.index[0]
    titulo(ax, f"A Olist promete com folga em todos os estados, de {br(t.folga.min())} dias ({menor}) a {br(t.folga.max())} ({maior})",
           "Mediana do prazo real e do prometido por estado do cliente · ordenado pela folga")
    salvar(fig, __file__, FONTES["olist"])
    return (f"Em nenhum estado a mediana real passa do prometido: a folga vai de {br(t.folga.min())} dias em {menor} a "
            f"{br(t.folga.max())} em {maior}. A correlação entre o prazo real e a folga é de {br(t.real.corr(t.folga), 2)}: "
            "estados com entrega mais lenta tendem a receber folgas maiores, mas não de forma consistente (Alagoas é lenta e tem a menor folga). "
            "A folga é margem para testar prazos prometidos menores, que tendem a aumentar a conversão.")


if __name__ == "__main__":
    print(gerar())
