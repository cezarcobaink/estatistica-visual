"""Funnel plot: separar desempenho ruim de pouco volume."""
from comum import COR, br, np, olist_entregues, plt, salvar, titulo, FONTES
from scipy import stats

META = dict(grupo="Incerteza", nome="Funnel plot",
            pergunta="Quais vendedores atrasam mais do que o acaso explicaria, dado o seu volume?",
            quando="Comparar taxas entre unidades de tamanhos muito diferentes (vendedores, hospitais, lojas) sem punir os pequenos pelo ruído.")


def gerar():
    d = olist_entregues()
    v = d.groupby("vendedor").agg(n=("atraso", "size"), atrasos=("atraso", "sum"))
    v = v[v.n >= 10]
    v["taxa"] = v.atrasos / v.n
    p = v.atrasos.sum() / v.n.sum()
    n = np.logspace(1, np.log10(v.n.max() * 1.1), 200)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    # Limites de controle binomiais: onde a taxa de um vendedor "normal" (taxa = média) cairia por acaso
    for conf, estilo in [(0.95, "--"), (0.998, "-")]:
        z = stats.norm.ppf(1 - (1 - conf) / 2)
        ax.plot(n, (p + z * np.sqrt(p * (1 - p) / n)) * 100, color=COR["texto2"], lw=1.2, ls=estilo)
        ax.plot(n, np.clip(p - z * np.sqrt(p * (1 - p) / n), 0, 1) * 100, color=COR["texto2"], lw=1.2, ls=estilo)
    lim = p + 3.09 * np.sqrt(p * (1 - p) / v.n)
    fora = v.taxa > lim
    ax.scatter(v.n[~fora], v.taxa[~fora] * 100, s=12, color=COR["contexto"], alpha=0.7, lw=0)
    ax.scatter(v.n[fora], v.taxa[fora] * 100, s=22, color=COR["destaque"], lw=0)
    ax.axhline(p * 100, color=COR["principal"], lw=1.5)
    ax.set_xscale("log"); ax.set_ylim(0, 60); ax.set_xlabel("pedidos entregues pelo vendedor (escala log)")
    ax.set_ylabel("% de pedidos atrasados")
    ax.text(n[-1], (p + 3.09 * np.sqrt(p * (1 - p) / n[-1])) * 100 + 1.5, "limite de 99,8%", ha="right", fontsize=9, color=COR["texto2"])
    titulo(ax, f"Só {fora.sum()} de {br(len(v))} vendedores atrasam acima do que o acaso explica",
           "Taxa de atraso por vendedor (10+ pedidos) · linhas = limites de 95% (tracejado) e 99,8% · laranja = acima do limite")
    salvar(fig, __file__, FONTES["olist"])
    pequenos = v[v.n < 30]
    falsos = (pequenos.taxa > 2 * p).sum()
    return (f"A taxa média de atraso é {br(p * 100, 1)}%. Entre os vendedores com menos de 30 pedidos, {falsos} têm taxa acima do dobro "
            f"da média, mas quase todos ficam dentro do funil: com tão poucos pedidos, isso é variação normal. Só {fora.sum()} vendedores "
            f"passam do limite de 99,8%, e são esses que merecem uma conversa. Um ranking simples de taxa colocaria no topo justamente "
            "os pequenos, que tiveram azar.")


if __name__ == "__main__":
    print(gerar())
