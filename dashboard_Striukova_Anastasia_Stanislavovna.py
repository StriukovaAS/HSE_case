# ==========================================================
# Дашборд еженедельного мониторинга портфеля
# Банк «ЦифраФинанс» | Streamlit + Plotly
# Запуск: streamlit run dashboard_Striukova.py
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="ЦифраФинанс — мониторинг портфеля", layout="wide")

SURNAME = "Striukova"
LGD = 0.45  # допущение Этапа 3

@st.cache_data
def load_data():
    df = pd.read_csv(f"loan_portfolio_clean_{SURNAME}.csv", parse_dates=["issue_date"])
    pf = pd.read_csv(f"plan_fact_{SURNAME}.csv")
    return df, pf

df, pf = load_data()

st.title("Банк «ЦифраФинанс» — еженедельный мониторинг портфеля")

# ---------------- ФИЛЬТРЫ ----------------
with st.sidebar:
    st.header("Фильтры")
    regions = st.multiselect("Регион", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
    channels = st.multiselect("Канал", sorted(df["channel"].unique()), default=sorted(df["channel"].unique()))
    products = st.multiselect("Продукт", sorted(df["loan_product"].unique()), default=sorted(df["loan_product"].unique()))
    d_min, d_max = df["issue_date"].min().date(), df["issue_date"].max().date()
    period = st.date_input("Период выдач", value=(d_min, d_max), min_value=d_min, max_value=d_max)

start_d, end_d = period if isinstance(period, (list, tuple)) and len(period) == 2 else (d_min, d_max)

fdf = df[
    df["region"].isin(regions)
    & df["channel"].isin(channels)
    & df["loan_product"].isin(products)
    & df["issue_date"].dt.date.between(start_d, end_d)
].copy()

if fdf.empty:
    st.warning("Под выбранные фильтры не попал ни один кредит.")
    st.stop()

# ---------------- 4 KPI ----------------
st.subheader("Ключевые показатели")
k1, k2, k3, k4 = st.columns(4)

volume = fdf["loan_amount"].sum()
dr = fdf["is_default"].mean() * 100
el = dr / 100 * volume * LGD
avg_dti = fdf["dti_ratio"].mean()

k1.metric("Объём портфеля", f"{volume / 1e6:,.1f} млн ₽", f"{len(fdf):,} кредитов")
k2.metric("Default rate", f"{dr:.1f}%", f"{dr - 10:+.1f} п.п. к цели 10%", delta_color="inverse")
k3.metric("Expected Loss", f"{el / 1e6:,.1f} млн ₽", "LGD = 45%", delta_color="inverse")
k4.metric("Средний DTI", f"{avg_dti:.1f}%")

# ---------------- Динамика выдач и дефолтов (две оси) ----------------
st.subheader("Динамика выдач и дефолтов по кварталам")
fdf["quarter"] = fdf["issue_date"].dt.to_period("Q").astype(str)
q = fdf.groupby("quarter").agg(issued=("loan_id", "count"), defaults=("is_default", "sum")).reset_index()
q["default_rate"] = (q["defaults"] / q["issued"] * 100).round(1)

fig_dyn = make_subplots(specs=[[{"secondary_y": True}]])
fig_dyn.add_trace(go.Bar(x=q["quarter"], y=q["issued"], name="Выдачи, шт", marker_color="#4c78a8"), secondary_y=False)
fig_dyn.add_trace(go.Scatter(x=q["quarter"], y=q["default_rate"], name="Default rate, %",
                             mode="lines+markers", line=dict(color="#e45756", width=3)), secondary_y=True)
fig_dyn.update_yaxes(title_text="Выдачи, шт", secondary_y=False)
fig_dyn.update_yaxes(title_text="Default rate, %", secondary_y=True)
fig_dyn.update_layout(height=420, legend=dict(orientation="h", y=1.08))
st.plotly_chart(fig_dyn, use_container_width=True)

# ---------------- Тепловая карта + scatter ----------------
col_hm, col_sc = st.columns(2)

with col_hm:
    st.subheader("DR: канал × тип занятости")
    hm = (fdf.pivot_table(values="is_default", index="channel", columns="employment_type", aggfunc="mean") * 100).round(1)
    fig_hm = px.imshow(hm, text_auto=".1f", color_continuous_scale="YlOrRd", aspect="auto",
                       labels=dict(x="Тип занятости", y="Канал", color="DR, %"))
    fig_hm.update_layout(height=420)
    st.plotly_chart(fig_hm, use_container_width=True)

with col_sc:
    st.subheader("Credit score × DTI")
    fig_sc = px.scatter(fdf, x="credit_score", y="dti_ratio", color="is_default",
                        color_discrete_map={0: "#2ca02c", 1: "#d62728"},
                        labels=dict(credit_score="Credit score", dti_ratio="DTI, %", is_default="Дефолт"),
                        opacity=0.45, height=420)
    st.plotly_chart(fig_sc, use_container_width=True)

# ---------------- План-факт с подсветкой ----------------
st.subheader("План-факт по справочнику (регион × канал)")
pf_view = pf[pf["region"].isin(regions) & pf["channel"].isin(channels)].copy()

def status_color(v):
    if v == "OK":
        return "background-color: #c8e6c9"
    if v == "BAD":
        return "background-color: #ffcdd2"
    return ""

status_cols = ["pd_status", "score_status", "dti_status"]
try:
    styler = pf_view.style.map(status_color, subset=status_cols)
except AttributeError:  # старый pandas
    styler = pf_view.style.applymap(status_color, subset=status_cols)

styler = styler.format({
    "fact_pd": "{:.1%}", "plan_default_rate": "{:.1%}", "dev_pd": "{:+.1%}",
    "fact_score": "{:.0f}", "plan_credit_score": "{:.0f}", "dev_score": "{:+.1f}",
    "fact_dti": "{:.1f}", "plan_dti": "{:.1f}", "dev_dti": "{:+.1f}",
})

st.dataframe(styler, use_container_width=True)
st.caption("Зелёный — факт лучше плана, красный — хуже. Комбинации без плана не выводятся (ограничение анализа).")