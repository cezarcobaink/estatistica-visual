"""Coordenadas paralelas: cada cliente é uma linha que atravessa vários eixos."""
from comum import COR, br, np, plt, salvar, telco, titulo, FONTES

META = dict(grupo="Relação", nome="Coordenadas paralelas",
            pergunta="Qual é o perfil, em várias medidas ao mesmo tempo, dos clientes que cancelam?",
            quando="Comparar perfis multivariados de grupos (4 a 8 variáveis); funciona melhor com amostras e transparência.")


def gerar():
    d = telco().dropna(subset=["TotalCharges"]).copy()
    servicos = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    d["servicos"] = (d[servicos] == "Yes").sum(axis=1)
    d["contrato_meses"] = d.contrato.map({"Mensal": 1, "1 ano": 12, "2 anos": 24})
    eixos = [("tenure", "Meses como cliente"), ("contrato_meses", "Contrato (meses)"), ("servicos", "Serviços extras"),
             ("MonthlyCharges", "Mensalidade"), ("TotalCharges", "Total pago")]
    norm = d[[c for c, _ in eixos]].apply(lambda s: (s - s.min()) / (s.max() - s.min()))
    rng = np.random.default_rng(3)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    x = np.arange(len(eixos))
    for saiu, cor, alpha in [(0, COR["texto2"], 0.10), (1, COR["destaque"], 0.10)]:
        idx = rng.choice(np.where(d.saiu == saiu)[0], 350, replace=False)
        for i in idx:
            ax.plot(x, norm.iloc[i].values + rng.normal(0, 0.008, len(x)), color=cor, alpha=alpha, lw=0.8)
        mediana = norm[d.saiu == saiu].median().values
        ax.plot(x, mediana, color=COR["destaque"] if saiu else COR["texto2"], lw=3.2, label="cancelou (mediana)" if saiu else "ficou (mediana)")
    for xi, (c, nome) in zip(x, eixos):
        ax.axvline(xi, color=COR["texto2"], lw=0.8)
        ax.text(xi, 1.04, nome, ha="center", fontsize=9.5, color=COR["texto"])
        ax.text(xi, -0.06, br(d[c].min()), ha="center", fontsize=8, color=COR["texto2"])
        ax.text(xi, 1.0, br(d[c].max()), ha="center", va="bottom", fontsize=8, color=COR["texto2"])
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_ylim(-0.1, 1.12)
    ax.legend(loc="upper right", bbox_to_anchor=(1, -0.04), ncol=2)
    titulo(ax, "Quem cancela: pouco tempo de casa, contrato mensal, poucos extras e mensalidade alta",
           "350 clientes sorteados de cada grupo · cada linha é um cliente, eixos normalizados entre o mínimo e o máximo")
    salvar(fig, __file__, FONTES["telco"], y_fonte=-0.1)
    m = d.groupby("saiu")[["tenure", "servicos", "MonthlyCharges"]].median()
    return (f"As linhas laranjas descem no tempo de casa (mediana de {br(m.loc[1, 'tenure'])} meses contra {br(m.loc[0, 'tenure'])} de "
            f"quem ficou), ficam no piso do contrato e sobem na mensalidade (US$ {br(m.loc[1, 'MonthlyCharges'])} contra "
            f"US$ {br(m.loc[0, 'MonthlyCharges'])}). O gráfico mostra o perfil inteiro de uma vez; a ordem dos eixos importa, porque "
            "só se leem bem as relações entre eixos vizinhos.")


if __name__ == "__main__":
    print(gerar())
