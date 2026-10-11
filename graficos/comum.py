"""Base compartilhada pelos gráficos da galeria: estilo, cores, leitura dos dados e salvamento.

Cada gráfico é um script em graficos/ com:
- META: número, grupo, nome do gráfico, a pergunta que ele responde e quando usar esse tipo;
- gerar(): monta o gráfico, salva em figuras/ e devolve a leitura com os números calculados.
`scripts/gerar_galeria.py` executa todos e monta o README a partir disso.
"""
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
FIGURAS = RAIZ / "figuras"

# Paleta validada para contraste e para os três tipos de daltonismo
COR = {"principal": "#00806B", "destaque": "#C9721F", "contexto": "#B9C3BF",
       "texto": "#16211F", "texto2": "#56635F", "grade": "#E6EBE8", "fundo": "#FFFFFF"}
# Categóricas (até 6 grupos), na ordem em que devem ser usadas
CATEGORICAS = ["#00806B", "#C9721F", "#2F6DB5", "#D0587E", "#7F8F1F", "#7A5AB8"]
SEQ = LinearSegmentedColormap.from_list("seq", ["#E3F1EC", "#7CC0AE", "#00806B", "#0A3F36"])
DIV = LinearSegmentedColormap.from_list("div", ["#C9721F", "#F7F4EE", "#00806B"])

FONTES = {
    "olist": "Fonte: Olist Brazilian E-Commerce Public Dataset (CC BY-NC-SA 4.0)",
    "airbnb": "Fonte: Inside Airbnb, Buenos Aires (CC BY 4.0)",
    "telco": "Fonte: IBM Telco Customer Churn (Apache 2.0)",
    "filmes": "Fonte: MovieTweetings, Dooms et al. (MIT)",
    "simulado": "Dados simulados",
}

REGIAO = {"SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste", "ES": "Sudeste",
          "PR": "Sul", "SC": "Sul", "RS": "Sul",
          "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
          "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
          "RN": "Nordeste", "AL": "Nordeste", "SE": "Nordeste", "PI": "Nordeste",
          "PA": "Norte", "AM": "Norte", "RO": "Norte", "TO": "Norte", "AC": "Norte", "AP": "Norte", "RR": "Norte"}

CATEGORIA_PT = {
    "cama_mesa_banho": "Cama, mesa e banho", "beleza_saude": "Beleza e saúde", "esporte_lazer": "Esporte e lazer",
    "moveis_decoracao": "Móveis e decoração", "informatica_acessorios": "Informática",
    "utilidades_domesticas": "Utilidades domésticas", "relogios_presentes": "Relógios e presentes",
    "telefonia": "Telefonia", "ferramentas_jardim": "Ferramentas e jardim", "automotivo": "Automotivo",
    "brinquedos": "Brinquedos", "cool_stuff": "Cool stuff", "perfumaria": "Perfumaria", "bebes": "Bebês",
    "eletronicos": "Eletrônicos", "papelaria": "Papelaria", "fashion_bolsas_e_acessorios": "Bolsas e acessórios",
    "pet_shop": "Pet shop", "moveis_escritorio": "Móveis de escritório", "consoles_games": "Games",
    "malas_acessorios": "Malas", "construcao_ferramentas_construcao": "Construção", "eletrodomesticos": "Eletrodomésticos",
    "instrumentos_musicais": "Instrumentos musicais", "eletroportateis": "Eletroportáteis",
    "casa_construcao": "Casa e construção", "livros_interesse_geral": "Livros", "alimentos": "Alimentos",
    "moveis_sala": "Móveis de sala", "casa_conforto": "Casa e conforto", "bebidas": "Bebidas",
    "audio": "Áudio", "climatizacao": "Climatização", "pcs": "PCs", "market_place": "Marketplace",
}

PAGAMENTO_PT = {"credit_card": "Cartão de crédito", "boleto": "Boleto", "voucher": "Vale-presente",
                "debit_card": "Cartão de débito", "not_defined": "Não definido"}


def aplicar_estilo():
    mpl.rcParams.update({
        "figure.facecolor": COR["fundo"], "axes.facecolor": COR["fundo"], "savefig.facecolor": COR["fundo"],
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.edgecolor": COR["grade"], "axes.labelcolor": COR["texto2"],
        "axes.titlesize": 13.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.titlecolor": COR["texto"], "axes.titlepad": 26,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.grid": True, "axes.axisbelow": True, "grid.color": COR["grade"], "grid.linewidth": 0.8,
        "xtick.color": COR["texto2"], "ytick.color": COR["texto2"],
        "xtick.major.size": 0, "ytick.major.size": 0,
        "legend.frameon": False, "savefig.dpi": 150, "savefig.bbox": "tight",
    })


aplicar_estilo()


def titulo(ax, titulo, subtitulo=None):
    """Título com a conclusão e subtítulo cinza com o que o gráfico mede."""
    ax.set_title(titulo)
    if subtitulo:
        ax.text(0, 1.02, subtitulo, transform=ax.transAxes, fontsize=10, color=COR["texto2"], va="bottom")


