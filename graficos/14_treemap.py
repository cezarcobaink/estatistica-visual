"""Treemap com o algoritmo squarify implementado do zero."""
from comum import COR, SEQ, br, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Composição", nome="Treemap",
            pergunta="Como o faturamento da Olist se divide entre as categorias de produto?",
            quando="Mostrar a composição de um total com muitas partes (dezenas), quando a área relativa basta e a ordem exata não importa.")


def squarify(valores, x, y, largura, altura):
    """Algoritmo squarified (Bruls, Huizing e van Wijk, 2000): retângulos o mais próximos possível de quadrados.

    Os valores, em ordem decrescente e já escalados para somar largura × altura, são colocados em fileiras ao longo
    do lado menor do espaço livre; uma fileira cresce enquanto isso melhora a pior proporção entre lados.
    """
    retangulos = []
    valores = list(valores)
    while valores:
        lado = min(largura, altura)
        fileira, pior = [], float("inf")
        while valores:
            teste = fileira + [valores[0]]
            soma = sum(teste)
            proporcao = max(max(lado ** 2 * v / soma ** 2, soma ** 2 / (lado ** 2 * v)) for v in teste)
            if proporcao > pior:
                break
            fileira, pior = teste, proporcao
            valores.pop(0)
        soma = sum(fileira)
        espessura = soma / lado
        pos = 0
        for v in fileira:
            comprimento = v / espessura
            if largura >= altura:  # fileira vertical na esquerda
                retangulos.append((x, y + pos, espessura, comprimento))
            else:                  # fileira horizontal embaixo
                retangulos.append((x + pos, y, comprimento, espessura))
            pos += comprimento
        if largura >= altura:
            x, largura = x + espessura, largura - espessura
        else:
            y, altura = y + espessura, altura - espessura
    return retangulos


def gerar():
    d = olist()
    d = d[d.status != "canceled"]
    receita = d.groupby("categoria_pt").valor_itens.sum().sort_values(ascending=False)
    top = receita.iloc[:18]
    outras = receita.iloc[18:].sum()
    nomes = list(top.index) + [f"Outras {len(receita) - 18} categorias"]
    valores = list(top.values) + [outras]
    total = sum(valores)
    L, A = 16, 9
    escala = [v / total * L * A for v in valores]
    rets = squarify(escala, 0, 0, L, A)
    fig, ax = plt.subplots(figsize=(12, 6.8))
    for i, ((x, y, w, h), nome, v) in enumerate(zip(rets, nomes, valores)):
        cor = COR["contexto"] if nome.startswith("Outras") else SEQ(0.95 - 0.7 * i / len(top))
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=cor, edgecolor="white", lw=2))
        if w * h > 1.2:
            claro = i < 8 and not nome.startswith("Outras")
            ax.text(x + 0.12, y + h - 0.15, f"{nome}\n{br(v / total * 100, 1)}%", va="top", fontsize=9 if w > 1.6 else 7.5,
                    color="white" if claro else COR["texto"])
    ax.set_xlim(0, L); ax.set_ylim(0, A); ax.set_aspect("equal"); ax.axis("off")
    top5 = sum(valores[:5]) / total
    titulo(ax, f"Cinco categorias fazem {br(top5 * 100)}% do faturamento; a cauda longa soma {br(outras / total * 100)}%",
           "Faturamento em itens por categoria, 2016–2018 · área proporcional à receita")
    salvar(fig, __file__, FONTES["olist"])
    return (f"{nomes[0]} lidera com {br(valores[0] / total * 100, 1)}% do faturamento. As cinco maiores categorias somam "
            f"{br(top5 * 100)}%, e as {len(receita) - 18} menores, juntas, {br(outras / total * 100)}%. O algoritmo squarify "
            "(implementado do zero, sem biblioteca) mantém os retângulos próximos de quadrados, o que torna as áreas comparáveis. "
            "Para comparar valores com precisão, porém, barras ordenadas são melhores: o olho humano compara comprimentos melhor que áreas.")


if __name__ == "__main__":
    print(gerar())
