"""Waffle: 100 quadrados, cada um 1% do total."""
from comum import CATEGORICAS, COR, PAGAMENTO_PT, br, np, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Composição", nome="Waffle",
            pergunta="Como os clientes pagam os pedidos da Olist?",
            quando="Mostrar proporções de poucas partes para públicos não técnicos; mais legível que pizza porque cada quadrado é 1%.")


def gerar():
    d = olist()
    d = d[(d.status != "canceled") & d.pagamento.isin(["credit_card", "boleto", "voucher", "debit_card"])]
    part = d.pagamento.value_counts(normalize=True)
    # Arredondamento pelo maior resto: os quadrados somam exatamente 100
    bruto = part * 100
    quad = np.floor(bruto).astype(int)
    faltam = 100 - quad.sum()
    for k in (bruto - quad).sort_values(ascending=False).index[:faltam]:
        quad[k] += 1
    cores = dict(zip(part.index, CATEGORICAS))
    fig, ax = plt.subplots(figsize=(9, 5))
    i = 0
    for metodo, n in quad.items():
        for _ in range(n):
            col, lin = divmod(i, 10)
            ax.add_patch(plt.Rectangle((col, 9 - lin), 0.88, 0.88, color=cores[metodo]))
            i += 1
    for k, (metodo, n) in enumerate(quad.items()):
        ax.add_patch(plt.Rectangle((10.6, 8.6 - k * 1.3), 0.8, 0.8, color=cores[metodo]))
        ax.text(11.7, 9.0 - k * 1.3, f"{PAGAMENTO_PT[metodo]}: {br(part[metodo] * 100, 1)}%", va="center", fontsize=10.5,
                color=COR["texto"])
    ax.set_xlim(0, 17); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
    cartao = part["credit_card"]
    titulo(ax, f"Três de cada quatro pedidos são pagos no cartão de crédito",
           "Forma de pagamento principal de cada pedido · cada quadrado = 1% dos pedidos")
    salvar(fig, __file__, FONTES["olist"])
    parcelado = (d[d.pagamento == "credit_card"].parcelas > 1).mean()
    return (f"Cartão de crédito responde por {br(cartao * 100, 1)}% dos pedidos e boleto por {br(part['boleto'] * 100, 1)}%. "
            f"Entre os pagos no cartão, {br(parcelado * 100)}% são parcelados, um traço do varejo brasileiro que muda o "
            "fluxo de caixa dos vendedores. O waffle usa o arredondamento pelo maior resto para que os quadrados somem 100.")


if __name__ == "__main__":
    print(gerar())
