import pathlib
import sqlite3
import zipfile

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard Anime SQL",
    page_icon="🎌",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {background: linear-gradient(180deg, #08122d 0%, #162b58 100%); color: #f9fafb;}
    .stApp {background: linear-gradient(180deg, #091836 0%, #1d2f62 100%);}
    .block-container {padding: 1.5rem 2rem 2rem;}
    h1, h2, h3, p, div {color: #f9fafb;}
    .stButton>button {background-color: #f45b8f; color: white;}
    .stButton>button:hover {background-color: #e73d78;}
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "anime.db"
CSV_CANDIDATES = ["top_anime_2024.csv", "top_anime.csv", "anime.csv"]

st.title("Top Anime 2024 — SQL Dashboard")
st.subheader("Descarga con kagglehub, carga con SQLite y muestra recomendaciones con SQL")

try:
    import kagglehub
except Exception as exc:
    st.error("No se puede importar kagglehub. Instala las dependencias con `pip install -r requirements.txt`.")
    st.stop()


def find_local_csv():
    for name in CSV_CANDIDATES:
        local = DATA_DIR / name
        if local.exists():
            return local
        local = pathlib.Path(name)
        if local.exists():
            return local
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    return csv_files[0] if csv_files else None


def download_dataset():
    try:
        downloaded = pathlib.Path(kagglehub.dataset_download("bhavyadhingra00020/top-anime-dataset-2024"))
        if not downloaded.exists():
            return None
        if downloaded.suffix == ".zip":
            with zipfile.ZipFile(downloaded, "r") as archive:
                archive.extractall(DATA_DIR)
            csv_file = find_local_csv()
            return csv_file
        if downloaded.suffix == ".csv":
            destination = DATA_DIR / downloaded.name
            if downloaded.parent != DATA_DIR:
                downloaded.replace(destination)
            return destination
        return find_local_csv()
    except Exception:
        return None


csv_path = find_local_csv()
if csv_path is None:
    st.info("No se encontró un archivo CSV local. Intentando descargar el dataset desde Kaggle...")
    csv_path = download_dataset()

if csv_path is None:
    st.error(
        "No se encontró el dataset local ni se pudo descargar automáticamente."
    )
    st.info(
        "Coloca el CSV en la carpeta `data/` o en la raíz del proyecto con nombre `top_anime_2024.csv`, `top_anime.csv` o `anime.csv`."
    )
    st.stop()

st.success(f"Dataset encontrado en: {csv_path}")

try:
    df = pd.read_csv(csv_path)
except Exception as exc:
    st.error(f"Error leyendo el CSV: {exc}")
    st.stop()

available_cols = {col.lower(): col for col in df.columns}
name_col = next((available_cols[c] for c in ["name", "title", "anime_name", "anime"] if c in available_cols), None)
rating_col = next((available_cols[c] for c in ["rating", "score", "avg_rating", "ratings"] if c in available_cols), None)
review_col = next((available_cols[c] for c in ["rating_count", "reviews", "members", "votes"] if c in available_cols), None)
genre_col = next((available_cols[c] for c in ["genre", "genres"] if c in available_cols), None)

if name_col is None or rating_col is None:
    st.error("El CSV no tiene columnas esperadas de nombre o rating. Revisa el archivo.")
    st.write("Columnas encontradas:", list(df.columns))
    st.stop()

if review_col is None and "members" in available_cols:
    review_col = available_cols["members"]

if review_col is None:
    st.error("No se encontró una columna válida para reseñas / reviews / miembros.")
    st.stop()

selected_columns = [name_col, rating_col, review_col]
if genre_col:
    selected_columns.append(genre_col)

clean_df = df[selected_columns].copy()
rename_map = {name_col: "anime", rating_col: "rating", review_col: "reviews"}
if genre_col:
    rename_map[genre_col] = "genre"

clean_df = clean_df.rename(columns=rename_map)
clean_df["anime"] = clean_df["anime"].astype(str)
clean_df["rating"] = pd.to_numeric(clean_df["rating"], errors="coerce")
clean_df["reviews"] = pd.to_numeric(clean_df["reviews"], errors="coerce")
clean_df = clean_df.dropna(subset=["anime", "rating"])
clean_df["reviews"] = clean_df["reviews"].fillna(0).astype(int)

conn = sqlite3.connect(DB_PATH)
clean_df.to_sql("anime", conn, if_exists="replace", index=False)

st.markdown("---")

st.markdown("### Consulta SQL: Animes con más reseñas")
query_reviews = "SELECT anime, rating, reviews FROM anime ORDER BY reviews DESC LIMIT 12"
top_reviews = pd.read_sql_query(query_reviews, conn)

fig = px.bar(
    top_reviews[::-1],
    x="reviews",
    y="anime",
    orientation="h",
    color="rating",
    color_continuous_scale="Tealgrn",
    labels={"anime": "Anime", "reviews": "Reseñas", "rating": "Rating"},
    title="Top 12 de animes según reseñas",
)
fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#f9fafb")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.markdown("### Recomendaciones usando SQL")
recommendation_option = st.radio(
    "Elige un criterio de recomendación:",
    ["Mejores Ratings", "Más Reseñas", "Combinado"],
)

sql_base = "SELECT anime, rating, reviews" + (", genre" if genre_col else "") + " FROM anime"
where_clause = ""
params = []

if genre_col:
    genre_filter = st.selectbox(
        "Filtrar por género:",
        ["Todos"] + sorted({g.strip() for cell in clean_df["genre"].dropna() for g in str(cell).split(",") if g.strip()}),
    )
    if genre_filter != "Todos":
        where_clause = " WHERE genre LIKE ?"
        params = [f"%{genre_filter}%"]

if recommendation_option == "Mejores Ratings":
    order_clause = " ORDER BY rating DESC, reviews DESC"
elif recommendation_option == "Más Reseñas":
    order_clause = " ORDER BY reviews DESC, rating DESC"
else:
    order_clause = " ORDER BY rating DESC, reviews DESC"

recommendation_sql = sql_base + where_clause + order_clause + " LIMIT 5"
recommendations = pd.read_sql_query(recommendation_sql, conn, params=params)

for _, row in recommendations.iterrows():
    st.markdown(f"**{row['anime']}** — ⭐ {row['rating']:.2f} — {int(row['reviews']):,} reseñas")
    if genre_col and row.get("genre"):
        st.caption(f"Género: {row['genre']}")

st.markdown("---")

st.markdown("### Tabla de resultados SQL")
st.dataframe(top_reviews, use_container_width=True)

st.markdown("---")

st.caption(f"Base SQLite creada en: {DB_PATH}")
conn.close()
