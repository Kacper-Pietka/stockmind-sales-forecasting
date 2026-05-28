# ═══════════════════════════════════════════════════════════════════
# EKSPORT ARTEFAKTÓW DLA APLIKACJI WEBOWEJ (Etap 5)
# ═══════════════════════════════════════════════════════════════════
# Ta komórka generuje wszystkie pliki potrzebne aplikacji FastAPI + Streamlit.
# Pliki idą do folderu app/artifacts/ — backend je tam wczytuje przy starcie.

from pathlib import Path

# Ścieżka do folderu artifacts (zakładamy że projekt ma strukturę:
#   /KursDataSianace/projekt.ipynb
#   /KursDataSianace/app/artifacts/  <- tu zapisujemy
# Jeśli aplikacja jest gdzie indziej, zmień ścieżkę.

app_artifacts = Path('app/artifacts')
app_artifacts.mkdir(parents=True, exist_ok=True)

# 1. Inventory (zawiera safety_stock, reorder_point, trend, RMSE)
inventory_df.to_csv(app_artifacts / 'inventory_recommendations.csv', 
                    index=False, encoding='utf-8')

# 2. Forecast tygodniowy
forecast_export = forecast_df.copy()
forecast_export['forecast'] = forecast_export['forecast'].round(1)
forecast_export['week_start'] = forecast_export['week_start'].astype(str)
forecast_export.to_csv(app_artifacts / 'forecast_4_weeks.csv',
                       index=False, encoding='utf-8')

# 3. Trendy
trends_df.to_csv(app_artifacts / 'trends_summary.csv',
                 index=False, encoding='utf-8')

# 4. Mapa product_id -> kategoria (do drill-down i merge w API)
product_category_map_export = (
    delivered_df[['product_id', 'product_category_name_english']]
    .drop_duplicates(subset='product_id')
    .dropna()
)
product_category_map_export.to_csv(app_artifacts / 'product_category_map.csv',
                                    index=False, encoding='utf-8')

# 5. Metryki modelu (dla dashboardu)
test_pred = np.maximum(best_model.predict(X_test), 0)
metrics_export = pd.DataFrame([
    {'metric': 'model', 'value': best_model_name},
    {'metric': 'RMSE', 'value': float(rmse(y_test, test_pred))},
    {'metric': 'MAE', 'value': float(mean_absolute_error(y_test, test_pred))},
    {'metric': 'MAPE', 'value': float(mape(y_test, test_pred))},
    {'metric': 'n_features', 'value': len(FEATURES)},
    {'metric': 'train_size', 'value': len(X_train)},
    {'metric': 'test_size', 'value': len(X_test)},
])
metrics_export.to_csv(app_artifacts / 'model_metrics.csv',
                      index=False, encoding='utf-8')

print(f"✓ Eksport zakończony: {app_artifacts.absolute()}")
print(f"\nPliki:")
for f in sorted(app_artifacts.glob('*.csv')):
    print(f"  - {f.name:40s}  {f.stat().st_size / 1024:>6.1f} KB")
