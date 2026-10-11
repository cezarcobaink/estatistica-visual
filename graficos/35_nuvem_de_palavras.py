"""Nuvem de palavras implementada do zero (espiral + detecção de colisão)."""
from collections import Counter

from comum import COR, SEQ, avaliacoes, br, np, palavras, plt, salvar, titulo, FONTES

META = dict(grupo="Texto", nome="Nuvem de palavras",
            pergunta="Que palavras os clientes insatisfeitos mais usam?",
            quando="Dar uma primeira impressão de um texto para público amplo; para análise, prefira barras (veja o gráfico seguinte).")


def nuvem(ax, freq, largura=12, altura=6.5, tam_max=46, tam_min=9, semente=0):
    """Posiciona as palavras numa espiral de Arquimedes a partir do centro, sem sobreposição.

    Para cada palavra (da mais frequente para a menos), anda pela espiral até achar um ponto onde a caixa
    do texto não colide com as já colocadas. O tamanho da fonte é proporcional à raiz da frequência,
    para que a área (e não a altura) acompanhe a contagem.
    """
    fig = ax.figure
    renderer = fig.canvas.get_renderer()
    rng = np.random.default_rng(semente)
    ax.set_xlim(-largura / 2, largura / 2); ax.set_ylim(-altura / 2, altura / 2)
    maximo = max(freq.values())
    caixas = []
    para_dados = ax.transData.inverted()
    colocadas = 0
    for i, (p, f) in enumerate(freq.items()):
        tamanho = tam_min + (tam_max - tam_min) * np.sqrt(f / maximo)
        cor = SEQ(0.45 + 0.55 * np.sqrt(f / maximo)) if i % 4 else COR["destaque"]
        texto = ax.text(0, 0, p, fontsize=tamanho, ha="center", va="center", color=cor, fontweight="bold")
        inicio = rng.uniform(0, 2 * np.pi)
        for passo in range(4000):
            t = passo * 0.12
            x, y = 0.09 * t * np.cos(t + inicio) * 1.6, 0.09 * t * np.sin(t + inicio)
            texto.set_position((x, y))
            bb = texto.get_window_extent(renderer).transformed(para_dados)
            dentro = bb.x0 > -largura / 2 and bb.x1 < largura / 2 and bb.y0 > -altura / 2 and bb.y1 < altura / 2
            if dentro and not any(bb.overlaps(c) for c in caixas):
                caixas.append(bb.expanded(1.04, 1.08))
                colocadas += 1
                break
        else:
            texto.remove()
    ax.axis("off")
    return colocadas


def gerar():
    a = avaliacoes()
    negativas = a[a.nota <= 2].texto
    def tokens(texto):
        """Palavras do texto, com o 'não' grudado na palavra seguinte ('não recebi' vira um termo só)."""
        ps, saida, i = palavras(texto), [], 0
        while i < len(ps):
            if ps[i] == "nao" and i + 1 < len(ps):
                saida.append(f"não {ps[i + 1]}")
                i += 2
            else:
                saida.append(ps[i])
                i += 1
        return saida

    cont = Counter(p for t in negativas for p in tokens(t))
    for k in ["nao", "produto", "compra", "pedido"]:
        cont.pop(k, None)
    freq = dict(cont.most_common(70))
    fig, ax = plt.subplots(figsize=(12, 6.8))
    n = nuvem(ax, freq)
    top = list(freq)[:5]
    titulo(ax, f"Nas avaliações negativas, as palavras dominantes falam de entrega: {', '.join(top[:3])}",
           f"{n} palavras mais frequentes em {br(len(negativas))} avaliações com nota 1 ou 2 · tamanho ∝ raiz da frequência")
    salvar(fig, __file__, FONTES["olist"])
    return (f"As maiores palavras ({', '.join(top)}) contam a história da insatisfação: entrega e prazo. Duas decisões tornam a nuvem "
            "útil: as palavras óbvias de qualquer avaliação ('produto', 'pedido', 'compra') foram tiradas, e o 'não' foi juntado à "
            "palavra seguinte, porque 'não recebi' e 'recebi' dizem o oposto. A nuvem foi implementada do zero: as palavras andam numa "
            "espiral a partir do centro até encontrar espaço livre. Limite: o tamanho de fonte é difícil de comparar e palavras longas "
            "parecem mais importantes. Por isso o próximo gráfico refaz a análise com barras.")


if __name__ == "__main__":
    print(gerar())
