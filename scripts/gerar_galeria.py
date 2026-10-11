"""Executa todos os gráficos de graficos/ e monta o README da galeria.

    python scripts/gerar_galeria.py            # todos
    python scripts/gerar_galeria.py 19 35      # só alguns (o README é refeito com as leituras guardadas)

Cada script devolve a leitura com os números calculados na hora; o README nunca tem número digitado à mão.
"""
import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GRAFICOS = RAIZ / "graficos"
CACHE = RAIZ / "figuras" / "leituras.json"
sys.path.insert(0, str(GRAFICOS))

ORDEM_GRUPOS = ["Distribuição", "Comparação", "Composição", "Fluxo", "Relação", "Tempo", "Texto", "Incerteza", "Errado × certo"]
INTRO_GRUPO = {
    "Distribuição": "Como os valores se espalham: forma, caudas e diferenças entre grupos.",
    "Comparação": "Quem é maior, quem mudou, quem subiu no ranking.",
    "Composição": "Como um total se divide em partes.",
    "Fluxo": "De onde vem e para onde vai: caminhos, etapas e trocas.",
    "Relação": "Como duas ou mais variáveis andam juntas.",
    "Tempo": "Tendência, sazonalidade, choques e previsão.",
    "Texto": "O que as pessoas escrevem, em números.",
    "Incerteza": "Quanto confiar no número: intervalos, testes e diagnóstico de modelos.",
    "Errado × certo": "O mesmo dado em um gráfico que engana e em um que informa.",
}


def carregar(arquivo):
    spec = importlib.util.spec_from_file_location(arquivo.stem.replace("-", "_"), arquivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(filtro):
    leituras = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    itens = []
    for arq in sorted(GRAFICOS.glob("[0-9][0-9]_*.py")):
        mod = carregar(arq)
        numero = arq.stem[:2]
        if not filtro or numero in filtro:
            print(f"gerando {arq.stem}...", flush=True)
            leituras[arq.stem] = mod.gerar()
        itens.append((arq, mod.META, leituras.get(arq.stem, "")))
    CACHE.write_text(json.dumps(leituras, ensure_ascii=False, indent=1), encoding="utf-8")
    escrever_readme(itens)


def ancora(texto):
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 -]", "", t).strip().replace(" ", "-")


def escrever_readme(itens):
    linhas = [
        "# Estatística visual: 45 gráficos com dados reais, cada um com a sua leitura",
        "",
        "Uma galeria de gráficos estatísticos em Python. Cada um responde a uma pergunta concreta com dados públicos reais "
        "(e-commerce da Olist, Airbnb em Buenos Aires, churn de telecom, avaliações de filmes) e vem com **a leitura do "
        "resultado** e **quando usar** aquele tipo de gráfico.",
        "",
        "**Destaques:**",
        "- Sankey, diagrama de cordas, alluvial, treemap (squarify), nuvem de palavras e horizon chart **implementados do zero** "
        "em matplotlib, sem bibliotecas prontas para eles;",
        "- todos os números das leituras são calculados pelo próprio script na hora de gerar o gráfico; nenhum foi digitado à mão;",
        "- uma seção **Errado × certo**, com o mesmo dado mostrado de forma enganosa e de forma honesta;",
        "- um padrão visual único: paleta validada para daltonismo, título com a conclusão, subtítulo com o que foi medido e fonte no rodapé.",
        "",
        "## Índice",
        "",
        "| # | Gráfico | Pergunta |",
        "|---|---|---|",
    ]
    por_grupo = {}
    for arq, meta, leitura in itens:
        por_grupo.setdefault(meta["grupo"], []).append((arq, meta, leitura))
    for grupo in ORDEM_GRUPOS:
        for arq, meta, _ in por_grupo.get(grupo, []):
            n = arq.stem[:2]
            linhas.append(f"| {n} | [{meta['nome']}](#{ancora(n + '-' + meta['nome'])}) | {meta['pergunta']} |")
    for grupo in ORDEM_GRUPOS:
        linhas += ["", f"## {grupo}", "", f"*{INTRO_GRUPO[grupo]}*", ""]
        for arq, meta, leitura in por_grupo.get(grupo, []):
            n = arq.stem[:2]
            linhas += [
                f"### {n} {meta['nome']}",
                "",
                f"**Pergunta:** {meta['pergunta']}",
                "",
                f"![{meta['nome']}](figuras/{arq.stem}.png)",
                "",
                f"**Leitura:** {leitura}",
                "",
                f"**Quando usar:** {meta['quando']}",
                "",
                f"[Código]({arq.relative_to(RAIZ).as_posix()})",
                "",
            ]
    linhas += [
        "## Como reproduzir",
        "",
        "```bash",
        "pip install -r requirements.txt",
        "python scripts/gerar_galeria.py        # gera os 45 gráficos e este README",
        "python graficos/19_sankey.py           # ou um gráfico só",
        "```",
        "",
        "Estrutura: `graficos/` (um script por gráfico + `comum.py` com estilo, dados e utilidades) · `dados/` (bases enxutas, "
        "geradas por `scripts/preparar_dados.py`) · `figuras/`.",
        "",
        "## Dados",
        "",
        "- **Olist:** [Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (CC BY-NC-SA 4.0)",
        "- **Airbnb Buenos Aires:** [Inside Airbnb](https://insideairbnb.com/get-the-data/) (CC BY 4.0), sem nomes de anfitriões",
        "- **Telco Customer Churn:** [IBM](https://github.com/IBM/telco-customer-churn-on-icp4d) (Apache 2.0)",
        "- **MovieTweetings:** [Dooms et al.](https://github.com/sidooms/MovieTweetings) (MIT), agregado por filme e ano",
        "",
        "---",
        "Cézar Bento · [portfólio](https://cezarcobaink.github.io/WebSite/) · [LinkedIn](https://www.linkedin.com/in/c%C3%A9zar-augusto-bento-a91528a8)",
        "",
    ]
    (RAIZ / "README.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"README com {len(itens)} gráficos")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
