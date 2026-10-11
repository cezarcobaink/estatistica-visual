"""Área empilhada 100%: composição ao longo do tempo."""
from comum import CATEGORICAS, COR, PAGAMENTO_PT, br, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Composição", nome="Área empilhada 100%",
            pergunta="A mistura de formas de pagamento mudou ao longo de 2017 e 2018?",
            quando="Acompanhar a composição de um total no tempo; só a primeira e a última camada têm base fixa e são fáceis de ler.")


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & (d.compra >= "2017-01-01") & (d.compra < "2018-09-01")]
    d = d[d.pagamento.isin(["credit_card", "boleto", "voucher", "debit_card"])]
    m = d.groupby([d.compra.dt.to_period("M").dt.to_timestamp(), "pagamento"]).size().unstack(fill_value=0)
    m = m[["credit_card", "boleto", "voucher", "debit_card"]]
    p = m.div(m.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.stackplot(p.index, p.T.values, colors=CATEGORICAS[:4], alpha=0.9, edgecolor="white", lw=0.6)
    meio = p.index[len(p) // 2]
    acumulado = 0
    for j, metodo in enumerate(p.columns):
        h = p.loc[meio, metodo]
        if h > 3:
            ax.text(meio, acumulado + h / 2, PAGAMENTO_PT[metodo], ha="center", va="center", fontsize=10, color="white")
        acumulado += h
    ax.set_ylim(0, 100); ax.set_xlim(p.index[0], p.index[-1]); ax.set_ylabel("% dos pedidos do mês")
    debito = p.debit_card
    titulo(ax, f"A mistura é estável; o débito cresce aos poucos, de {br(debito.iloc[0], 1)}% para {br(debito.iloc[-1], 1)}%",
           "Participação de cada forma de pagamento nos pedidos de cada mês, jan/2017 a ago/2018")
    salvar(fig, __file__, FONTES["olist"])
    return (f"Cartão de crédito oscila entre {br(p.credit_card.min())}% e {br(p.credit_card.max())}% e o boleto entre "
            f"{br(p.boleto.min())}% e {br(p.boleto.max())}%. O cartão de débito, ainda pequeno, sobe de {br(debito.iloc[0], 1)}% "
            f"para {br(debito.iloc[-1], 1)}%. Cuidado de leitura: as camadas do meio não têm base fixa; para comparar o boleto entre meses, "
            "uma linha simples seria mais precisa.")


if __name__ == "__main__":
    print(gerar())
