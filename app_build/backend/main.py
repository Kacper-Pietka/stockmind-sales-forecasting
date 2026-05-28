"""
FastAPI backend dla systemu predykcji sprzedaży e-commerce.

Endpointy:
  GET  /                       - health check
  GET  /categories             - lista wszystkich kategorii z prognozami
  GET  /categories/{name}      - szczegóły jednej kategorii
  GET  /categories/{name}/products - produkty w kategorii z prawdziwej bazy
  POST /recommend              - upload CSV z magazynem -> rekomendacje
  GET  /trends                 - wszystkie trendy
  GET  /metrics                - metryki modelu (RMSE, MAE itd.)
"""
import io
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── Konfiguracja ───
ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"

app = FastAPI(
    title="Sales Forecast API",
    description="Predykcja sprzedaży + rekomendacje magazynowe (Olist e-commerce)",
    version="1.0.0"
)

# CORS - żeby frontend Streamlit mógł się dobić
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Wczytanie artefaktów przy starcie ───
inventory_df: Optional[pd.DataFrame] = None
forecast_df: Optional[pd.DataFrame] = None
trends_df: Optional[pd.DataFrame] = None
product_lookup: Optional[pd.DataFrame] = None
metrics: Optional[dict] = None


@app.on_event("startup")
def load_artifacts():
    """Wczytuje wszystkie artefakty z folderu /artifacts przy starcie aplikacji."""
    global inventory_df, forecast_df, trends_df, product_lookup, metrics

    try:
        inventory_df = pd.read_csv(ARTIFACTS_DIR / "inventory_recommendations.csv")
        forecast_df = pd.read_csv(ARTIFACTS_DIR / "forecast_4_weeks.csv")
        trends_df = pd.read_csv(ARTIFACTS_DIR / "trends_summary.csv")
        product_lookup = pd.read_csv(ARTIFACTS_DIR / "product_lookup.csv")

        # Konwersja dat
        forecast_df["week_start"] = pd.to_datetime(forecast_df["week_start"])

        # Metryki modelu (opcjonalnie)
        metrics_path = ARTIFACTS_DIR / "model_metrics.csv"
        if metrics_path.exists():
            m = pd.read_csv(metrics_path)
            metrics = m.set_index("metric")["value"].to_dict()
        else:
            metrics = {}

        print("OK: Artefakty wczytane:")
        print(f"  - inventory_df: {len(inventory_df)} kategorii")
        print(f"  - forecast_df:  {len(forecast_df)} prognoz")
        print(f"  - trends_df:    {len(trends_df)} trendów")
        print(f"  - product_lookup:  {len(product_lookup)} produktów")

    except FileNotFoundError as e:
        print(f"BLAD: brak artefaktów! {e}")
        print(f"  Sprawdź czy {ARTIFACTS_DIR} zawiera pliki CSV z notebooka.")


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTY
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    """Health check + info o systemie."""
    return {
        "status": "ok",
        "service": "Sales Forecast API",
        "artifacts_loaded": inventory_df is not None,
        "categories_count": len(inventory_df) if inventory_df is not None else 0,
    }


@app.get("/metrics")
def get_metrics():
    """Metryki modelu (RMSE, MAE, MAPE itp.)"""
    if metrics is None:
        return {}
    return metrics


@app.get("/categories")
def list_categories():
    """Lista wszystkich kategorii z prognozami + safety stock."""
    if inventory_df is None:
        raise HTTPException(503, "Artefakty nie wczytane")
    return inventory_df.to_dict(orient="records")


@app.get("/categories/{name}")
def category_detail(name: str):
    """Szczegóły jednej kategorii: prognoza + safety stock + trend."""
    if inventory_df is None:
        raise HTTPException(503, "Artefakty nie wczytane")

    row = inventory_df[inventory_df["category"] == name]
    if row.empty:
        raise HTTPException(404, f"Kategoria '{name}' nie znaleziona")

    # Forecast szczegółowy per tydzień
    cat_forecast = forecast_df[forecast_df["category"] == name].copy()
    cat_forecast["week_start"] = cat_forecast["week_start"].astype(str)

    # Trend
    trend = trends_df[trends_df["category"] == name]

    return {
        "summary": row.iloc[0].to_dict(),
        "weekly_forecast": cat_forecast.to_dict(orient="records"),
        "trend": trend.iloc[0].to_dict() if not trend.empty else None,
    }


@app.get("/categories/{name}/products")
def category_products(name: str, limit: int = 50):
    """Lista produktów (product_id, product_name) w danej kategorii."""
    if product_lookup is None:
        raise HTTPException(503, "Artefakty nie wczytane")

    products = product_lookup[
        product_lookup["category_pl"] == name
    ]

    if products.empty:
        raise HTTPException(404, f"Brak produktów w kategorii '{name}'")

    # Pobieramy zarówno product_id jak i product_name_pl
    subset = products.head(limit)[["product_id", "product_name_pl"]].rename(
        columns={"product_name_pl": "product_name"}
    )

    return {
        "category": name,
        "total_products": len(products),
        "products_shown": min(limit, len(products)),
        "products": subset.to_dict(orient="records"),
    }


@app.get("/trends")
def get_trends():
    """Wszystkie trendy."""
    if trends_df is None:
        raise HTTPException(503, "Artefakty nie wczytane")
    return trends_df.to_dict(orient="records")


