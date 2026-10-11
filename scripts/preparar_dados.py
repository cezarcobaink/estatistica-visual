"""Gera as bases enxutas em dados/ a partir das fontes públicas originais.

Uso:  python scripts/preparar_dados.py PASTA_OLIST LISTINGS_AIRBNB TELCO_CSV RATINGS_MOVIETWEETINGS MOVIES_MOVIETWEETINGS

Fontes:
- Olist: Brazilian E-Commerce Public Dataset (Kaggle, CC BY-NC-SA 4.0)
- Airbnb Buenos Aires: Inside Airbnb (CC BY 4.0), listings.csv
- Telco Customer Churn: IBM (Apache 2.0)
- MovieTweetings: Simon Dooms (MIT)
Colunas com dados pessoais (nomes de anfitriões, IDs longos) não são copiadas.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DADOS = Path(__file__).resolve().parents[1] / "dados"


def olist(pasta: Path) -> pd.DataFrame:
    datas = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
             "order_delivered_customer_date", "order_estimated_delivery_date"]
    pedidos = pd.read_csv(pasta / "olist_orders_dataset.csv", parse_dates=datas)
    clientes = pd.read_csv(pasta / "olist_customers_dataset.csv")
    itens = pd.read_csv(pasta / "olist_order_items_dataset.csv")
    produtos = pd.read_csv(pasta / "olist_products_dataset.csv")
    vendedores = pd.read_csv(pasta / "olist_sellers_dataset.csv")
    pagamentos = pd.read_csv(pasta / "olist_order_payments_dataset.csv")
    avaliacoes = pd.read_csv(pasta / "olist_order_reviews_dataset.csv")

    itens = itens.merge(produtos[["product_id", "product_category_name"]], on="product_id", how="left")
    itens = itens.merge(vendedores[["seller_id", "seller_state"]], on="seller_id", how="left")
    itens = itens.sort_values("price", ascending=False)
    por_pedido = itens.groupby("order_id").agg(
        itens=("order_item_id", "size"), valor_itens=("price", "sum"), frete=("freight_value", "sum"),
        categoria=("product_category_name", "first"), uf_vendedor=("seller_state", "first"),
        vendedor=("seller_id", "first"))
    pag = pagamentos.sort_values("payment_value", ascending=False).groupby("order_id").agg(
        pagamento=("payment_type", "first"), parcelas=("payment_installments", "max"), valor_pago=("payment_value", "sum"))
    nota = avaliacoes.groupby("order_id").review_score.mean()

    p = pedidos.merge(clientes[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id")
    p = p.set_index("order_id").join(por_pedido).join(pag)
    p["nota"] = nota
    t = pd.DataFrame({
        "cliente": pd.factorize(p.customer_unique_id)[0],
        "vendedor": pd.factorize(p.vendedor)[0],
        "status": p.order_status,
        "compra": p.order_purchase_timestamp,
        "aprovacao": p.order_approved_at,
        "postagem": p.order_delivered_carrier_date,
        "entrega": p.order_delivered_customer_date,
        "prometido": p.order_estimated_delivery_date,
        "uf_cliente": p.customer_state, "uf_vendedor": p.uf_vendedor,
        "categoria": p.categoria, "itens": p.itens, "valor_itens": p.valor_itens, "frete": p.frete,
        "pagamento": p.pagamento, "parcelas": p.parcelas, "valor_pago": p.valor_pago, "nota": p.nota,
    })
    return t.reset_index(drop=True).sort_values("compra")


def airbnb(arquivo: Path) -> pd.DataFrame:
    d = pd.read_csv(arquivo)
    colunas = ["neighbourhood", "latitude", "longitude", "room_type", "price", "minimum_nights",
               "number_of_reviews", "reviews_per_month", "calculated_host_listings_count", "availability_365"]
    return d[colunas].rename(columns={"neighbourhood": "bairro", "room_type": "tipo", "price": "preco",
                                      "minimum_nights": "noites_minimas", "number_of_reviews": "avaliacoes",
                                      "reviews_per_month": "avaliacoes_mes",
                                      "calculated_host_listings_count": "anuncios_do_anfitriao",
                                      "availability_365": "disponibilidade"})


def filmes(ratings: Path, movies: Path) -> pd.DataFrame:
    """Avaliações por filme e ano, com gêneros (sem identificar usuários)."""
    r = pd.read_csv(ratings, sep="::", engine="python", names=["usuario", "filme", "nota", "ts"])
    m = pd.read_csv(movies, sep="::", engine="python", names=["filme", "titulo", "generos"]).drop_duplicates("filme")
    r["ano"] = pd.to_datetime(r.ts, unit="s").dt.year
    agg = r.groupby(["filme", "ano"]).agg(avaliacoes=("nota", "size"), nota_media=("nota", "mean")).reset_index()
    return agg.merge(m, on="filme", how="left")


if __name__ == "__main__":
    pasta_olist, listings, telco, ratings, movies = map(Path, sys.argv[1:6])
    DADOS.mkdir(exist_ok=True)
    olist(pasta_olist).to_csv(DADOS / "olist_pedidos.csv.gz", index=False, float_format="%.2f")
    airbnb(listings).to_csv(DADOS / "airbnb_buenos_aires.csv.gz", index=False)
    pd.read_csv(telco).drop(columns="customerID").to_csv(DADOS / "telco_churn.csv.gz", index=False)
    filmes(ratings, movies).to_csv(DADOS / "movietweetings_filmes_ano.csv.gz", index=False, float_format="%.3f")
    print("ok")
