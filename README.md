# Анализ кредитного портфеля — банк «ЦифраФинанс»

Проектная работа: очистка данных, анализ дефолтности, сегментация,
рекомендации по кредитной политике, аудит отчёта стажёра, дашборд мониторинга.

## Состав репозитория
- `MyCode_Striukova_Anastasia_Stanislavovna.ipynb` — весь код анализа (Этапы 1–5), запускается последовательно
- `dashboard_Striukova_Anastasia_Stanislavovna.py` — дашборд (Streamlit)
- `loan_portfolio.csv`, `branch_reference.csv` — исходные данные
- `*_Striukova_Anastasia_Stanislavovna.csv` — артефакты: журнал очистки, план-факт, рекомендации, ошибки стажёра
- `requirements.txt` — зависимости

## Запуск анализа
1. Скачать репозиторий (Code → Download ZIP) или клонируй: `git clone <ссылка>`
2. Установить зависимости `pip install -r requirements.txt`
3. Открыть `MyCode_Striukova_Anastasia_Stanislavovna.ipynb` → Kernel → Restart & Run All

## Запуск дашборда локально
streamlit run `dashboard_Striukova_Anastasia_Stanislavovna.py`

## Публичная ссылка на дашборд
https://dashboard-striukova-anastasia-stanislavovna.streamlit.app
NB: доступ без ВПН может быть нестабилен
