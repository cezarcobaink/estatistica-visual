"""Matriz de correlação reordenada por agrupamento hierárquico, com dendrograma."""
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

from comum import COR, DIV, br, np, plt, salvar, telco, titulo_figura, FONTES

META = dict(grupo="Relação", nome="Matriz de correlação agrupada",
            pergunta="Quais características dos clientes andam juntas, e quais andam com o cancelamento?",
            quando="Explorar muitas variáveis de uma vez; reordenar por agrupamento faz os blocos de variáveis parecidas aparecerem.")

ROTULOS = {"tenure": "Meses como cliente", "MonthlyCharges": "Mensalidade", "TotalCharges": "Total pago",
           "SeniorCitizen": "Idoso", "Partner": "Tem cônjuge", "Dependents": "Tem dependentes",
           "PaperlessBilling": "Fatura digital", "OnlineSecurity": "Segurança online", "TechSupport": "Suporte técnico",
           "StreamingTV": "Streaming de TV", "StreamingMovies": "Streaming de filmes", "OnlineBackup": "Backup",
           "fibra": "Internet por fibra", "mensal": "Contrato mensal", "boleto_eletronico": "Paga com cheque eletrônico",
           "saiu": "Cancelou"}


def gerar():
    d = telco()
    X = d[["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen", "saiu"]].copy()
    for c in ["Partner", "Dependents", "PaperlessBilling", "OnlineSecurity", "TechSupport", "StreamingTV",
              "StreamingMovies", "OnlineBackup"]:
        X[c] = (d[c] == "Yes").astype(int)
    X["fibra"] = (d.InternetService == "Fiber optic").astype(int)
    X["mensal"] = (d.contrato == "Mensal").astype(int)
    X["boleto_eletronico"] = (d.PaymentMethod == "Electronic check").astype(int)
    # Spearman: robusta a assimetrias e funciona com variáveis binárias e ordinais
    C = X.dropna().corr(method="spearman")
    distancia = squareform(1 - C.abs().values, checks=False)
    ligacao = linkage(distancia, method="average")
    ordem = leaves_list(ligacao)
    C = C.iloc[ordem, ordem]
    nomes = [ROTULOS[c] for c in C.columns]
    fig, ax = plt.subplots(figsize=(10.5, 9))
    im = ax.imshow(C.values, cmap=DIV, vmin=-1, vmax=1)
    for i in range(len(C)):
        for j in range(len(C)):
            v = C.values[i, j]
            if i != j and abs(v) >= 0.2:
                ax.text(j, i, br(v, 1), ha="center", va="center", fontsize=7.5, color="white" if abs(v) > 0.55 else COR["texto"])
    ax.set_xticks(range(len(C)), nomes, rotation=55, ha="right", fontsize=9)
    ax.set_yticks(range(len(C)), nomes, fontsize=9); ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.6, pad=0.03, label="correlação de Spearman")
    churn = C["saiu"].drop("saiu").sort_values()
    titulo_figura(fig, "O cancelamento anda junto com contrato mensal e fibra, e longe do tempo de casa",
                  "Correlação de Spearman entre 16 características dos clientes · ordem definida por agrupamento hierárquico",
                  y=0.92)
    salvar(fig, __file__, FONTES["telco"], y_fonte=-0.06)
    return (f"O agrupamento junta variáveis que contam a mesma história: tempo de casa, total pago e contratos longos formam um bloco; "
            f"fibra, mensalidade alta e streaming formam outro. O cancelamento se liga a {ROTULOS[churn.index[-1]].lower()} "
            f"({br(churn.iloc[-1], 2)}) e se opõe a {ROTULOS[churn.index[0]].lower()} ({br(churn.iloc[0], 2)}). "
            "Sem reordenar, a mesma matriz pareceria um tabuleiro aleatório. Só os valores com módulo de pelo menos 0,2 aparecem escritos, "
            "para não poluir.")


if __name__ == "__main__":
    print(gerar())