def titulo_figura(fig, titulo, subtitulo=None, y=1.02):
    """Título para figuras com vários painéis."""
    fig.text(0.01, y + 0.045, titulo, ha="left", va="bottom", fontsize=13.5, fontweight="bold", color=COR["texto"])
    if subtitulo:
        fig.text(0.01, y, subtitulo, fontsize=10, color=COR["texto2"], va="bottom")


def salvar(fig, arquivo_script, fonte, y_fonte=-0.03):
    """Rodapé com a fonte e salvamento em figuras/<nome do script>.png."""
    fig.text(0.01, y_fonte, fonte + " · elaboração: Cézar Bento", fontsize=8, color=COR["texto2"], ha="left", va="top")
    FIGURAS.mkdir(exist_ok=True)
    destino = FIGURAS / (Path(arquivo_script).stem + ".png")
    fig.savefig(destino)
    plt.close(fig)
    return destino


def br(v, casas=0):
    """Número no padrão brasileiro: 1.234,5."""
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v, casas=0):
    return br(v * 100, casas) + "%"


# ---------------------------------------------------------------- dados

@lru_cache(maxsize=None)
def olist():
    d = pd.read_csv(DADOS / "olist_pedidos.csv.gz",
                    parse_dates=["compra", "aprovacao", "postagem", "entrega", "prometido"])
    d["regiao"] = d.uf_cliente.map(REGIAO)
    d["regiao_vendedor"] = d.uf_vendedor.map(REGIAO)
    d["categoria_pt"] = d.categoria.map(CATEGORIA_PT).fillna(d.categoria)
    d["dias_entrega"] = (d.entrega - d.compra).dt.total_seconds() / 86400
    d["dias_prometidos"] = (d.prometido - d.compra.dt.normalize()).dt.days
    d["atraso"] = (d.entrega.dt.normalize() > d.prometido).where(d.entrega.notna())
    return d


@lru_cache(maxsize=None)
def olist_entregues():
    d = olist()
    return d[(d.status == "delivered") & d.entrega.notna()].copy()


@lru_cache(maxsize=None)
def avaliacoes():
    return pd.read_csv(DADOS / "olist_avaliacoes.csv.gz")


@lru_cache(maxsize=None)
def airbnb():
    d = pd.read_csv(DADOS / "airbnb_buenos_aires.csv.gz")
    d["tipo"] = d.tipo.map({"Entire home/apt": "Imóvel inteiro", "Private room": "Quarto privativo",
                            "Shared room": "Quarto compartilhado", "Hotel room": "Quarto de hotel"})
    # Preço em pesos argentinos; extremos (anúncios de teste, erros de digitação) ficam de fora
    d = d[d.preco.between(d.preco.quantile(0.01), d.preco.quantile(0.99))]
    return d


@lru_cache(maxsize=None)
def telco():
    d = pd.read_csv(DADOS / "telco_churn.csv.gz")
    d["TotalCharges"] = pd.to_numeric(d.TotalCharges, errors="coerce")
    d["saiu"] = (d.Churn == "Yes").astype(int)
    d["contrato"] = d.Contract.map({"Month-to-month": "Mensal", "One year": "1 ano", "Two year": "2 anos"})
    return d


@lru_cache(maxsize=None)
def filmes():
    return pd.read_csv(DADOS / "movietweetings_filmes_ano.csv.gz")


def faixa(ax, x0, y0, x1, y1, cor, alpha=0.45):
    """Fita curva entre dois intervalos verticais: (x0, y0=(baixo, cima)) → (x1, y1=(baixo, cima)).

    Base dos diagramas de Sankey e alluvial: as bordas são curvas de Bézier cúbicas, com tangente horizontal
    nas pontas, o que dá o formato de "S".
    """
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath
    meio = (x0 + x1) / 2
    vertices = [(x0, y0[1]), (meio, y0[1]), (meio, y1[1]), (x1, y1[1]),
                (x1, y1[0]), (meio, y1[0]), (meio, y0[0]), (x0, y0[0]), (x0, y0[1])]
    codigos = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
               MPath.LINETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(vertices, codigos), facecolor=cor, edgecolor="none", alpha=alpha))


# ---------------------------------------------------------------- texto

STOPWORDS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para pra com e que se ao aos ele ela eles elas eu
voce voces me te lhe meu minha seu sua isso isto esse essa este esta foi ser ter tem era sao estou esta estava ja
ainda mais muito tambem so pois como quando onde ate mas ou porem entao la aqui num numa pelo pela pelos pelas
""".split())


def palavras(texto):
    """Normaliza (minúsculas, sem acento, sem pontuação) e devolve as palavras sem stopwords. Mantém o 'não'."""
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", str(texto).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z\s]", " ", t)
    return [p for p in t.split() if p not in STOPWORDS and len(p) > 1]
