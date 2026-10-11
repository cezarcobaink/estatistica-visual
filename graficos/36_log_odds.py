"""Barras de log-odds: as palavras que mais distinguem avaliações negativas de positivas."""
from collections import Counter

from comum import COR, avaliacoes, br, np, palavras, plt, salvar, titulo, FONTES

META = dict(grupo="Texto", nome="Log-odds de palavras",
            pergunta="Quais palavras são típicas de avaliações negativas, e não só frequentes?",
            quando="Comparar o vocabulário de dois grupos de textos; corrige o viés das palavras comuns, que dominam qualquer contagem.")


def log_odds_dirichlet(c1, c2, prior):
    """Log-odds com prior de Dirichlet informativo (Monroe, Colaresi e Quinn, 2008), em escore z.

    Compara a frequência de cada palavra nos dois grupos, encolhendo as palavras raras em direção ao prior
    (a frequência na base inteira). Sem isso, palavras que aparecem 2 vezes teriam razões enormes por acaso.
    """
    n1, n2, a0 = sum(c1.values()), sum(c2.values()), sum(prior.values())
    z = {}
    for w, a in prior.items():
        y1, y2 = c1.get(w, 0), c2.get(w, 0)
        d = np.log((y1 + a) / (n1 + a0 - y1 - a)) - np.log((y2 + a) / (n2 + a0 - y2 - a))
        var = 1 / (y1 + a) + 1 / (y2 + a)
        z[w] = d / np.sqrt(var)
    return z


def gerar():
    a = avaliacoes()
    neg = Counter(p for t in a[a.nota <= 2].texto for p in palavras(t))
    pos = Counter(p for t in a[a.nota >= 4].texto for p in palavras(t))
    prior = Counter({w: c for w, c in (neg + pos).items() if c >= 30})
    escala = 500 / sum(prior.values())
    prior = {w: c * escala for w, c in prior.items()}
    z = log_odds_dirichlet(neg, pos, prior)
    serie = sorted(z.items(), key=lambda kv: kv[1])
    lados = serie[:12] + serie[-12:]
    fig, ax = plt.subplots(figsize=(9.5, 8))
    y = np.arange(len(lados))
    valores = [v for _, v in lados]
    ax.barh(y, valores, color=[COR["destaque"] if v > 0 else COR["principal"] for v in valores], height=0.7)
    ax.set_yticks(y, [w.replace("nao", "não") for w, _ in lados]); ax.axvline(0, color=COR["texto2"], lw=0.8); ax.grid(axis="y", visible=False)
    ax.set_xlabel("escore z do log-odds (← positivas · negativas →)")
    topo = [w.replace("nao", "não") for w, _ in serie[-3:]][::-1]
    titulo(ax, f"'{topo[0]}', '{topo[1]}' e '{topo[2]}' são as marcas da avaliação negativa",
           "Palavras que mais distinguem avaliações nota 1–2 (laranja) das nota 4–5 (verde) · log-odds com prior de Dirichlet")
    salvar(fig, __file__, FONTES["olist"])
    positivas = [w for w, _ in serie[:3]]
    return (f"Diferente da nuvem, este gráfico mede quanto cada palavra é mais típica de um grupo que do outro. Do lado negativo, "
            f"lideram {', '.join(topo)}; do positivo, {', '.join(positivas)}. O método de Monroe et al. encolhe as palavras raras, "
            "então nenhum termo entra por aparecer duas vezes por acaso. É o tipo de evidência que alimenta um classificador de "
            "sentimento, como no projeto de NLP do repositório de Machine Learning.")


if __name__ == "__main__":
    print(gerar())
