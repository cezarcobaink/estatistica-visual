"""Rede de coocorrência: quais gêneros aparecem juntos nos mesmos filmes."""
import networkx as nx

from comum import COR, SEQ, br, filmes, np, plt, salvar, titulo, FONTES
from itertools import combinations

META = dict(grupo="Relação", nome="Rede de coocorrência",
            pergunta="Quais gêneros de filme costumam aparecer juntos?",
            quando="Mostrar relações entre entidades (coocorrência, conexões) quando a estrutura da rede é a mensagem.")

PT = {"Drama": "Drama", "Comedy": "Comédia", "Action": "Ação", "Thriller": "Suspense", "Adventure": "Aventura", "Crime": "Crime",
      "Romance": "Romance", "Sci-Fi": "Ficção científica", "Horror": "Terror", "Fantasy": "Fantasia", "Mystery": "Mistério",
      "Biography": "Biografia", "Animation": "Animação", "Family": "Família", "History": "História", "War": "Guerra",
      "Music": "Música", "Sport": "Esporte", "Documentary": "Documentário", "Western": "Faroeste", "Musical": "Musical"}


def gerar():
    f = filmes().drop_duplicates("filme").dropna(subset=["generos"])
    listas = [[g for g in s.split("|") if g in PT] for s in f.generos]
    cont, pares = {}, {}
    for gs in listas:
        for g in gs:
            cont[g] = cont.get(g, 0) + 1
        for a, b in combinations(sorted(set(gs)), 2):
            pares[(a, b)] = pares.get((a, b), 0) + 1
    n = len(listas)
    G = nx.Graph()
    for g, c in cont.items():
        G.add_node(g, n=c)
    # Lift: quantas vezes mais o par aparece do que apareceria se os gêneros fossem independentes
    for (a, b), c in pares.items():
        lift = c * n / (cont[a] * cont[b])
        if c >= 150 and lift > 1.3:
            G.add_edge(a, b, peso=c, lift=lift)
    G.remove_nodes_from([v for v in list(G.nodes) if G.degree(v) == 0])
    pos = nx.spring_layout(G, weight="lift", seed=7, k=0.9)
    fig, ax = plt.subplots(figsize=(10, 8))
    lifts = np.array([G.edges[e]["lift"] for e in G.edges])
    for (a, b), l in zip(G.edges, lifts):
        ax.plot(*zip(pos[a], pos[b]), color=SEQ(min(1, 0.3 + (l - 1.3) / 3)), lw=0.8 + 4 * (l - 1.3) / (lifts.max() - 1.3), zorder=1,
                alpha=0.85)
    tam = np.array([G.nodes[v]["n"] for v in G.nodes])
    ax.scatter([pos[v][0] for v in G.nodes], [pos[v][1] for v in G.nodes], s=60 + 1400 * tam / tam.max(),
               color=COR["destaque"], edgecolor="white", lw=1.5, zorder=2)
    for v in G.nodes:
        ax.text(pos[v][0], pos[v][1] - 0.07, PT[v], ha="center", va="top", fontsize=9.5, color=COR["texto"], zorder=3)
    ax.axis("off")
    top = sorted(G.edges(data=True), key=lambda e: -e[2]["lift"])[:3]
    a, b, dados = top[0]
    titulo(ax, f"{PT[a]} e {PT[b]} aparecem juntos {br(dados['lift'], 1)}× mais que o acaso",
           "Gêneros ligados quando coocorrem mais que o esperado (lift > 1,3) · espessura = lift · tamanho = nº de filmes")
    salvar(fig, __file__, FONTES["filmes"])
    outros = "; ".join(f"{PT[x]} + {PT[y]} ({br(dd['lift'], 1)}×)" for x, y, dd in top[1:])
    return (f"A ligação usa o lift, não a contagem bruta: Drama aparece com tudo porque é o gênero mais comum, e isso não é afinidade. "
            f"Pelo lift, {PT[a]} e {PT[b]} são o par mais forte ({br(dados['lift'], 1)}×), seguidos de {outros}. "
            "Os grupos que surgem (família/animação/aventura, crime/suspense/mistério) são a base de um recomendador por conteúdo.")


if __name__ == "__main__":
    print(gerar())
