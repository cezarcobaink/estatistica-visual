"""Errado × certo: eixo duplo sugere relações que a escala inventa."""
from comum import CATEGORICAS, COR, br, np, olist, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Errado × certo", nome="Eixo duplo × índice",
            pergunta="Pedidos e ticket médio cresceram juntos?",
            quando="Para comparar a evolução de duas grandezas com unidades diferentes, use um índice (base 100) num eixo só.")


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & (d.compra >= "2017-01-01") & (d.compra < "2018-09-01")]
    m = d.groupby(d.compra.dt.to_period("M").dt.to_timestamp()).agg(pedidos=("valor_pago", "size"), ticket=("valor_pago", "mean"))
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw={"wspace": 0.35})
    ax = axes[0]
    ax.plot(m.index, m.pedidos, color=CATEGORICAS[0], lw=2.2)
    ax.set_ylabel("pedidos por mês", color=CATEGORICAS[0])
    ax2 = ax.twinx()
    ax2.plot(m.index, m.ticket, color=CATEGORICAS[1], lw=2.2)
    # O truque do eixo duplo: escolher a escala da direita faz a segunda linha "acompanhar" a primeira
    ax2.set_ylim(m.ticket.min() * 0.985, m.ticket.max() * 1.005)
    ax2.set_ylabel("ticket médio (R$)", color=CATEGORICAS[1]); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax.set_title("Errado: duas escalas escolhidas à mão", fontsize=11, pad=8, color=COR["destaque"])
    ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%m/%y"))
    ax = axes[1]
    base = m.iloc[:3].mean()
    idx = m / base * 100
    ax.plot(m.index, idx.pedidos, color=CATEGORICAS[0], lw=2.2)
    ax.plot(m.index, idx.ticket, color=CATEGORICAS[1], lw=2.2)
    ax.text(m.index[-1], idx.pedidos.iloc[-1], "  pedidos", color=CATEGORICAS[0], va="center", fontsize=10)
    ax.text(m.index[-1], idx.ticket.iloc[-1], "  ticket médio", color=CATEGORICAS[1], va="center", fontsize=10)
    ax.axhline(100, color=COR["texto2"], lw=0.8, ls="--")
    ax.set_ylabel("índice (jan–mar/2017 = 100)"); ax.set_ylim(0, None)
    ax.set_title("Certo: as duas séries como índice num eixo só", fontsize=11, pad=8, color=COR["principal"])
    ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%m/%y"))
    r = np.corrcoef(m.pedidos, m.ticket)[0, 1]
    titulo_figura(fig, f"Os pedidos chegaram a {br(idx.pedidos.max() / 100, 1)}× o início de 2017; o ticket médio ficou praticamente parado",
                  "Mesmos dados nos dois painéis · pedidos e ticket médio por mês, 2017–2018", y=0.97)
    salvar(fig, __file__, FONTES["olist"])
    return (f"No painel da esquerda, a escala da direita vai só de R$ {br(m.ticket.min())} a R$ {br(m.ticket.max())}: variações de "
            f"poucos por cento no ticket ganham a mesma altura da triplicação dos pedidos, e as duas linhas parecem disputar a mesma "
            f"história (a correlação entre elas é {br(r, 2)}). No índice, com as duas séries na "
            f"mesma base, a história real aparece: pedidos chegaram a {br(idx.pedidos.max())} ({br(idx.pedidos.max() / 100, 1)}× o início de 2017) e o "
            f"ticket ficou entre {br(idx.ticket.min())} e {br(idx.ticket.max())}. Eixo duplo deixa quem desenha escolher a conclusão.")


if __name__ == "__main__":
    print(gerar())
