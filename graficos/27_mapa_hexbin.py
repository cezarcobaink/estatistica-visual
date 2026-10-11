"""Mapa sem shapefile: hexágonos sobre latitude e longitude."""
from comum import COR, SEQ, airbnb, br, np, plt, salvar, titulo, FONTES

META = dict(grupo="Relação", nome="Mapa de hexágonos",
            pergunta="Onde ficam os anúncios mais caros do Airbnb em Buenos Aires?",
            quando="Mapear uma métrica por localização com muitos pontos; hexágonos evitam que o mapa vire só um retrato da densidade.")


def gerar():
    d = airbnb()
    d = d[d.tipo == "Imóvel inteiro"]
    fig, ax = plt.subplots(figsize=(9, 8))
    # Fundo: todos os anúncios em cinza, para dar o contorno da cidade
    ax.scatter(d.longitude, d.latitude, s=1, color=COR["grade"], zorder=1)
    hb = ax.hexbin(d.longitude, d.latitude, C=d.preco / 1000, reduce_C_function=np.median, gridsize=38, cmap=SEQ,
                   mincnt=15, zorder=2, linewidths=0.3, edgecolors="white")
    cb = fig.colorbar(hb, ax=ax, shrink=0.7); cb.set_label("diária mediana (mil pesos)")
    lat0 = d.latitude.mean()
    ax.set_aspect(1 / np.cos(np.deg2rad(lat0)))  # corrige a distorção da longitude nessa latitude
    ax.axis("off")
    valores = hb.get_array()
    centros = hb.get_offsets()
    caro = centros[np.argmax(valores)]
    perto = d[(abs(d.longitude - caro[0]) < 0.01) & (abs(d.latitude - caro[1]) < 0.01)].bairro.mode().iloc[0]
    titulo(ax, f"As diárias mais altas ficam na orla leste, em {perto}",
           "Imóveis inteiros · cada hexágono mostra a diária mediana (só hexágonos com 15 anúncios ou mais)")
    salvar(fig, __file__, FONTES["airbnb"])
    return (f"O mapa usa só latitude e longitude, sem arquivo de fronteiras: os pontos cinza desenham a cidade e os hexágonos "
            f"mostram a diária mediana. Os hexágonos mais caros estão em {perto}, na orla leste, com mediana de até "
            f"ARS {br(valores.max() * 1000)}; o resto da área central fica numa faixa bem mais estreita. Os pontos cinza fora dos hexágonos "
            "são regiões com menos de 15 anúncios, onde a mediana seria instável. O aspecto do gráfico corrige "
            "a distorção da longitude, que encolhe longe do equador.")


if __name__ == "__main__":
    print(gerar())
