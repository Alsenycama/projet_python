import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

# 1. Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("My_Dataset.csv")

    # Conversion date
    df["TransactionStartTime"] = pd.to_datetime(df["TransactionStartTime"])

    # Nouvelles colonnes temporelles
    df["DATE"] = df["TransactionStartTime"].dt.date
    df["JOUR"] = df["TransactionStartTime"].dt.day_name()
    df["SEMAINE"] = df["TransactionStartTime"].dt.isocalendar().week
    df["MOIS"] = df["TransactionStartTime"].dt.month_name()

    # Colonne FRAUDE
    df["FRAUDE"] = df["FraudResult"].apply(lambda x: "Fraude" if x == 1 else "Non fraude")

    return df

df = load_data()

st.title("Dashboard - Analyse des Transactions et Fraudes")

# 2. SIDEBAR (FILTRES)
st.sidebar.header("Filtres")

# Filtre par mois
mois = st.sidebar.multiselect("Choisir le mois", df["MOIS"].unique(), default=df["MOIS"].unique())
df = df[df["MOIS"].isin(mois)]

# Filtre par canal
canal = st.sidebar.multiselect("Choisir le canal", df["ChannelId"].unique(), default=df["ChannelId"].unique())
df = df[df["ChannelId"].isin(canal)]

# Filtre fraude
fraude = st.sidebar.multiselect("Type de transaction", df["FRAUDE"].unique(), default=df["FRAUDE"].unique())
df = df[df["FRAUDE"].isin(fraude)]

# 3. KPIs 
col1, col2, col3 = st.columns(3)

col1.metric("Nombre total de transactions", len(df))
col2.metric("Montant total", f"{df['Amount'].sum():,.0f}")
col3.metric("Taux de fraude", f"{df['FraudResult'].mean()*100:.2f}%")

# 4. GRAPHIQUES

# Evolution dans le temps
st.subheader("Evolution des transactions")
evolution = df.groupby("DATE")["Amount"].sum().reset_index()
fig_line = px.line(evolution, x="DATE", y="Amount", title="Montant des transactions par date")
st.plotly_chart(fig_line, use_container_width=True)

# Fraude par canal
st.subheader("Fraude par canal")
fraud_canal = df.groupby(["ChannelId", "FRAUDE"]).size().reset_index(name="Count")
fig_bar = px.bar(fraud_canal, x="ChannelId", y="Count", color="FRAUDE",
             title="Fraude vs Non fraude par canal")
st.plotly_chart(fig_bar, use_container_width=True)

# Histogramme des montants
st.subheader("Distribution des montants")
fig_hist = px.histogram(df, x="Amount", color="FRAUDE", nbins=30)
st.plotly_chart(fig_hist, use_container_width=True)

# Pie chart fraude
st.subheader("Répartition des fraudes")
fig_pie = px.pie(df, names="FRAUDE", title="Fraude vs Non fraude")
st.plotly_chart(fig_pie, use_container_width=True)

# Analyse par mois
st.subheader("Analyse mensuelle")
monthly = df.groupby("MOIS")["Amount"].sum().reset_index()
fig_month = px.bar(monthly, x="MOIS", y="Amount", title="Montant total par mois")
st.plotly_chart(fig_month, use_container_width=True)

# 5. TABLEAU
st.subheader("Données filtrées")
st.dataframe(df)

# 6. TELECHARGEMENT
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Télécharger les données", csv, "dataset_filtrée.csv", "text/csv")