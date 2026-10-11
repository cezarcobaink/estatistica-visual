"""Beeswarm: cada ponto é um cliente, sem sobreposição."""
from comum import CATEGORICAS, COR, br, np, plt, salvar, telco, titulo, FONTES

META = dict(grupo="Distribuição", nome="Beeswarm",
            pergunta="Clientes que cancelaram pagavam mensalidades diferentes dos que ficaram?",
            quando="Mostrar cada observação quando o número de pontos é moderado (centenas), mantendo a forma da distribuição.")


def enxame(valores, largura_bin, passo):
    """Posições horizontais de um beeswarm: pontos no mesmo intervalo de valor se espalham para os lados."""
    ordem = np.argsort(valores)
    desloc = np.zeros(len(valores))
    bins = np.floor(valores[ordem] / largura_bin)
    contagem = {}
    for k, b in zip(ordem, bins):
        n = contagem.get(b, 0)
        # alterna esquerda e direita: 0, +1, −1, +2, −2...
        desloc[k] = ((n + 1) // 2) * passo * (1 if n % 2 else -1)
        contagem[b] = n + 1
    return desloc


def gerar():
    d = telco()
    rng = np.random.default_rng(1)
    fig, ax = plt.subplots(figsize=(10, 5))
    grupos = [("Ficou", 0, CATEGORICAS[0]), ("Cancelou", 1, CATEGORICAS[1])]
    medianas = {}
    for i, (nome, valor, cor) in enumerate(grupos):
        x = d.loc[d.saiu == valor, "MonthlyCharges"].to_numpy()
        medianas[nome] = np.median(x)
        amostra = rng.choice(x, 450, replace=False)
        y = i + enxame(amostra, largura_bin=2.0, passo=0.018)
        ax.scatter(amostra, y, s=9, color=cor, alpha=0.8, lw=0)
        ax.plot([medianas[nome]] * 2, [i - 0.38, i + 0.38], color=COR["texto"], lw=1.5)
        ax.text(medianas[nome], i + 0.42, f"mediana US$ {br(medianas[nome])}", ha="center", fontsize=9, color=COR["texto"])
    ax.set_yticks([0, 1], [g[0] for g in grupos]); ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel("mensalidade (US$)"); ax.grid(axis="y", visible=False)
    baixo = (d.loc[d.saiu == 0, "MonthlyCharges"] < 30).mean()
    titulo(ax, "Quem cancela paga mais; abaixo de US$ 30, quase ninguém sai",
           "Mensalidade de 450 clientes sorteados de cada grupo · cada ponto é um cliente")
    salvar(fig, __file__, FONTES["telco"])
    tx_baixo = d.loc[d.MonthlyCharges < 30, "saiu"].mean()
    tx_alto = d.loc[d.MonthlyCharges.between(70, 110), "saiu"].mean()
    return (f"A mediana de quem cancelou é US$ {br(medianas['Cancelou'])}, contra US$ {br(medianas['Ficou'])} de quem ficou. "
            f"O enxame mostra o que a média esconde: a distribuição de quem fica é bimodal, com um bloco grande abaixo de US$ 30 "
            f"(planos sem internet), onde só {br(tx_baixo * 100)}% cancelam. Entre US$ 70 e 110, o cancelamento sobe para {br(tx_alto * 100)}%. "
            f"{br(baixo * 100)}% de quem ficou paga menos de US$ 30.")


if __name__ == "__main__":
    print(gerar())
