import csv, os
import streamlit as st
import pandas as pd
from datetime import datetime

ARCHIVO = "finanzas.csv"
CATS = ["Alimentación", "Transporte", "Arriendo", "Salud", "Educación", "Entretenimiento", "Otros"]

# ── Datos ────────────────────────────────────────────────────────────────────

def cargar():
    if not os.path.exists(ARCHIVO):
        return pd.DataFrame(columns=["fecha","tipo","categoria","descripcion","monto"])
    df = pd.read_csv(ARCHIVO)
    df["monto"] = df["monto"].astype(float)
    return df

def guardar(tipo, cat, desc, monto):
    nuevo = not os.path.exists(ARCHIVO)
    with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fecha","tipo","categoria","descripcion","monto"])
        if nuevo: w.writeheader()
        w.writerow({"fecha": datetime.now().strftime("%Y-%m-%d"), "tipo": tipo,
                    "categoria": cat, "descripcion": desc, "monto": monto})

# ── UI ───────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Finanzas Personales", page_icon="💰", layout="centered")
st.title("💰 Finanzas Personales")

df = cargar()

# Métricas resumen
ing = df[df["tipo"]=="ingreso"]["monto"].sum() if not df.empty else 0
gas = df[df["tipo"]=="gasto"]["monto"].sum()   if not df.empty else 0
bal = ing - gas

col1, col2, col3 = st.columns(3)
col1.metric("Ingresos",  f"${ing:,.0f}")
col2.metric("Gastos",    f"${gas:,.0f}")
col3.metric("Balance",   f"${bal:,.0f}", delta=f"${bal:,.0f}", delta_color="normal")

st.divider()

# Formulario de registro
st.subheader("Registrar transacción")
with st.form("registro", clear_on_submit=True):
    tipo  = st.radio("Tipo", ["ingreso", "gasto"], horizontal=True)
    cat   = st.selectbox("Categoría", CATS)
    desc  = st.text_input("Descripción", placeholder="ej: sueldo, supermercado...")
    monto = st.number_input("Monto ($)", min_value=1, step=1000)
    ok    = st.form_submit_button("Guardar", use_container_width=True)

if ok and monto > 0:
    guardar(tipo, cat, desc or "Sin descripción", monto)
    st.success(f"✓ {tipo.capitalize()} de ${monto:,.0f} guardado.")
    st.rerun()

st.divider()

# Gráfico por categoría
if not df.empty:
    st.subheader("Gastos por categoría")
    gastos_cat = (df[df["tipo"]=="gasto"]
                  .groupby("categoria")["monto"]
                  .sum()
                  .sort_values(ascending=False))
    if not gastos_cat.empty:
        st.bar_chart(gastos_cat)

    # Historial
    st.subheader("Últimas transacciones")
    historial = df.iloc[::-1].head(15).copy()
    historial["monto"] = historial.apply(
        lambda r: f"+${r['monto']:,.0f}" if r["tipo"]=="ingreso" else f"-${r['monto']:,.0f}", axis=1)
    st.dataframe(historial[["fecha","tipo","categoria","descripcion","monto"]],
                 use_container_width=True, hide_index=True)
else:
    st.info("Aún no hay transacciones. ¡Registra la primera arriba!")
