"""Diagnóstico de resíduos em 4 painéis: o modelo linear é adequado?"""
from scipy import stats

from comum import COR, airbnb, br, np, pd, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Incerteza", nome="Diagnóstico de resíduos",
            pergunta="Uma regressão linear para o preço do Airbnb cumpre as suposições que dão validade aos intervalos de confiança?",
            quando="Sempre depois de ajustar uma regressão: os resíduos mostram não linearidade, variância desigual e caudas pesadas.")


def gerar():
    d = airbnb().dropna(subset=["avaliacoes_mes"]).copy()
    top = d.bairro.value_counts().index[:12]
    d["bairro"] = d.bairro.where(d.bairro.isin(top), "Outros")
    X = pd.get_dummies(d[["tipo", "bairro"]], drop_first=True, dtype=float)
    X["log_noites"] = np.log1p(d.noites_minimas)
    X["log_avaliacoes"] = np.log1p(d.avaliacoes)
    X["disponibilidade"] = d.disponibilidade / 365
    X.insert(0, "constante", 1.0)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), gridspec_kw={"hspace": 0.4, "wspace": 0.25})
    resultados = {}
    for nome, y in [("preço", d.preco.to_numpy(float)), ("log do preço", np.log(d.preco.to_numpy(float)))]:
        beta, *_ = np.linalg.lstsq(X.values, y, rcond=None)
        ajuste = X.values @ beta
        res = y - ajuste
        resultados[nome] = (ajuste, res, 1 - res.var() / y.var())
    ajuste, res, r2 = resultados["log do preço"]
    rng = np.random.default_rng(0)
    amostra = rng.choice(len(res), 4000, replace=False)
    padron = res / res.std()
    # 1) resíduo × ajustado: procura curvatura
    ax = axes[0, 0]
    ax.scatter(ajuste[amostra], res[amostra], s=4, alpha=0.35, color=COR["principal"], lw=0)
    ordem = np.argsort(ajuste)
    janela = pd.Series(res[ordem]).rolling(800, center=True).median()
    ax.plot(ajuste[ordem], janela, color=COR["destaque"], lw=2); ax.axhline(0, color=COR["texto"], lw=0.8)
    ax.set_title("Resíduo × valor ajustado", fontsize=11, pad=6); ax.set_xlabel("log do preço ajustado"); ax.set_ylabel("resíduo")
    # 2) Q-Q dos resíduos padronizados
    ax = axes[0, 1]
    (teo, obs), _ = stats.probplot(padron[amostra])
    ax.scatter(teo, obs, s=4, color=COR["principal"], alpha=0.5, lw=0); ax.plot([-4, 4], [-4, 4], color=COR["destaque"], lw=1.5)
    ax.set_title("Q-Q dos resíduos", fontsize=11, pad=6); ax.set_xlabel("quantis da normal"); ax.set_ylabel("resíduo padronizado")
    # 3) escala-localização: procura variância que muda com o ajuste
    ax = axes[1, 0]
    raiz = np.sqrt(np.abs(padron))
    ax.scatter(ajuste[amostra], raiz[amostra], s=4, alpha=0.35, color=COR["principal"], lw=0)
    ax.plot(ajuste[ordem], pd.Series(raiz[ordem]).rolling(800, center=True).mean(), color=COR["destaque"], lw=2)
    ax.set_title("Escala-localização", fontsize=11, pad=6); ax.set_xlabel("log do preço ajustado"); ax.set_ylabel("√|resíduo padronizado|")
    # 4) comparação: resíduos do modelo em preço bruto × em log
    ax = axes[1, 1]
    for nome, cor in [("preço", COR["contexto"]), ("log do preço", COR["principal"])]:
        r = resultados[nome][1]
        ax.hist(r / r.std(), bins=80, range=(-5, 5), density=True, histtype="stepfilled" if nome == "preço" else "step",
                color=cor, lw=2, label=f"modelo em {nome} (assimetria {br(stats.skew(r), 1)})")
    ax.set_title("Resíduos: preço bruto × log", fontsize=11, pad=6); ax.legend(fontsize=8.5); ax.set_xlabel("resíduo padronizado")
    caudas = (np.abs(padron) > 3).mean()
    titulo_figura(fig, f"Em log, o modelo de preço quase cumpre as suposições; as caudas são o ponto fraco",
                  f"Regressão linear do log da diária (tipo, bairro, noites mínimas, avaliações, disponibilidade) · R² = {br(r2, 2)}", y=0.95)
    salvar(fig, __file__, FONTES["airbnb"])
    return (f"Os quatro painéis checam as suposições da regressão. O resíduo × ajustado não mostra curvatura forte; a escala-localização "
            f"mostra variância parecida ao longo dos preços; o Q-Q revela caudas mais pesadas que a normal ({br(caudas * 100, 1)}% dos "
            f"resíduos passam de 3 desvios, contra 0,3% esperado). O último painel justifica o log: no preço bruto, os resíduos têm "
            f"assimetria {br(stats.skew(resultados['preço'][1]), 1)}; em log, {br(stats.skew(res), 1)}. Com caudas pesadas, os "
            "intervalos de confiança devem vir de erros-padrão robustos ou bootstrap.")


if __name__ == "__main__":
    print(gerar())
