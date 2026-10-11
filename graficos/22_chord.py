"""Diagrama de cordas implementado do zero: fluxos entre os estados."""
from matplotlib.patches import PathPatch, Wedge
from matplotlib.path import Path as MPath

from comum import CATEGORICAS, COR, br, np, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Fluxo", nome="Diagrama de cordas",
            pergunta="Entre os maiores estados, quem vende para quem?",
            quando="Mostrar fluxos de ida e volta entre poucas entidades (até ~10), onde uma matriz de origem e destino é o dado de base.")


def arco(a_ini, a_fim, raio=1.0, n=30):
    """Pontos ao longo de um arco do círculo, do ângulo a_ini até a_fim."""
    t = np.linspace(a_ini, a_fim, n)
    return list(zip(raio * np.cos(t), raio * np.sin(t)))


def corda(a0, a1, b0, b1):
    """Contorno de uma corda: arco na origem, curva pelo centro, arco no destino, curva de volta."""
    pts = arco(a0, a1)
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(pts) - 1)
    pts += [(0, 0), (np.cos(b0), np.sin(b0))]; codes += [MPath.CURVE3, MPath.CURVE3]
    meio = arco(b0, b1)[1:]
    pts += meio; codes += [MPath.LINETO] * len(meio)
    pts += [(0, 0), (np.cos(a0), np.sin(a0))]; codes += [MPath.CURVE3, MPath.CURVE3]
    return MPath(pts, codes)


def gerar():
    d = olist()
    d = d[d.status != "canceled"]
    estados = ["SP", "RJ", "MG", "PR", "RS", "SC"]
    sub = d[d.uf_vendedor.isin(estados) & d.uf_cliente.isin(estados)]
    completo = sub.groupby(["uf_vendedor", "uf_cliente"]).size().unstack(fill_value=0).reindex(index=estados, columns=estados, fill_value=0)
    valores = completo.to_numpy(copy=True)
    np.fill_diagonal(valores, 0)  # só fluxos entre estados diferentes
    m = completo.__class__(valores, index=estados, columns=estados)
    total = m.values.sum()
    vao = np.deg2rad(3)
    util = 2 * np.pi - vao * len(estados)
    # Arco de cada estado = o que ele vende para os outros + o que compra dos outros
    tam = (m.sum(axis=1) + m.sum(axis=0)) / (2 * total) * util
    inicio, ang = {}, np.pi / 2
    for e in estados:
        inicio[e] = ang
        ang -= tam[e] + vao
    escala = util / (2 * total)
    cor = dict(zip(estados, CATEGORICAS))
    cursor = dict(inicio)
    fig, ax = plt.subplots(figsize=(7.8, 7.8))
    # Primeiro a parte de venda de cada arco, depois a de compra: cada corda liga a venda de um à compra do outro
    vendas = {}
    for o in estados:
        for dd in estados:
            w = m.loc[o, dd] * escala
            vendas[(o, dd)] = (cursor[o], cursor[o] - w)
            cursor[o] -= w
    for dd in estados:
        for o in estados:
            w = m.loc[o, dd] * escala
            if w == 0:
                continue
            b0, b1 = cursor[dd], cursor[dd] - w
            cursor[dd] -= w
            a0, a1 = vendas[(o, dd)]
            ax.add_patch(PathPatch(corda(a0, a1, b0, b1), facecolor=cor[o], edgecolor="white", lw=0.3, alpha=0.75))
    for e in estados:
        a_ini, a_fim = np.rad2deg(inicio[e] - tam[e]), np.rad2deg(inicio[e])
        ax.add_patch(Wedge((0, 0), 1.08, a_ini, a_fim, width=0.07, color=cor[e]))
        meio = inicio[e] - tam[e] / 2
        ax.text(1.2 * np.cos(meio), 1.2 * np.sin(meio), e, ha="center", va="center", fontsize=12, fontweight="bold", color=cor[e])
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3); ax.set_aspect("equal"); ax.axis("off")
    sp_vende = m.loc["SP"].sum() / total
    titulo(ax, f"{br(sp_vende * 100)}% dos pedidos entre estados saem de vendedores paulistas",
           "Pedidos entre os 6 maiores estados do Sul e Sudeste, sem contar compras dentro do mesmo estado · cor = estado do vendedor")
    salvar(fig, __file__, FONTES["olist"])
    compra_de_sp = {e: m.loc["SP", e] / m[e].sum() for e in estados if e != "SP"}
    menor = min(compra_de_sp, key=compra_de_sp.get)
    interno = completo.loc["SP", "SP"] / completo.values.sum()
    return (f"A maioria das cordas é verde, a cor de SP: {br(sp_vende * 100)}% dos pedidos entre estados diferentes têm vendedor "
            f"paulista. Mesmo no estado menos dependente ({menor}), {br(compra_de_sp[menor] * 100)}% das compras vindas de fora saem de SP. "
            f"As compras dentro do próprio estado ficaram de fora porque dominariam o desenho: só SP para SP já é {br(interno * 100)}% "
            "dos pedidos entre esses seis estados. O diagrama foi desenhado do zero; com mais de 8 a 10 entidades ele fica ilegível, "
            "e uma matriz de calor passa a ser a melhor saída.")


if __name__ == "__main__":
    print(gerar())
