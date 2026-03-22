import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

# 1. Chargement des données
@st.cache_data
def load_data():
    return pd.read_csv("Dataset.csv")

df = load_data()

st.title("Dashboard Interactif - Analyse des Transactions")

# 2. Sidebar - Filtres dynamiques
st.sidebar.header("Filtres")

# convertir la variable TransactionStartTime
df["TransactionStartTime"] = pd.to_datetime(df["TransactionStartTime"])
df.head()

# récupérer la date, l'heure, le jour et le mois des transactions
df['Date'] = df['TransactionStartTime'].dt.date
df['Hour'] = df['TransactionStartTime'].dt.hour
df['Day'] = df['TransactionStartTime'].dt.day
df['Month'] = df['TransactionStartTime'].dt.month
df.head()

# supprimer la colonne TransactionStartTime
df.drop(['TransactionStartTime'], axis =1, inplace =True)
df.head()

# Conversion Date si présente
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    date_min = df['Date'].min()
    date_max = df['Date'].max()
    date_range = st.sidebar.date_input("Filtrer par Date", [date_min, date_max])

    if len(date_range) == 2:
        df = df[(df['Date'] >= pd.to_datetime(date_range[0])) & (df['Date'] <= pd.to_datetime(date_range[1]))]

# # Filtres catégoriels multiples
colonnes_categorique = df.select_dtypes(include=['object', 'category']).columns.tolist()
for col in colonnes_categorique:
    valeurs = df[col].unique().tolist()
    selection = st.sidebar.multiselect(f"{col}", valeurs, default=valeurs)
    df = df[df[col].isin(selection)]

# 3. Sélection pour Graphiques
colonnes_numerique = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

col_x = st.sidebar.selectbox("Variable X (catégorique)", colonnes_categorique)
col_y = st.sidebar.selectbox("Variable Y (numérique)", colonnes_numerique)
col_color = st.sidebar.selectbox("Variable couleur (optionnel)", [None] + colonnes_categorique)

# 4. Affichage de Graphiques

# Ligne de tendance par date
if 'Date' in df.columns:
    st.subheader("Évolution temporelle")
    line_data = df.groupby('Date')[col_y].mean().reset_index()
    fig_line = px.line(line_data, x='Date', y=col_y, title=f"{col_y} moyen au fil du temps")
    st.plotly_chart(fig_line, use_container_width=True)

# Histogramme
st.subheader("Histogramme interactif")
fig_hist = px.histogram(df, x=col_y, color=col_color, nbins=30)
st.plotly_chart(fig_hist, use_container_width=True)

# Barplot (moyenne par catégorie)
st.subheader("Moyenne par catégorie")
agg_data = df.groupby(col_x)[col_y].mean().reset_index()
fig_bar = px.bar(agg_data, x=col_x, y=col_y, color=col_x, title=f"Moyenne de {col_y} par {col_x}")
st.plotly_chart(fig_bar, use_container_width=True)


# Heatmap de corrélation
st.subheader("Heatmap de Corrélation")
corr = df[colonnes_numerique].corr()
fig_corr, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig_corr)

# Pie chart
if col_x:
    st.subheader("Répartition des catégories")
    fig_pie = px.pie(df, names=col_x, title=f"Répartition de {col_x}")
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. Analyse tabulaire
st.subheader("Analyse Tabulaire")
groupby_col = st.selectbox("Grouper par", colonnes_categorique)
agg_col = st.multiselect("Colonnes à agréger", colonnes_numerique, default=colonnes_numerique[:1])
if groupby_col and agg_col:
    st.dataframe(df.groupby(groupby_col)[agg_col].agg(['mean', 'sum', 'count']).round(2))

# 6. Données brutes
with st.expander("Aperçu des données"):
    st.dataframe(df)

# 7. Téléchargement des données filtrées
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Télécharger les données filtrées", csv, "transactions_filtrées.csv", "text/csv")
