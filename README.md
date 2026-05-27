# Dashboard Visual de Anime 2024

Este proyecto carga el dataset de Kaggle `Top Anime Dataset 2024` y crea un dashboard visual con recomendaciones y una gráfica de los animes con más reseñas.

## Qué hace

- Descarga el dataset con `kagglehub`
- Carga los datos en SQLite
- Ejecuta consultas SQL para generar el dashboard
- Muestra un gráfico de los animes con más reseñas
- Ofrece recomendaciones basadas en `rating` y `reviews`
- Permite filtrar por género

## Cómo usarlo

1. Descarga el dataset desde Kaggle si no lo tienes:
   https://www.kaggle.com/datasets/bhavyadhingra00020/top-anime-dataset-2024
2. Copia el archivo CSV en la carpeta del proyecto como `data/top_anime_2024.csv`.
   - También se aceptan nombres alternativos: `data/top_anime.csv`, `data/anime.csv`, `top_anime_2024.csv`, `top_anime.csv`, `anime.csv`
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la aplicación SQL:
   ```bash
   streamlit run app_sql.py
   ```

## Qué verás en `app_sql.py`

- Descarga automática del dataset usando `kagglehub`
- Carga en una base SQLite local `data/anime.db`
- Consulta SQL de los `Top 12` por reseñas
- Recomendaciones SQL por:
  - Mejores Ratings
  - Más Reseñas
  - Opción combinada
- Dashboard visual con gráfico y tabla

## Uso directo con SQL

- `anime_queries.sql`: consultas SQL reutilizables para llamar desde Python o cualquier cliente SQLite.
- `anime_sql.py`: script Python que crea o actualiza `data/anime.db` desde el CSV y ejecuta las consultas definidas en `anime_queries.sql`.

## Cómo ejecutar `anime_sql.py`

1. Asegúrate de tener el CSV en:
   - `data/top_anime_2024.csv`
   - `data/top_anime.csv`
   - `data/anime.csv`
   - o en la raíz con esos nombres

2. Ejecuta:
   ```powershell
   python anime_sql.py
   ```

3. Si quieres ejecutar solo una consulta específica, usa un número o nombre:
   ```powershell
   python anime_sql.py 1
   python anime_sql.py top_reviews
   python anime_sql.py mejor_rating
   python anime_sql.py mas_reseñas
   python anime_sql.py combinado
   python anime_sql.py filtro_genero
   ```
4. Si no tienes el CSV local, el script intentará descargar el dataset automáticamente usando `kagglehub`.

## Archivos

- `app.py`: dashboard visual en Streamlit sin SQL
- `app_sql.py`: dashboard con descarga y consultas SQL usando SQLite
- `anime_queries.sql`: archivo SQL con consultas de ejemplo
- `anime_sql.py`: script Python que carga el CSV y ejecuta `anime_queries.sql`
- `requirements.txt`: dependencias necesarias
- `README.md`: instrucciones de uso

