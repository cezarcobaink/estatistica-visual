"""Funil: perdas entre etapas sucessivas."""
from comum import COR, br, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Fluxo", nome="Funil",
            pergunta="Em qual etapa, da compra à avaliação nota 5, a Olist perde mais pedidos?",
            quando="Mostrar etapas sequenciais em que cada uma é um subconjunto da anterior, destacando a maior perda.")


def gerar():
    d = olist()
    etapas = [
        ("Compra registrada", len(d)),
        ("Pagamento aprovado", d.aprovacao.notna().sum()),
        ("Postado", d.postagem.notna().sum()),
        ("Entregue", d.entrega.notna().sum()),
        ("Entregue no prazo", (d.atraso == False).sum()),  # noqa: E712
        ("No prazo e nota 5", ((d.atraso == False) & (d.nota == 5)).sum()),  # noqa: E712
    ]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    topo = etapas[0][1]
    perdas = []
    for i, (nome, v) in enumerate(etapas):
        w = v / topo
        ax.barh(i, w, left=(1 - w) / 2, color=COR["principal"] if i < len(etapas) - 1 else COR["destaque"], height=0.72)
        ax.text(0.5, i, f"{nome}  ·  {br(w * 100, 1)}%", ha="center", va="center", fontsize=10, color="white")
        if i:
            perda = 1 - v / etapas[i - 1][1]
            perdas.append((perda, etapas[i - 1][0], nome))
            ax.text(1.02, i - 0.5, f"−{br(perda * 100, 1)}%", va="center", fontsize=9, color=COR["texto2"])
    ax.invert_yaxis(); ax.set_xlim(0, 1.12); ax.axis("off")
    maior = max(perdas)
    titulo(ax, f"A maior perda não é logística: só {br(etapas[-1][1] / etapas[-2][1] * 100)}% das entregas no prazo viram nota 5",
           "Pedidos que chegam a cada etapa, em % das compras registradas · à direita, a perda em relação à etapa anterior")
    salvar(fig, __file__, FONTES["olist"])
    return (f"A operação é eficiente até a entrega ({br(etapas[3][1] / topo * 100, 1)}% das compras são entregues) e quase sempre "
            f"no prazo. A maior queda está na última etapa: de {maior[1].lower()} para {maior[2].lower()}, {br(maior[0] * 100)}% "
            "ficam pelo caminho. Ou seja, cumprir o prazo é necessário, mas não basta para encantar: o produto e a experiência "
            "pesam na nota máxima.")


if __name__ == "__main__":
    print(gerar())
