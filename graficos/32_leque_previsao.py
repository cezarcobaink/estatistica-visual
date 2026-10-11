"""Fan chart: previsão com faixas de incerteza crescentes."""
from comum import COR, SEQ, br, np, olist, pd, plt, salvar, titulo, FONTES

META = dict(grupo="Tempo", nome="Fan chart (leque de incerteza)",
            pergunta="Quantos pedidos esperar nas próximas 12 semanas, e com quanta incerteza?",
            quando="Comunicar uma previsão sem fingir precisão: as faixas mostram o que é plausível e como a incerteza cresce com o horizonte.")


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & (d.compra >= "2017-01-02") & (d.compra < "2018-06-04")]
    semanal = d.groupby(d.compra.dt.to_period("W-SUN").dt.start_time).size()
    corte = pd.Timestamp("2018-03-05")
    hist = semanal[semanal.index < corte]
    real = semanal[semanal.index >= corte]
    # Passeio aleatório em log: ponto de partida = média das últimas 4 semanas; volatilidade semanal estimada
    # pelo desvio absoluto mediano (MAD) das variações das últimas 26 semanas, robusto a picos como a Black Friday
    variacoes = np.diff(np.log(hist.values))[-26:]
    sigma = 1.4826 * np.median(np.abs(variacoes - np.median(variacoes)))
    nivel = np.log(hist.iloc[-4:].mean())
    h = len(real)
    rng = np.random.default_rng(0)
    sim = np.exp(nivel + np.cumsum(rng.normal(0, sigma, size=(5000, h)), axis=1))
    datas = real.index
    fig, ax = plt.subplots(figsize=(10.5, 5))
    ax.plot(hist.index[-40:], hist.values[-40:], color=COR["texto"], lw=1.8, label="histórico")
    faixas = [(5, 95), (10, 90), (25, 75)]
    for i, (lo, hi) in enumerate(faixas):
        ax.fill_between(datas, np.percentile(sim, lo, axis=0), np.percentile(sim, hi, axis=0), color=SEQ(0.35 + 0.25 * i), lw=0,
                        label=f"{hi - lo}% das trajetórias")
    ax.plot(datas, np.median(sim, axis=0), color=COR["principal"], lw=2, ls="--", label="mediana")
    ax.plot(datas, real.values, color=COR["destaque"], lw=2, marker="o", ms=4, label="o que aconteceu")
    ax.axvline(corte, color=COR["texto2"], lw=1, ls=":")
    ax.set_ylabel("pedidos por semana"); ax.set_ylim(0, None); ax.legend(loc="lower left", ncol=3, fontsize=9)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b/%y"))
    lo90, hi90 = np.percentile(sim, 5, axis=0), np.percentile(sim, 95, axis=0)
    dentro = ((real.values >= lo90) & (real.values <= hi90)).mean()
    posicao = (real.values - lo90) / (hi90 - lo90)
    mais_baixa = real.index[np.argmin(posicao)]
    titulo(ax, f"Em 3 meses, a faixa de 90% vai de {br(lo90[-1])} a {br(hi90[-1])} pedidos por semana: larga demais para planejar com um número",
           f"Previsão feita em mar/2018: passeio aleatório em log com volatilidade robusta (σ = {br(sigma * 100, 1)}% por semana) · 5 mil trajetórias")
    salvar(fig, __file__, FONTES["olist"])
    return (f"Cada tom do leque é uma faixa de probabilidade, que se abre com o horizonte porque os erros se acumulam. A previsão "
            f"central quase não tem informação: é o nível atual. O valor está nas faixas, que dizem para que volume a operação deve "
            f"estar preparada. Conferindo com o que aconteceu, {int(round(dentro * h))} das {h} semanas ficaram dentro da faixa de 90%, "
            f"mas a faixa é larga: na 13ª semana vai de {br(lo90[-1])} a {br(hi90[-1])} pedidos. A semana mais perto da borda "
            f"inferior é a de {mais_baixa:%d/%m}, a greve dos caminhoneiros. É a mesma conclusão do projeto de previsão de demanda: a "
            "três meses a incerteza domina, e replanejar toda semana vale mais que um modelo mais sofisticado. A volatilidade foi "
            "estimada pela mediana dos desvios (MAD), que não deixa a Black Friday inflar o leque.")


if __name__ == "__main__":
    print(gerar())
