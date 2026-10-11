"""Gráfico Q-Q: os dados seguem uma distribuição teórica?"""
from scipy import stats

from comum import COR, br, np, olist_entregues, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Distribuição", nome="Gráfico Q-Q",
            pergunta="O valor dos pedidos segue uma distribuição normal? E o logaritmo do valor?",
            quando="Checar uma suposição de modelo (normalidade de resíduos, log-normalidade) olhando as caudas, onde os testes formais são pouco informativos.")


def gerar():
    v = olist_entregues().valor_pago.dropna()
    v = v[v > 0].sample(4000, random_state=0).to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw={"wspace": 0.3})
    resumo = {}
    for ax, dados, rotulo, nome in [(axes[0], v, "valor (R$)", "Valor em R$"), (axes[1], np.log(v), "log do valor", "Log do valor")]:
        (teorico, ordenado), (incl, inter, r) = stats.probplot(dados, dist="norm")
        ax.scatter(teorico, ordenado, s=6, color=COR["principal"], alpha=0.5, lw=0)
        ax.plot(teorico, inter + incl * teorico, color=COR["destaque"], lw=1.6)
        ax.set_xlabel("quantis de uma normal padrão"); ax.set_ylabel(f"quantis observados ({rotulo})")
        ax.set_title(f"{nome}: correlação com a reta {br(r, 3)}", fontsize=11, pad=8)
        resumo[rotulo] = (r, stats.skew(dados))
    titulo_figura(fig, "O valor dos pedidos é aproximadamente log-normal, não normal",
                  "Gráfico Q-Q contra a normal · 4 mil pedidos sorteados · reta laranja = normal ajustada")
    salvar(fig, __file__, FONTES["olist"])
    return (f"No valor bruto, os pontos se curvam para cima à direita: a cauda é muito mais longa que a de uma normal "
            f"(assimetria {br(resumo['valor (R$)'][1], 1)}). Depois do log, os pontos seguem a reta no miolo "
            f"(assimetria {br(resumo['log do valor'][1], 2)}), com desvios só nos extremos. Consequência prática: médias e "
            "intervalos de confiança do valor devem ser calculados em log, ou com mediana e bootstrap.")


if __name__ == "__main__":
    print(gerar())
