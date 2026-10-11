"""UpSet: interseções de conjuntos (a alternativa legível ao diagrama de Venn)."""
from itertools import compress

from comum import COR, br, np, plt, salvar, telco, titulo_figura, FONTES

META = dict(grupo="Composição", nome="UpSet",
            pergunta="Quais combinações de serviços extras os clientes de internet contratam, e quais cancelam menos?",
            quando="Mostrar interseções entre mais de 3 conjuntos, onde um diagrama de Venn fica ilegível.")

SERVICOS = {"OnlineSecurity": "Segurança", "OnlineBackup": "Backup", "TechSupport": "Suporte técnico",
            "StreamingTV": "TV", "StreamingMovies": "Filmes"}


def gerar():
    d = telco()
    d = d[d.InternetService != "No"].copy()
    tem = (d[list(SERVICOS)] == "Yes").astype(int)
    d["combo"] = tem.astype(str).agg("".join, axis=1)
    g = d.groupby("combo").agg(clientes=("saiu", "size"), churn=("saiu", "mean")).sort_values("clientes", ascending=False).head(14)
    fig = plt.figure(figsize=(11, 6.6))
    grade = fig.add_gridspec(3, 1, height_ratios=[2.2, 1.2, 1.6], hspace=0.12)
    ax_barra, ax_churn, ax_mat = (fig.add_subplot(grade[i]) for i in range(3))
    x = np.arange(len(g))
    ax_barra.bar(x, g.clientes, color=COR["principal"], width=0.6)
    for xi, v in zip(x, g.clientes):
        ax_barra.text(xi, v + 15, br(v), ha="center", fontsize=8.5, color=COR["texto"])
    ax_barra.set_ylabel("clientes"); ax_barra.set_xticks([]); ax_barra.grid(axis="x", visible=False)
    media = d.saiu.mean()
    cores = [COR["destaque"] if c > media else COR["principal"] for c in g.churn]
    ax_churn.scatter(x, g.churn * 100, color=cores, s=40, zorder=3)
    ax_churn.vlines(x, media * 100, g.churn * 100, color=cores, lw=1.5)
    ax_churn.axhline(media * 100, color=COR["texto2"], lw=1, ls="--")
    ax_churn.set_ylabel("% cancelou"); ax_churn.set_xticks([]); ax_churn.grid(axis="x", visible=False)
    nomes = list(SERVICOS.values())
    for j in range(len(nomes)):
        ax_mat.scatter(x, [j] * len(x), color=COR["grade"], s=60, zorder=1)
    for xi, combo in zip(x, g.index):
        ativos = [j for j, c in enumerate(combo) if c == "1"]
        if ativos:
            ax_mat.scatter([xi] * len(ativos), ativos, color=COR["texto"], s=60, zorder=2)
            ax_mat.plot([xi, xi], [min(ativos), max(ativos)], color=COR["texto"], lw=2)
    ax_mat.set_yticks(range(len(nomes)), nomes); ax_mat.set_xticks([]); ax_mat.grid(False); ax_mat.invert_yaxis()
    for a in (ax_barra, ax_churn, ax_mat):
        a.set_xlim(-0.6, len(g) - 0.4)
    nenhum = g.loc["00000"]
    completo_seg = d[(tem.OnlineSecurity == 1) & (tem.TechSupport == 1)].saiu.mean()
    titulo_figura(fig, f"Sem nenhum serviço extra, {br(nenhum.churn * 100)}% cancelam; com segurança e suporte, {br(completo_seg * 100)}%",
                  "As 14 combinações mais comuns de serviços extras entre clientes de internet · pontos pretos = serviços contratados", y=0.93)
    salvar(fig, __file__, FONTES["telco"])
    pior = g.churn.idxmax()
    pior_nomes = " + ".join(compress(nomes, [c == "1" for c in pior]))
    return (f"A combinação mais comum é não contratar nada ({br(nenhum.clientes)} clientes), com {br(nenhum.churn * 100)}% de "
            f"cancelamento, contra {br(media * 100)}% na média. Quem contrata só streaming cancela ainda mais: com apenas {pior_nomes}, chega a "
            f"{br(g.churn.max() * 100)}%. Combinações com segurança online e suporte técnico "
            f"cancelam bem menos ({br(completo_seg * 100)}%). Com cinco serviços, um diagrama de Venn teria 31 regiões; o UpSet "
            "lista as combinações como colunas e ainda permite pendurar uma métrica (aqui, o cancelamento) em cada uma. "
            "É associação, não causa: quem contrata mais serviços já é um cliente mais engajado.")


if __name__ == "__main__":
    print(gerar())
