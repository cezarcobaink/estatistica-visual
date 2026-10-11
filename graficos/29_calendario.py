"""Heatmap de calendário: um quadrado por dia, no formato do GitHub."""
from comum import COR, SEQ, br, np, olist, pd, plt, salvar, titulo, FONTES

META = dict(grupo="Tempo", nome="Heatmap de calendário",
            pergunta="Em quais dias de 2017 a Olist vendeu mais?",
            quando="Mostrar uma série diária de um ano inteiro, deixando visíveis o padrão semanal e os dias excepcionais.")

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def gerar():
    d = olist()
    d = d[d.status != "canceled"]
    serie = d.groupby(d.compra.dt.normalize()).size().reindex(pd.date_range("2017-01-01", "2017-12-31"), fill_value=0)
    semana = ((serie.index - pd.Timestamp("2016-12-26")).days // 7).to_numpy()
    dia = serie.index.dayofweek.to_numpy()
    M = np.full((7, semana.max() + 1), np.nan)
    M[dia, semana] = serie.values
    fig, ax = plt.subplots(figsize=(12.5, 3.6))
    im = ax.imshow(M, cmap=SEQ, aspect="equal", vmin=0, vmax=np.nanpercentile(M, 99))
    # grade branca entre os dias
    ax.set_xticks(np.arange(-0.5, M.shape[1], 1), minor=True); ax.set_yticks(np.arange(-0.5, 7, 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.5); ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)
    inicio_mes = [((pd.Timestamp(2017, m, 1) - pd.Timestamp("2016-12-26")).days // 7) for m in range(1, 13)]
    ax.set_xticks(inicio_mes, MESES); ax.set_yticks(range(7), DIAS)
    pico = serie.idxmax()
    fig.colorbar(im, ax=ax, shrink=0.45, pad=0.01, label="pedidos")
    for s in ax.spines.values():
        s.set_visible(False)
    fim_semana = serie[serie.index.dayofweek >= 5].mean() / serie[serie.index.dayofweek < 5].mean()
    titulo(ax, f"A Black Friday ({pico:%d/%m}) vendeu {br(serie.max() / serie.median(), 1)}× um dia típico de 2017",
           "Pedidos por dia em 2017 · cada quadrado é um dia, cada coluna é uma semana · o quadrado mais escuro é 24/11")
    salvar(fig, __file__, FONTES["olist"], y_fonte=-0.08)
    return (f"O calendário mostra três coisas que uma linha diária misturaria: o crescimento ao longo do ano (as colunas escurecem), "
            f"o padrão semanal (sábados e domingos vendem {br((1 - fim_semana) * 100)}% menos que os dias úteis) e o pico isolado da "
            f"Black Friday, com {br(serie.max())} pedidos em {pico:%d/%m}, {br(serie.max() / serie.median(), 1)}× a mediana diária do ano.")


if __name__ == "__main__":
    print(gerar())
