"""Pequenos múltiplos: um painel por categoria, mesmo eixo."""
from comum import COR, br, filmes, np, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Comparação", nome="Pequenos múltiplos",
            pergunta="Quais gêneros de filme ganharam e perderam espaço nas avaliações publicadas no Twitter?",
            quando="Comparar a evolução de muitas séries sem o emaranhado de linhas sobrepostas (o 'espaguete').")

GENEROS_PT = {"Drama": "Drama", "Comedy": "Comédia", "Action": "Ação", "Thriller": "Suspense", "Adventure": "Aventura",
              "Crime": "Crime", "Romance": "Romance", "Sci-Fi": "Ficção científica", "Horror": "Terror",
              "Fantasy": "Fantasia", "Mystery": "Mistério", "Biography": "Biografia"}


def gerar():
    f = filmes().dropna(subset=["generos"])
    f = f[f.ano.between(2013, 2020)]
    linhas = f.assign(genero=f.generos.str.split("|")).explode("genero")
    total = f.groupby("ano").avaliacoes.sum()
    por = linhas.groupby(["genero", "ano"]).avaliacoes.sum().unstack(0).div(total, axis=0) * 100
    escolhidos = [g for g in GENEROS_PT if g in por.columns][:12]
    fig, axes = plt.subplots(3, 4, figsize=(12, 7.5), sharex=True, sharey=True, gridspec_kw={"hspace": 0.45, "wspace": 0.12})
    variacao = {}
    for ax, g in zip(axes.flat, escolhidos):
        for outro in escolhidos:
            ax.plot(por.index, por[outro], color=COR["grade"], lw=1)
        s = por[g]
        variacao[g] = s.iloc[-1] - s.iloc[0]
        cor = COR["principal"] if variacao[g] > 0 else COR["destaque"]
        ax.plot(por.index, s, color=cor, lw=2.4)
        ax.set_title(f"{GENEROS_PT[g]} ({variacao[g]:+.0f} p.p.)", fontsize=10.5, pad=6, color=COR["texto"])
        ax.set_xticks([2013, 2016, 2020], ["2013", "2016", "2020"])
    for ax in axes[:, 0]:
        ax.set_ylabel("% das avaliações")
    sobe = max(variacao, key=variacao.get); desce = min(variacao, key=variacao.get)
    titulo_figura(fig, f"{GENEROS_PT[sobe]} ganhou espaço; {GENEROS_PT[desce]} perdeu",
                  "% das avaliações de cada ano que envolvem o gênero (um filme pode ter vários) · linhas cinza = outros gêneros",
                  y=0.94)
    salvar(fig, __file__, FONTES["filmes"])
    return (f"Cada painel mostra um gênero contra o fundo cinza de todos os outros, com o mesmo eixo, o que permite comparar "
            f"nível e tendência sem legenda. {GENEROS_PT[sobe]} variou {variacao[sobe]:+.0f} pontos percentuais entre 2013 e 2020; "
            f"{GENEROS_PT[desce]}, {variacao[desce]:+.0f}. Como um filme pode ter vários gêneros, as porcentagens não somam 100%.")


if __name__ == "__main__":
    print(gerar())
