# 📦 StockMind — Predykcja Sprzedaży E-commerce

> **Predict. Optimize. Grow.**
> Inteligentny system prognozowania sprzedaży i optymalizacji stanów magazynowych dla e-commerce, oparty na danych z brazylijskiej platformy Olist.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

---

## 📋 Spis treści

- [O projekcie](#-o-projekcie)
- [Architektura](#-architektura)
- [Pipeline Data Science](#-pipeline-data-science)
- [Stack technologiczny](#-stack-technologiczny)
- [Struktura repozytorium](#-struktura-repozytorium)
- [Instalacja i uruchomienie](#-instalacja-i-uruchomienie)
- [API — endpointy](#-api--endpointy)
- [Aplikacja webowa](#-aplikacja-webowa)
- [Format danych wejściowych](#-format-danych-wejściowych)
- [Zespół](#-zespół)

---

## 🎯 O projekcie

> 🎓 **Projekt zaliczeniowy** kursu **Data Science + AI** w [infoShare Academy](https://infoshareacademy.com/).

**StockMind** to end-to-endowy projekt Data Science obejmujący pełen cykl: od surowych danych transakcyjnych, przez eksplorację (EDA), feature engineering, trening i porównanie 7 modeli ML, aż po wdrożenie w postaci REST API i interaktywnej aplikacji webowej.

### Co rozwiązujemy?

Sklepy e-commerce stają przed dwoma odwiecznymi problemami magazynowymi:
- **Brakami towaru** → utrata sprzedaży i niezadowoleni klienci
- **Nadwyżkami** → zamrożony kapitał, koszty magazynowania, ryzyko przeterminowania

StockMind dostarcza:
1. **Prognozę sprzedaży na 4 tygodnie naprzód** dla każdej kategorii produktów
2. **Rekomendowany stan magazynowy** uwzględniający bufor bezpieczeństwa
3. **Wykrywanie trendów** (rosnący / spadający / stabilny)
4. **Konkretne akcje biznesowe** per produkt na podstawie wgranego pliku z magazynu klienta

### Źródło danych

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — ~100k zamówień, 9 powiązanych tabel relacyjnych (ERD), dane z lat 2016–2018.

---

## 🏗 Architektura

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Notebook (ML)  │  ───>   │  Artefakty CSV  │  ───>   │  FastAPI (8000) │
│  Trening modelu │         │   /artifacts/   │         │  REST endpoints │
└─────────────────┘         └─────────────────┘         └────────┬────────┘
                                                                  │
                                                                  │ HTTP/JSON
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │ Streamlit (8501)│
                                                         │   Frontend UI   │
                                                         └─────────────────┘
```

**Decyzja architektoniczna:** rozdzielenie warstw na trzy niezależne komponenty.

- **Notebook** trenuje modele *offline* — wynikiem są pliki CSV (prognozy, rekomendacje, trendy). To prosta, ale solidna strategia "batch inference" — nie trzeba uruchamiać modelu na produkcji ani trzymać go w pamięci API.
- **FastAPI** to cienka warstwa serwująca dane z CSV-ek + obsługująca upload pliku klienta (`POST /recommend`).
- **Streamlit** to czysty frontend — komunikuje się z API przez HTTP, nie ma żadnej logiki biznesowej.

> 💡 **Dlaczego nie online inference?** Prognoza sprzedaży jest *tygodniowa* — nie ma potrzeby przeliczać jej w czasie rzeczywistym. Batch processing raz w tygodniu jest tańszy, bardziej przewidywalny i łatwiejszy w utrzymaniu.

---

## 🔬 Pipeline Data Science

Projekt jest podzielony na 5 etapów, każdy w osobnej sekcji notebooka:

### Etap 0 — Pozyskanie danych
Wczytanie 9 tabel Olist + polskie tłumaczenia nazw produktów i kategorii. Połączenie zgodnie ze schematem ERD, z agregacją relacji 1:N **przed** mergem (uniknięcie duplikacji wierszy).

### Etap 1 — EDA (Exploratory Data Analysis)
- Czyszczenie dat (`errors='coerce'` → NaT zamiast crashu)
- Filtrowanie zamówień do statusu `delivered`
- Analiza cech dostawy, rozkładu cen, top kategorii
- Wizualizacja sprzedaży w czasie i metod płatności

### Etap 2 — Feature Engineering

Agregacja danych do **granulacji tygodniowej** per kategoria.

> **Dlaczego tydzień, a nie dzień?** Sprzedaż dzienna ma za dużo szumu i sezonowości tygodniowej (weekend ≠ wtorek). Tydzień wygładza szum, ale zachowuje wystarczającą rozdzielczość biznesową.

Inżynieria cech:
- **Lagi** (lag_1, lag_2, lag_4, lag_8) — sprzedaż sprzed N tygodni
- **Rolling statistics** — średnia, mediana, std w oknach 4 i 8 tygodni
- **Momentum** i `pct_change` — dynamika zmian
- **Cechy czasowe** — miesiąc, tydzień roku, kwartał
- **Święta brazylijskie** — flagi binarne

Krytyczne decyzje:
- **Podział chronologiczny 70/15/15** (a nie losowy!) — przy szeregach czasowych losowy split powoduje *data leakage* (model "widzi przyszłość").
- **Target encoding tylko z train setu** — kategorie kodowane jako średnia sprzedaży z train. Użycie val/test do encodingu = leakage.
- **NIE robimy `dropna()` na wszystkim** — tylko filtrujemy po statusie zamówienia, usuwamy braki TYLKO w kluczowych kolumnach.

### Etap 3 — Modelowanie

Porównanie **7 modeli**:

| # | Model | Typ | Po co? |
|---|---|---|---|
| 1 | Baseline (lag_1) | Heurystyka | Punkt odniesienia — "sprzedaż w przyszłym tygodniu = sprzedaż w tym tygodniu" |
| 2 | Ridge Regression | Liniowy | Sprawdzenie czy wystarczy prosty model |
| 3 | Random Forest | Bagging | Nieliniowość bez tuningu |
| 4 | LightGBM | Boosting | Szybkie GBM Microsoftu |
| 5 | **XGBoost (tuned)** | Boosting | **Wybrany jako finalny — najlepsze RMSE** |
| 6 | CatBoost | Boosting | Specjalizacja w cechach kategorycznych |
| 7 | LSTM | Deep Learning | Test czy sieć rekurencyjna pobije GBM |

**Metryki:**
- **RMSE** — kara kwadratowa za duże błędy (kluczowa dla magazynu — duże pomyłki są kosztowne)
- **MAE** — średni błąd bezwzględny (intuicyjna interpretacja w sztukach)
- **MAPE** — błąd procentowy (porównywalność między kategoriami)

> **Dlaczego XGBoost wygrał z LSTM?** Sieci neuronowe potrzebują dużo danych i wielu kroków historycznych, żeby naprawdę zabłysnąć. Mamy ~150 tygodni × ~70 kategorii — to za mało dla LSTM, ale w sam raz dla gradient boostingu, który świetnie radzi sobie z cechami tabelarycznymi.

### Etap 4 — Trendy + Hybrydowy Safety Stock

**Predykcja rekursywna** 4 tygodni w przód — predykcja tygodnia T+1 staje się inputem (lag_1) dla T+2 itd. Trzeba uważać na propagację błędów.

**Detekcja trendów** — porównanie średniej prognozy 4 tygodni z średnią ostatnich 4 historycznych:
- `>+10%` → 📈 rosnący
- `<-10%` → 📉 spadający
- inaczej → ➡️ stabilny

**Hybrydowy Safety Stock** — kluczowa innowacja projektu.

Klasyczna formuła `Z × σ × √(LT)` zakłada normalność rozkładu popytu, co rzadko jest prawdą w e-commerce. Nasze podejście łączy:
1. **RMSE modelu per kategoria** — im gorsza prognoza, tym większy bufor
2. **Lead Time** liczony z prawdziwych danych dostawy (nie szacunek!)
3. **Globalny fallback** dla kategorii bez danych testowych

**Reorder Point** = average_weekly_demand × lead_time + safety_stock

### Etap 5 — Aplikacja webowa
Eksport artefaktów do CSV (`/artifacts/`) → FastAPI je serwuje → Streamlit konsumuje.

---

## 🛠 Stack technologiczny

**Data Science / ML:**
- `pandas`, `numpy` — manipulacja danych
- `scikit-learn` — Ridge, Random Forest, metryki
- `xgboost`, `lightgbm`, `catboost` — gradient boosting
- `tensorflow` / `keras` — LSTM
- `statsmodels` — SARIMA
- `matplotlib`, `seaborn` — wykresy w notebooku

**Backend:**
- `fastapi` — REST API
- `uvicorn` — serwer ASGI
- `pydantic` — walidacja danych

**Frontend:**
- `streamlit` — interaktywna aplikacja webowa
- `plotly` — wykresy interaktywne

---

## 📂 Struktura repozytorium

```
stockmind/
├── notebooks/
│   └── projekt_grupowy_po_etapie_4.ipynb   # Pełny pipeline ML (Etapy 0-5)
├── backend/
│   └── main.py                              # FastAPI — REST API
├── frontend/
│   ├── app.py                               # Streamlit — UI
│   └── assets/
│       └── stockmind_logo.png               # Logo aplikacji
├── artifacts/                               # Generowane przez notebook
│   ├── forecast_4_weeks.csv                 # Prognoza per kategoria × tydzień
│   ├── inventory_recommendations.csv        # Rekomendacje stanów magazynowych
│   ├── trends_summary.csv                   # Wykryte trendy
│   ├── product_lookup.csv                   # Mapowanie product_id → kategoria
│   └── model_metrics.csv                    # Metryki finalnego modelu
├── data/                                    # Surowe dane Olist (nie commitowane!)
│   └── .gitkeep
├── requirements.txt
├── .gitignore
└── README.md
```

> ⚠️ **Folder `data/`** — surowe dane Olist (~120 MB) nie są commitowane do repo. Pobierz je z [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) i wrzuć ręcznie.

---

## 🚀 Instalacja i uruchomienie

### Wymagania
- Python 3.10+
- ~2 GB RAM (LSTM podczas treningu ~4 GB)
- (opcjonalnie) GPU dla szybszego treningu LSTM

### 1. Klonowanie i środowisko

```bash
git clone https://github.com/<twoj-user>/stockmind.git
cd stockmind

python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Trening modeli (jednorazowo)

Pobierz dane Olist z Kaggle do folderu `data/`, potem uruchom notebook:

```bash
jupyter notebook notebooks/projekt_grupowy_po_etapie_4.ipynb
```

Po przejściu wszystkich komórek w folderze `artifacts/` pojawią się pliki CSV potrzebne dla API.

### 3. Uruchomienie backendu

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Sprawdź czy API działa: `http://localhost:8000` → powinno zwrócić `{"status": "ok", ...}`
Dokumentacja Swagger: `http://localhost:8000/docs`

### 4. Uruchomienie frontendu

W **drugim terminalu**:

```bash
cd frontend
streamlit run app.py
```

Aplikacja otworzy się pod adresem `http://localhost:8501`.

---

## 🔌 API — endpointy

| Metoda | Endpoint | Opis |
|--------|----------|------|
| `GET` | `/` | Health check + status załadowania artefaktów |
| `GET` | `/metrics` | Metryki modelu (RMSE, MAE, MAPE) |
| `GET` | `/categories` | Lista wszystkich kategorii z prognozami i safety stock |
| `GET` | `/categories/{name}` | Szczegóły kategorii: prognoza tygodniowa + trend |
| `GET` | `/categories/{name}/products` | Produkty w kategorii (paginowane, `?limit=50`) |
| `GET` | `/trends` | Wszystkie wykryte trendy |
| `POST` | `/recommend` | Upload CSV z magazynem → rekomendacje per produkt |

### Przykład `POST /recommend`

```bash
curl -X POST http://localhost:8000/recommend \
  -F "file=@magazyn.csv"
```

**Response:**
```json
{
  "total_products": 120,
  "known_products": 115,
  "unknown_products": 5,
  "actions_summary": {
    "ZAMÓW PILNIE": 8,
    "ZAMÓW": 23,
    "OK": 84,
    "NADWYŻKA": 5
  },
  "total_units_to_order": 1842.0,
  "recommendations": [ ... ]
}
```

---

## 🖥 Aplikacja webowa

Streamlit UI oferuje 3 strony nawigacyjne:

### 🏠 Przegląd magazynu
- KPI: liczba kategorii, łączna prognoza, rekomendowany stan, bufor bezpieczeństwa
- Top 3 kategorie rosnące / spadające z konkretnymi akcjami
- Rozkład trendów (donut chart) + top 10 kategorii (bar chart)

### 🔍 Szczegóły kategorii
- Drill-down w pojedynczą kategorię
- Wykres prognozy tygodniowej z safety stock
- Lista produktów w kategorii

### 📤 Analiza Twojego magazynu
- Upload pliku CSV ze stanem magazynowym klienta
- Automatyczne dopasowanie produktów do kategorii
- Tabela rekomendacji z filtrowaniem (akcja, pilność, źródło danych)
- Eksport raportu do CSV

---

## 📄 Format danych wejściowych

Plik CSV uploadowany przez stronę "Analiza Twojego magazynu":

```csv
product_id,current_stock
abc123def456,150
def789ghi012,42
xyz456abc789,8
```

**Wymagane kolumny:**
- `product_id` (string) — identyfikator produktu z bazy Olist
- `current_stock` (int) — aktualny stan magazynowy

**Logika decyzyjna API:**

| Warunek | Akcja | Pilność |
|---------|-------|---------|
| `current_stock < reorder_point` | 🚨 ZAMÓW PILNIE | high |
| `current_stock < forecast_4w` | 🟠 ZAMÓW | medium |
| `current_stock < recommended_stock` | 🟡 OBSERWUJ | low |
| `current_stock > recommended × 2` | 🔵 NADWYŻKA | low |
| inaczej | ✅ OK | low |

---

## 👥 Zespół

Projekt **zaliczeniowy** zrealizowany w ramach kursu **Data Science + AI** w [**infoShare Academy**](https://infoshareacademy.com/), przez **3-osobowy zespół**:

| Autor | GitHub |
|---|---|
| Kacper Pietka | [@Kacper-Pietka](https://github.com/Kacper-Pietka) |
| Ariel Korczyk | [@ArielKorczyk](https://github.com/ArielKorczyk) |
| Paweł Skurczyński | [@pawelskurczynski1-ship-it](https://github.com/pawelskurczynski1-ship-it) |

### Model pracy

Każdy członek zespołu **samodzielnie przechodził przez wszystkie etapy projektu** (EDA → Feature Engineering → Modelowanie → Trendy → Aplikacja), tworząc własną wersję rozwiązania. Następnie wspólnie porównywaliśmy podejścia, dyskutowaliśmy o wyborach metodologicznych i **łączyliśmy najlepsze elementy** każdej wersji w jeden spójny projekt finalny.

**Dlaczego taki model?** Choć jest bardziej pracochłonny niż klasyczny podział zadań, dał nam trzy ważne korzyści:
- Każdy zna **cały pipeline** — od surowych danych po endpoint API
- Mieliśmy **3 niezależne perspektywy** na każdy problem (np. wybór modelu, sposób liczenia safety stock, struktura API) — co prowadziło do lepszych decyzji
- Brak "wąskich gardeł" — żaden członek zespołu nie był jedyną osobą znającą daną część kodu

---

## 📜 Licencja

MIT License — szczegóły w pliku `LICENSE`.

---

## 🙏 Podziękowania

- **Olist** za udostępnienie zbioru danych
- **Kaggle** za platformę hostującą dataset
- Społeczność open-source za biblioteki ML i web

---

<div align="center">

**Made with ❤️ for the love of data**

⭐ Jeśli podoba Ci się projekt, zostaw gwiazdkę!

</div>