@app.post("/recommend")
async def recommend_inventory(file: UploadFile = File(...)):
    """
    Upload CSV z aktualnym magazynem klienta.

    Format CSV: product_id, current_stock

    Zwraca: rekomendacje per produkt (forecast, safety_stock, action, ile zamówić).
    """
    if inventory_df is None:
        raise HTTPException(503, "Artefakty nie wczytane")

    # ── Walidacja pliku ──
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Wgraj plik .csv")

    content = await file.read()
    try:
        client_input = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Nie można sparsować CSV: {e}")

    required_cols = {"product_id", "current_stock"}
    missing = required_cols - set(client_input.columns)
    if missing:
        raise HTTPException(400, f"Brakujące kolumny: {missing}")

    # ── Mapowanie product_id -> kategoria ──
    client_data = client_input.merge(product_lookup[["product_id", "category_pl", "product_name_pl"]], on="product_id", how="left")
    client_data["category_pl"] = (
        client_data["category_pl"].fillna("unknown")
    )
    client_data["product_name_pl"] = (
        client_data["product_name_pl"].fillna(client_data["product_id"])
    )
    client_data["is_known_product"] = (
        client_data["category_pl"] != "unknown"
    )

    # ── Globalne średnie dla "unknown" ──
    global_stats = {
        "category": "unknown",
        "forecast_total_4w": inventory_df["forecast_total_4w"].mean(),
        "avg_weekly_demand": inventory_df["avg_weekly_demand"].mean(),
        "safety_stock": inventory_df["safety_stock"].mean(),
        "reorder_point": inventory_df["reorder_point"].mean(),
        "recommended_stock_4w": inventory_df["recommended_stock_4w"].mean(),
        "trend": "b/d (nieznany produkt)",
    }
    inventory_with_unknown = pd.concat(
        [inventory_df, pd.DataFrame([global_stats])], ignore_index=True
    )

    # ── Merge z prognozami ──
    recommendations = client_data.merge(
        inventory_with_unknown[
            [
                "category",
                "forecast_total_4w",
                "avg_weekly_demand",
                "safety_stock",
                "reorder_point",
                "recommended_stock_4w",
                "trend",
            ]
        ],
        left_on="category_pl",
        right_on="category",
        how="left",
    )

    # ── Decyzja biznesowa ──
    def decide(row):
        if pd.isna(row["recommended_stock_4w"]):
            return "BRAK_DANYCH", "low"
        c, n, f = row["current_stock"], row["recommended_stock_4w"], row["forecast_total_4w"]
        if c < row["reorder_point"]:
            return "ZAMÓW PILNIE", "high"
        if c < f:
            return "ZAMÓW", "medium"
        if c < n:
            return "OBSERWUJ", "low"
        if c > n * 2:
            return "NADWYŻKA", "low"
        return "OK", "low"

    decisions = recommendations.apply(decide, axis=1)
    recommendations["action"] = [d[0] for d in decisions]
    recommendations["urgency"] = [d[1] for d in decisions]
    recommendations["units_to_order"] = (
        recommendations["recommended_stock_4w"] - recommendations["current_stock"]
    ).clip(lower=0).round(0)

    recommendations["data_source"] = recommendations["is_known_product"].apply(
        lambda x: "kategoria_znana" if x else "globalna_srednia"
    )

    # ── Wynik ──
    output_cols = [
        "product_id",
        "product_name_pl",
        "category_pl",
        "data_source",
        "current_stock",
        "forecast_total_4w",
        "avg_weekly_demand",
        "safety_stock",
        "reorder_point",
        "recommended_stock_4w",
        "units_to_order",
        "trend",
        "action",
        "urgency",
    ]
    result = recommendations[output_cols].rename(
        columns={"category_pl": "category", "product_name_pl": "product_name"}
    )

    # Zaokrąglanie
    numeric_cols = result.select_dtypes(include=[np.number]).columns
    result[numeric_cols] = result[numeric_cols].round(1)

    # Sortuj wg pilności
    urgency_order = {"high": 0, "medium": 1, "low": 2}
    result["_sort"] = result["urgency"].map(urgency_order)
    result = result.sort_values(
        ["_sort", "units_to_order"], ascending=[True, False]
    ).drop("_sort", axis=1)

    # ── NAPRAWA NaN/Inf → JSON compatible ──
    # NaN i Inf nie są poprawnym JSON-em, zamieniamy na None i 0
    result = result.replace([np.inf, -np.inf], 0)
    result = result.where(pd.notna(result), None)  # NaN → None (JSON null)

    # actions_summary też może mieć NaN-y w kluczach jeśli akcja nie była obliczona
    actions_summary = result["action"].fillna("BRAK_DANYCH").value_counts().to_dict()
    
    # total_units_to_order: NaN-safe
    total_order = result["units_to_order"].fillna(0).sum()
    
    return {
        "total_products": len(result),
        "known_products": int(recommendations["is_known_product"].sum()),
        "unknown_products": int((~recommendations["is_known_product"]).sum()),
        "actions_summary": actions_summary,
        "total_units_to_order": float(total_order) if not pd.isna(total_order) else 0.0,
        "recommendations": result.to_dict(orient="records"),
    }
