"""Diagrama de Sankey implementado do zero: de onde saem e para onde vão os pedidos."""
from comum import CATEGORICAS, COR, br, faixa, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Fluxo", nome="Sankey",
            pergunta="De que região saem os pedidos da Olist e para que região eles vão?",
            quando="Mostrar fluxos entre dois ou mais estágios, com a largura proporcional ao volume.")

ORDEM = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]


def gerar():
    d = olist()
    d = d[(d.status != "canceled")].dropna(subset=["regiao", "regiao_vendedor"])
    fluxo = d.groupby(["regiao_vendedor", "regiao"]).size().unstack(fill_value=0).reindex(index=ORDEM, columns=ORDEM, fill_value=0)
    total = fluxo.values.sum()
    vao = 0.02  # espaço entre os nós, em fração da altura
    altura_util = 1 - vao * (len(ORDEM) - 1)
    cor = dict(zip(ORDEM, CATEGORICAS))

    def posicoes(totais):
        pos, y = {}, 1.0
        for r in ORDEM:
            h = totais[r] / total * altura_util
            pos[r] = [y - h, y]
            y -= h + vao
        return pos

    origem, destino = posicoes(fluxo.sum(axis=1)), posicoes(fluxo.sum(axis=0))
    fig, ax = plt.subplots(figsize=(10, 6.6))
    cursor_o = {r: origem[r][1] for r in ORDEM}
    cursor_d = {r: destino[r][1] for r in ORDEM}
    for o in ORDEM:
        for dd in ORDEM:
            v = fluxo.loc[o, dd]
            if v == 0:
                continue
            h = v / total * altura_util
            faixa(ax, 0.06, (cursor_o[o] - h, cursor_o[o]), 0.94, (cursor_d[dd] - h, cursor_d[dd]), cor[o],
                  alpha=0.55 if o == "Sudeste" else 0.75)
            cursor_o[o] -= h
            cursor_d[dd] -= h
    def rotulos(pos, minimo=0.045):
        """Centro de cada rótulo, empurrado para baixo quando os nós são finos demais para caber o texto."""
        ys, anterior = {}, None
        for r in ORDEM:
            y = sum(pos[r]) / 2
            if anterior is not None and anterior - y < minimo:
                y = anterior - minimo
            ys[r] = anterior = y
        return ys

    y_origem, y_destino = rotulos(origem), rotulos(destino)
    for r in ORDEM:
        for x, pos, lado, tot, ys in [(0.0, origem, "right", fluxo.sum(axis=1), y_origem),
                                      (0.94, destino, "left", fluxo.sum(axis=0), y_destino)]:
            ax.add_patch(plt.Rectangle((x, pos[r][0]), 0.06, pos[r][1] - pos[r][0], color=cor[r]))
            tx = -0.01 if lado == "right" else 1.01
            ax.text(tx, ys[r], f"{r} {br(tot[r] / total * 100, 1)}%", ha=lado, va="center", fontsize=10,
                    color=COR["texto"])
    ax.text(0.03, 1.03, "Vendedor", ha="center", fontsize=10.5, fontweight="bold", color=COR["texto2"])
    ax.text(0.97, 1.03, "Cliente", ha="center", fontsize=10.5, fontweight="bold", color=COR["texto2"])
    ax.set_xlim(-0.25, 1.25); ax.set_ylim(-0.07, 1.07); ax.axis("off")
    sudeste = fluxo.loc["Sudeste"].sum() / total
    titulo(ax, f"{br(sudeste * 100)}% dos pedidos saem do Sudeste, para o país inteiro",
           "Pedidos por região do vendedor (esquerda) e do cliente (direita) · largura proporcional ao número de pedidos")
    salvar(fig, __file__, FONTES["olist"])
    fora = 1 - fluxo.loc["Nordeste", "Nordeste"] / fluxo["Nordeste"].sum()
    return (f"O lado esquerdo mostra a concentração da oferta: {br(sudeste * 100)}% dos pedidos têm vendedor no Sudeste, que "
            f"responde por {br(fluxo['Sudeste'].sum() / total * 100)}% da demanda. Dos pedidos do Nordeste, {br(fora * 100)}% "
            "vêm de outra região, o que explica parte dos prazos maiores (veja o raincloud e a ECDF). "
            "O Sankey foi desenhado do zero com curvas de Bézier: cada fita começa e termina com a mesma largura, o volume do fluxo.")


if __name__ == "__main__":
    print(gerar())
