# 🚀 Sales Forecast App — Etap 5

Aplikacja webowa do systemu predykcji sprzedaży e-commerce (Olist).

**Stack:**
- **Backend:** FastAPI (Python REST API) — port `8000`
- **Frontend:** Streamlit (dashboard) — port `8501`
- **Orkiestracja:** Docker Compose

## 📁 Struktura projektu

```
app/
├── backend/
│   ├── main.py              ← FastAPI: endpointy /recommend, /categories itd.
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py               ← Streamlit: 3 widoki (Dashboard, Drill-down, Upload)
│   ├── requirements.txt
│   └── Dockerfile
├── artifacts/               ← TU MUSZĄ BYĆ CSV-KI Z NOTEBOOKA
│   ├── inventory_recommendations.csv
│   ├── forecast_4_weeks.csv
│   ├── trends_summary.csv
│   ├── product_category_map.csv
│   └── model_metrics.csv
├── docker-compose.yml
└── README.md
```

## 🏁 Quick Start (3 kroki)

### 1️⃣ Wygeneruj artefakty w notebooku

W notebooku **`projekt_grupowy_HYBRID.ipynb`** dodaj na końcu (po Etapie 4) komórkę
ze skryptem **`EXPORT_CELL_to_notebook.py`** (z tego folderu) i uruchom ją.

Skrypt zapisze 5 plików CSV do `app/artifacts/`:
- `inventory_recommendations.csv` — prognozy + safety stock per kategoria
- `forecast_4_weeks.csv` — szczegółowa prognoza tygodniowa
- `trends_summary.csv` — wszystkie trendy
- `product_category_map.csv` — mapa product_id → kategoria (do drill-down)
- `model_metrics.csv` — RMSE, MAE, MAPE z testu

### 2️⃣ Odpal aplikację (Docker Compose)

```bash
cd app/
docker compose up --build
```

Pierwszy build trwa ~2-3 min. Kolejne odpalenia ~10 sekund.

### 3️⃣ Otwórz w przeglądarce

- **Streamlit (dashboard):** http://localhost:8501
- **FastAPI (API + docs):** http://localhost:8000/docs

## 🖼 Widoki aplikacji

### Dashboard (🏠)
- Metryki modelu (RMSE, MAE, MAPE)
- KPI strip: liczba kategorii, sumaryczna prognoza, sumaryczny safety stock
- Pie chart rozkładu trendów
- Top 10 kategorii wg zapotrzebowania
- Tabela kategorii z filtrowaniem po trendzie

### Drill-down (🔍)
- Wybierz kategorię → zobacz:
  - Prognozę tygodniową (bar chart + safety stock line)
  - Rekomendację stanu magazynu
  - Trend (rosnący/spadający/stabilny + zmiana %)
  - Listę product_id w kategorii

### Upload CSV (📤)
- Wgraj plik z aktualnym magazynem: `product_id,current_stock`
- System zwraca pełne rekomendacje per produkt:
  - Akcja (ZAMÓW PILNIE / ZAMÓW / OBSERWUJ / OK / NADWYŻKA)
  - Ile zamówić (units_to_order)
  - Trend kategorii
  - Czy bazuje na konkretnej kategorii czy globalnej średniej
- Filtruj wyniki + pobierz jako CSV

## 🔌 API Endpointy (FastAPI)

| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/` | Health check |
| GET | `/metrics` | Metryki modelu |
| GET | `/categories` | Lista wszystkich kategorii z prognozami |
| GET | `/categories/{name}` | Szczegóły kategorii (drill-down) |
| GET | `/categories/{name}/products` | Produkty w kategorii |
| GET | `/trends` | Wszystkie trendy |
| POST | `/recommend` | Upload CSV → rekomendacje |

Pełna dokumentacja API: http://localhost:8000/docs (Swagger UI auto-generowany).

## 🛠 Komendy

```bash
# Uruchom aplikację
docker compose up

# Uruchom w tle
docker compose up -d

# Zatrzymaj
docker compose down

# Przebuduj po zmianach w kodzie
docker compose up --build

# Logi
docker compose logs -f backend
docker compose logs -f frontend

# Wejdź do kontenera
docker compose exec backend bash
```

## ⚠ Troubleshooting

**Frontend pokazuje "Nie można połączyć się z API"**
- Sprawdź czy backend działa: `docker compose logs backend`
- Czy port 8000 nie jest zajęty? `netstat -an | findstr 8000`

**Backend pokazuje "Artefakty nie wczytane"**
- Czy folder `artifacts/` zawiera 5 plików CSV?
- Sprawdź czy notebook wygenerował artefakty (krok 1)

**Port 8501 zajęty (Streamlit)**
- Zmień port w `docker-compose.yml`: `"8502:8501"` zamiast `"8501:8501"`

## 🎯 Co pokazać na zjeździe

1. **Architektura** — backend i frontend oddzielnie, komunikują się przez REST API
2. **Docker** — jedno polecenie i działa, niezależne od systemu
3. **API auto-docs** — Swagger UI w `/docs`
4. **Drill-down** — kategoria → produkty w niej
5. **Upload CSV** — pipeline pełen przez UI
6. **Filtrowanie + download** — gotowy raport dla klienta
