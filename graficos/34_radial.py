"""Heatmap radial: hora do dia × dia da semana num relógio."""
from comum import COR, SEQ, br, np, olist, plt, salvar, titulo_figura, FONTES

META = dict(grupo="Tempo", nome="Heatmap radial (relógio)",
            pergunta="Em que horas e dias da semana os clientes compram?",
            quando="Mostrar padrões cíclicos (horas, meses), em que o fim encosta no começo; a versão retangular é mais precisa para leitura exata.")

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def gerar():
    d = olist()
    d = d[d.status != "canceled"]
    t = d.groupby([d.compra.dt.dayofweek, d.compra.dt.hour]).size().unstack(fill_value=0)
    semanas = d.compra.dt.to_period("W").nunique()
    t = t / semanas  # pedidos médios por hora em cada dia da semana
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(projection="polar")
    theta = np.linspace(0, 2 * np.pi, 25)
    raio = np.arange(8) + 2  # anel interno = segunda, externo = domingo; o centro fica vazio
    T, R = np.meshgrid(theta, raio)
    pc = ax.pcolormesh(T, R, t.values, cmap=SEQ, shading="flat", edgecolors="white", lw=0.6)
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    ax.set_xticks(np.linspace(0, 2 * np.pi, 24, endpoint=False), [f"{h}h" for h in range(24)], fontsize=9)
    ax.set_yticks(raio[:-1] + 0.5, DIAS, fontsize=8.5, color=COR["texto2"]); ax.set_rlabel_position(0)
    ax.set_ylim(0, 9); ax.grid(False); ax.spines["polar"].set_visible(False)
    fig.colorbar(pc, ax=ax, shrink=0.6, pad=0.08, label="pedidos por hora (média semanal)")
    pico = t.stack().idxmax()
    madrugada = t.loc[:, 2:5].values.mean() / t.values.mean()
    titulo_figura(fig, f"O pico é {DIAS[pico[0]]} às {pico[1]}h; de madrugada, as vendas caem a {br(madrugada * 100)}% da média",
           "Pedidos médios por hora e dia da semana · anéis de dentro para fora: segunda a domingo", y=0.9)
    salvar(fig, __file__, FONTES["olist"])
    noite_dom = t.loc[6, 19:22].mean() / t.loc[5, 19:22].mean()
    return (f"O relógio torna natural a continuidade entre 23h e 0h, que num heatmap retangular ficaria nas bordas opostas. O pico "
            f"médio é {DIAS[pico[0]]} às {pico[1]}h; entre 2h e 5h as vendas caem a {br(madrugada * 100)}% da média. Os fins de semana "
            f"ficam mais claros durante o dia, mas a noite de domingo recupera ({br(noite_dom, 1)}× a de sábado no mesmo horário), "
            "um bom horário para campanhas. Ler valores exatos em anéis é difícil: para isso, a versão retangular é melhor.")


if __name__ == "__main__":
    print(gerar())
