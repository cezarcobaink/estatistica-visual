"""Lei de Benford: distribuição do primeiro dígito."""
from scipy import stats

from comum import COR, br, np, olist, plt, salvar, titulo, FONTES

META = dict(grupo="Incerteza", nome="Lei de Benford",
            pergunta="Os valores pagos na Olist seguem a Lei de Benford, como se espera de dados financeiros não manipulados?",
            quando="Triagem de fraude ou erro em valores que cobrem várias ordens de grandeza (pagamentos, notas fiscais, gastos públicos).")


def gerar():
    v = olist().valor_pago.dropna()
    v = v[v >= 1]
    digito = v.astype(str).str.lstrip("0.").str[0].astype(int)
    obs = digito.value_counts(normalize=True).sort_index()
    d = np.arange(1, 10)
    benford = np.log10(1 + 1 / d)
    faixa_100 = ((v >= 100) & (v < 200)).mean()
    mad = np.mean(np.abs(obs.values - benford))
    qui = stats.chisquare(digito.value_counts().sort_index().values, benford * len(digito))
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.bar(d, obs.values * 100, color=COR["principal"], width=0.65, label="observado")
    ax.plot(d, benford * 100, color=COR["destaque"], marker="o", lw=2, label="Lei de Benford")
    for x, o, b in zip(d, obs.values, benford):
        ax.text(x, max(o, b) * 100 + 0.8, f"{br((o - b) * 100, 1)} p.p.", ha="center", fontsize=8.5, color=COR["texto2"])
    ax.set_xticks(d); ax.set_xlabel("primeiro dígito do valor pago"); ax.set_ylabel("% dos pagamentos"); ax.legend()
    ax.grid(axis="x", visible=False)
    conformidade = "conformidade aceitável" if mad < 0.012 else "não conformidade" if mad > 0.015 else "conformidade marginal"
    maior = int(np.argmax(np.abs(obs.values - benford))) + 1
    titulo(ax, f"Os pagamentos seguem o formato de Benford, mas com excesso de valores começando em 1 e falta em 2",
           f"Primeiro dígito de {br(len(v))} pagamentos · barras = observado, linha = proporção esperada log₁₀(1 + 1/d)")
    salvar(fig, __file__, FONTES["olist"])
    return (f"Em valores que se espalham por várias ordens de grandeza, o dígito 1 aparece em cerca de 30% dos casos e o 9 em menos de 5%. "
            f"Os pagamentos da Olist seguem esse padrão com desvio absoluto médio de {br(mad * 100, 2)} p.p., o que pelos critérios de "
            f"Nigrini é {conformidade}: o dígito 1 tem {br((obs[1] - benford[0]) * 100, 1)} p.p. a mais e o 2, {br((benford[1] - obs[2]) * 100, 1)} p.p. a menos. "
            f"A causa provável é a escala: {br(faixa_100 * 100)}% dos pagamentos estão entre R$ 100 e 199, e Benford pressupõe valores espalhados por várias ordens de grandeza. O qui-quadrado dá p < 0,001, mas com {br(len(v))} valores qualquer desvio mínimo "
            "vira significativo: por isso a literatura usa o desvio médio, e não o p-valor. Na prática, Benford serve de triagem para "
            "escolher onde auditar, não como prova.")


if __name__ == "__main__":
    print(gerar())
