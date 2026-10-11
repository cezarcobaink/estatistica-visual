"""Alluvial: o caminho dos clientes por várias variáveis categóricas."""
from comum import COR, br, faixa, plt, salvar, telco, titulo, FONTES

META = dict(grupo="Fluxo", nome="Alluvial",
            pergunta="Por quais combinações de contrato e internet passam os clientes que cancelam?",
            quando="Seguir indivíduos por três ou mais classificações sucessivas e ver onde os caminhos se concentram.")

ETAPAS = [("contrato", ["Mensal", "1 ano", "2 anos"]),
          ("internet", ["Fibra", "DSL", "Sem internet"]),
          ("status", ["Cancelou", "Ficou"])]


def gerar():
    d = telco().copy()
    d["internet"] = d.InternetService.map({"Fiber optic": "Fibra", "DSL": "DSL", "No": "Sem internet"})
    d["status"] = d.saiu.map({1: "Cancelou", 0: "Ficou"})
    n = len(d); vao = 0.03
    xs = [0, 1, 2]; larg = 0.06

    def nos(col, ordem):
        cont = d[col].value_counts()
        util = 1 - vao * (len(ordem) - 1)
        pos, y = {}, 1.0
        for k in ordem:
            h = cont.get(k, 0) / n * util
            pos[k] = [y - h, y]
            y -= h + vao
        return pos, util

    posicoes = [nos(c, o) for c, o in ETAPAS]
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    # Fitas coloridas pelo desfecho final: o leitor segue os que cancelaram desde o início
    cor_status = {"Cancelou": COR["destaque"], "Ficou": COR["contexto"]}
    for e in range(len(ETAPAS) - 1):
        (c0, o0), (c1, o1) = ETAPAS[e], ETAPAS[e + 1]
        (p0, u0), (p1, u1) = posicoes[e], posicoes[e + 1]
        cur0 = {k: p0[k][1] for k in o0}
        cur1 = {k: p1[k][1] for k in o1}
        grupos = d.groupby([c0, c1, "status"]).size()
        for a in o0:
            for b in o1:
                for s in ["Cancelou", "Ficou"]:
                    v = grupos.get((a, b, s), 0)
                    if v == 0:
                        continue
                    h0, h1 = v / n * u0, v / n * u1
                    faixa(ax, xs[e] + larg, (cur0[a] - h0, cur0[a]), xs[e + 1], (cur1[b] - h1, cur1[b]), cor_status[s],
                          alpha=0.75 if s == "Cancelou" else 0.45)
                    cur0[a] -= h0; cur1[b] -= h1
    for e, ((col, ordem), (pos, _)) in enumerate(zip(ETAPAS, posicoes)):
        for k in ordem:
            ax.add_patch(plt.Rectangle((xs[e], pos[k][0]), larg, pos[k][1] - pos[k][0], color=COR["texto"]))
            ha, dx = ("right", -0.02) if e == 0 else ("left", larg + 0.02)
            ax.text(xs[e] + dx, sum(pos[k]) / 2, k, ha=ha, va="center", fontsize=10, color=COR["texto"])
        ax.text(xs[e] + larg / 2, 1.04, col.capitalize(), ha="center", fontsize=10.5, fontweight="bold", color=COR["texto2"])
    ax.set_xlim(-0.35, 2.4); ax.set_ylim(-0.02, 1.08); ax.axis("off")
    canc = d[d.saiu == 1]
    caminho = (canc.contrato.eq("Mensal") & canc.internet.eq("Fibra")).mean()
    titulo(ax, f"{br(caminho * 100)}% de quem cancela tem contrato mensal e fibra",
           "Clientes por contrato, tipo de internet e desfecho · laranja = cancelou, cinza = ficou")
    salvar(fig, __file__, FONTES["telco"])
    taxa = d[(d.contrato == "Mensal") & (d.internet == "Fibra")].saiu.mean()
    return (f"Colorir as fitas pelo desfecho final permite seguir quem cancelou desde a primeira etapa. O caminho contrato mensal "
            f"→ fibra concentra {br(caminho * 100)}% dos cancelamentos, e nesse grupo {br(taxa * 100)}% dos clientes cancelaram. "
            "Contratos de 2 anos quase não têm fitas laranjas. É a mesma informação de uma tabela cruzada de três dimensões, mas "
            "a hierarquia dos fluxos aparece de imediato.")


if __name__ == "__main__":
    print(gerar())
