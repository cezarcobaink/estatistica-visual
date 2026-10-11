"""Streamgraph: área empilhada com base que oscila em torno do centro."""
from comum import CATEGORICAS, COR, br, filmes, np, plt, salvar, titulo, FONTES

META = dict(grupo="Tempo", nome="Streamgraph",
            pergunta="Como o volume de avaliações de cada gênero evoluiu de 2013 a 2021?",
            quando="Mostrar o volume total e a mistura de categorias ao longo do tempo de forma expressiva, quando a leitura exata importa menos.")

PT = {"Drama": "Drama", "Comedy": "Comédia", "Action": "Ação", "Thriller": "Suspense", "Adventure": "Aventura", "Crime": "Crime"}


def gerar():
    f = filmes().dropna(subset=["generos"])
    f = f[f.ano.between(2013, 2021)]
    linhas = f.assign(genero=f.generos.str.split("|")).explode("genero")
    linhas["genero"] = linhas.genero.where(linhas.genero.isin(PT), "Outros")
    t = linhas.groupby(["ano", "genero"]).avaliacoes.sum().unstack(fill_value=0)
    t = t[list(PT) + ["Outros"]] / 1000
    # Interpolação suave entre anos, só para o desenho (os valores anuais ficam nos pontos inteiros)
    x = np.linspace(t.index.min(), t.index.max(), 200)
    Y = np.array([np.interp(x, t.index, t[c]) for c in t.columns])
    fig, ax = plt.subplots(figsize=(11, 5.6))
    cores = CATEGORICAS + [COR["contexto"]]
    ax.stackplot(x, Y, baseline="sym", colors=cores, alpha=0.9, edgecolor="white", lw=0.4)
    ax.set_xlim(x[0], x[-1]); ax.set_yticks([]); ax.grid(axis="y", visible=False)
    ax.legend([PT.get(c, c) for c in t.columns], loc="upper right", ncol=4, fontsize=9)
    total = t.sum(axis=1)
    pico = total.idxmax()
    titulo(ax, f"O volume de avaliações no Twitter caiu {br((1 - total.iloc[-1] / total.max()) * 100)}% desde o pico de {pico}",
           "Milhares de avaliações por gênero e ano (um filme pode contar em vários gêneros) · espessura = volume")
    salvar(fig, __file__, FONTES["filmes"])
    return (f"O streamgraph empilha as camadas em torno de um eixo central que oscila, o que deixa o desenho fluido e chama a atenção "
            f"para o volume total: o pico foi em {pico} e, até 2021, o volume caiu {br((1 - total.iloc[-1] / total.max()) * 100)}%, "
            "provavelmente porque a base só capta tweets gerados automaticamente pelo app do IMDb, um hábito que perdeu força. O custo: sem uma base fixa, comparar a espessura de "
            "uma camada entre anos é impreciso. Para análise, pequenos múltiplos (gráfico 12) são melhores; para apresentação, este impressiona.")


if __name__ == "__main__":
    print(gerar())
