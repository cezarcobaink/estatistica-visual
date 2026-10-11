"""Horizon chart: várias séries longas em pouca altura, com dobra de faixas."""
from comum import COR, DIV, br, np, olist, pd, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Tempo", nome="Horizon chart",
            pergunta="Quando cada região vendeu acima ou abaixo do seu próprio ritmo normal?",
            quando="Comparar muitas séries temporais longas em pouco espaço vertical, focando nos desvios.")

REGIOES = ["Sudeste", "Sul", "Centro-Oeste", "Nordeste", "Norte"]


def horizonte(ax, x, y, faixas=3, limite=None):
    """Desenha um horizon chart: valores positivos em verde e negativos em laranja, dobrados em `faixas` camadas.

    Cada camada cobre 1/faixas do limite; camadas superiores são sobrepostas com cor mais escura na mesma altura.
    """
    limite = limite or np.nanmax(np.abs(y))
    passo = limite / faixas
    for k in range(faixas):
        pos = np.clip(y - k * passo, 0, passo)
        neg = np.clip(-y - k * passo, 0, passo)
        ax.fill_between(x, 0, pos, color=DIV(0.62 + 0.38 * (k + 1) / faixas), lw=0, step="mid")
        ax.fill_between(x, 0, neg, color=DIV(0.38 - 0.38 * (k + 1) / faixas), lw=0, step="mid")
    ax.set_ylim(0, passo)


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & (d.compra >= "2017-03-01") & (d.compra < "2018-08-01")]
    s = d.groupby([d.compra.dt.normalize(), "regiao"]).size().unstack(fill_value=0)[REGIOES]
    # Desvio de cada dia em relação à média móvel de 8 semanas da própria região, em %
    tendencia = s.rolling(56, center=True, min_periods=28).mean()
    desvio = ((s.rolling(7, center=True).mean() / tendencia - 1) * 100).dropna()
    fig, axes = plt.subplots(len(REGIOES), 1, figsize=(11, 4.6), sharex=True, gridspec_kw={"hspace": 0.08})
    for ax, reg in zip(axes, REGIOES):
        horizonte(ax, desvio.index, desvio[reg].to_numpy(), faixas=3, limite=45)
        ax.set_yticks([]); ax.grid(False)
        ax.text(-0.01, 0.5, reg, transform=ax.transAxes, ha="right", va="center", fontsize=10, color=COR["texto"])
        for sp in ax.spines.values():
            sp.set_visible(False)
    axes[-1].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b/%y"))
    pico = desvio.max(axis=1).idxmax()
    titulo_figura(fig, "Choques nacionais viram colunas: Black Friday, fim de ano e a greve de 2018",
                  "Vendas diárias (média de 7 dias) em relação à tendência de 8 semanas de cada região · verde = acima, laranja = abaixo · "
                  "cada tom mais escuro = +15 p.p.", y=0.93)
    salvar(fig, __file__, FONTES["olist"])
    greve = desvio.loc["2018-05-21":"2018-05-31"].mean()
    bf = desvio.loc["2017-11-20":"2017-11-30"].mean()
    return (f"Cada faixa ocupa a altura de uma linha comum, mas guarda até ±45% de desvio, porque os valores grandes são \"dobrados\" "
            f"em tons mais escuros. Assim cinco séries de 17 meses cabem num espaço pequeno. Os choques que atingem o país inteiro aparecem como "
            f"colunas verticais, da mesma cor em todas as faixas: as festas de fim de ano (abaixo da tendência), "
            f"a Black Friday de 2017 (até +{br(bf.max().max())}% acima da tendência) e a greve dos caminhoneiros em maio "
            f"de 2018 (até {br(greve.min().min())}%). Ler o horizon chart exige um minuto de treino; em troca, ele "
            "permite comparar dezenas de séries.")


if __name__ == "__main__":
    print(gerar())
