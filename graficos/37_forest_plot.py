"""Forest plot: efeitos estimados com intervalos de confiança."""
from comum import COR, br, np, plt, salvar, telco, titulo, FONTES

META = dict(grupo="Incerteza", nome="Forest plot",
            pergunta="Quais características aumentam ou reduzem a chance de cancelar, descontando as outras?",
            quando="Mostrar vários efeitos estimados (coeficientes, razões de chance, estudos de uma meta-análise) com a incerteza de cada um.")

VARIAVEIS = {"contrato_1": "Contrato de 1 ano (vs. mensal)", "contrato_2": "Contrato de 2 anos (vs. mensal)",
             "fibra": "Internet por fibra (vs. DSL)", "sem_internet": "Sem internet (vs. DSL)",
             "cheque": "Paga com cheque eletrônico", "fatura_digital": "Fatura digital", "idoso": "Idoso",
             "seguranca": "Segurança online", "suporte": "Suporte técnico", "dependentes": "Tem dependentes",
             "tenure_ano": "Cada ano a mais como cliente"}


def logistica(X, y, iteracoes=50):
    """Regressão logística por Newton-Raphson; devolve coeficientes e erros-padrão (inversa da informação de Fisher)."""
    beta = np.zeros(X.shape[1])
    for _ in range(iteracoes):
        p = 1 / (1 + np.exp(-X @ beta))
        W = p * (1 - p)
        H = X.T @ (X * W[:, None])
        passo = np.linalg.solve(H, X.T @ (y - p))
        beta += passo
        if np.abs(passo).max() < 1e-10:
            break
    ep = np.sqrt(np.diag(np.linalg.inv(H)))
    return beta, ep


def gerar():
    d = telco()
    X = np.column_stack([
        np.ones(len(d)),
        d.contrato.eq("1 ano"), d.contrato.eq("2 anos"),
        d.InternetService.eq("Fiber optic"), d.InternetService.eq("No"),
        d.PaymentMethod.eq("Electronic check"), d.PaperlessBilling.eq("Yes"), d.SeniorCitizen.eq(1),
        d.OnlineSecurity.eq("Yes"), d.TechSupport.eq("Yes"), d.Dependents.eq("Yes"), d.tenure / 12,
    ]).astype(float)
    beta, ep = logistica(X, d.saiu.to_numpy(float))
    nomes = list(VARIAVEIS.values())
    rc, lo, hi = np.exp(beta[1:]), np.exp(beta[1:] - 1.96 * ep[1:]), np.exp(beta[1:] + 1.96 * ep[1:])
    ordem = np.argsort(rc)
    fig, ax = plt.subplots(figsize=(9.5, 6))
    y = np.arange(len(ordem))
    for yi, k in zip(y, ordem):
        cor = COR["destaque"] if lo[k] > 1 else COR["principal"] if hi[k] < 1 else COR["contexto"]
        ax.plot([lo[k], hi[k]], [yi, yi], color=cor, lw=2.2)
        ax.scatter(rc[k], yi, color=cor, s=60, marker="s", zorder=3)
        ax.text(hi[k] * 1.08, yi, f"{br(rc[k], 2)}", va="center", fontsize=9, color=COR["texto2"])
    ax.axvline(1, color=COR["texto"], lw=1)
    ax.set_xscale("log"); ax.xaxis.set_minor_locator(plt.NullLocator()); ax.set_xticks([0.1, 0.25, 0.5, 1, 2, 4], ["0,1", "0,25", "0,5", "1", "2", "4"])
    ax.set_yticks(y, [nomes[k] for k in ordem]); ax.grid(axis="y", visible=False)
    ax.set_xlabel("razão de chances de cancelar (escala log) · 1 = sem efeito")
    k2 = nomes.index("Contrato de 2 anos (vs. mensal)")
    titulo(ax, f"Com tudo o mais igual, contrato de 2 anos tem {br(rc[k2], 2)}× a chance de cancelar do mensal",
           "Regressão logística com 11 variáveis · quadrado = razão de chances, linha = IC de 95% · laranja aumenta, verde reduz o risco")
    salvar(fig, __file__, FONTES["telco"])
    kf = nomes.index("Internet por fibra (vs. DSL)")
    return (f"Cada linha é o efeito de uma característica mantendo as outras fixas, com o intervalo de 95%. Contrato de 2 anos "
            f"multiplica a chance de cancelar por {br(rc[k2], 2)} (IC {br(lo[k2], 2)}–{br(hi[k2], 2)}); fibra, por {br(rc[kf], 2)}. "
            "Intervalos que cruzam a linha do 1 (em cinza) são efeitos que os dados não distinguem de zero. A regressão foi implementada "
            "por Newton-Raphson, com os erros-padrão tirados da informação de Fisher. São associações, não efeitos causais: "
            "quem escolhe contrato longo já tende a ficar.")


if __name__ == "__main__":
    print(gerar())
