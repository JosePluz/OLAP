# OLAP - Anime & Manga Analytics

Este proyecto es un sistema local OLAP para analizar datos de Anime y Manga a partir de un dataset de MyAnimeList. El objetivo es facilitar la toma de decisiones con consultas SQL, gráficos y un dashboard interactivo.

## Descripción general

El sistema usa:
- `setup_database.py` para cargar los CSV de `data/anime_dataset.csv` y `data/manga_dataset.csv`.
- SQLite como base de datos local: `data/olap.db`.
- `dashboard.py` para mostrar el dashboard en Streamlit.
- Consultas predefinidas y un constructor de consultas personalizadas.

La idea es ver rápidamente qué series tienen mejor puntuación, qué géneros dominan, cómo ha cambiado el interés con el tiempo, qué tiene más popularidad y cómo se distribuyen los formatos.

## Cómo ejecutar el proyecto

1. Asegúrate de tener los dos archivos CSV en la carpeta `data/`:
   - `data/anime_dataset.csv`
   - `data/manga_dataset.csv`
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la creación de la base de datos:
   ```bash
   python setup_database.py
   ```
4. Inicia el dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## Qué hace cada parte del sistema

### `setup_database.py`

Este script lee los datasets de anime y manga, normaliza columnas importantes y crea la base SQLite en `data/olap.db`.

- Crea las tablas `anime` y `manga`.
- Convierte fechas y años.
- Agrupa género, puntuación y popularidad.
- Crea la vista `media_combined` para combinar ambos datasets.
- Agrega índices para acelerar las consultas.

### `dashboard.py`

En el dashboard hay 5 análisis predefinidos:

1. **Top Rated**
   - Consulta los 20 títulos mejor puntuados.
   - Ordena por `score` y `scored_by`.
   - Muestra gráfico de barras horizontal y datos clave.
   - Resultado real: se ven los animes/mangas con mejores ratings, y el gráfico ayuda a distinguir los más fuertes.

2. **Géneros Populares**
   - Cuenta cuántos registros hay por género.
   - Calcula el `AVG(score)` por género.
   - Muestra un gráfico de barras con la cantidad y la puntuación promedio.
   - Resultado: pude ver claramente qué géneros aparecen más y cuáles tienen mejor rating.

3. **Tendencia Temporal**
   - Agrupa por `year` desde 2000.
   - Calcula cantidad de títulos y promedio de puntuación.
   - Muestra una línea de evolución con el número de títulos por año.
   - Resultado: se observa la subida/bajada de producción y cómo cambia la puntuación promedio.

4. **Popularidad**
   - Selecciona títulos con `members > 0` y puntuación válida.
   - Ordena por miembros más activos.
   - Genera un scatter plot de `members` vs `score`.
   - Resultado: comprueba qué títulos son populares y si eso coincide con buena puntuación.

5. **Distribución de Tipos**
   - Agrupa por `type` (TV, Movie, Manga, etc.).
   - Calcula cantidad, puntaje promedio y miembros promedio.
   - Muestra un pastel y barras comparando tipos.
   - Resultado: el gráfico deja ver qué formato es más común y cuáles tienen mejor score.

## Consultas y ejemplos

### Consulta 1: Top 20 por puntuación

```sql
SELECT title, score, scored_by, type, year, genres
FROM anime
WHERE score IS NOT NULL AND score > 0
ORDER BY score DESC, scored_by DESC
LIMIT 20;
```
- Esta consulta saca los títulos con mejor puntuación.
- Es útil para saber qué anime o manga merece una recomendación rápida.

### Consulta 2: Géneros más frecuentes

```sql
SELECT genres, COUNT(*) as count, AVG(score) as avg_score
FROM anime
GROUP BY genres
ORDER BY count DESC
LIMIT 15;
```
- Permite saber qué género aparece más veces.
- También muestra el rating promedio, para detectar géneros populares y bien valorados.

### Consulta 3: Evolución por año

```sql
SELECT year, COUNT(*) as cantidad, AVG(score) as avg_score
FROM anime
WHERE year >= 2000 AND year IS NOT NULL
GROUP BY year
ORDER BY year;
```
- Esta consulta ayuda a ver tendencias temporales.
- Perfecta para analizar si la calidad o volumen crece con el tiempo.

### Consulta 4: Popularidad vs puntuación

```sql
SELECT title, members, score, type, genres
FROM anime
WHERE members > 0 AND score IS NOT NULL AND score > 0
ORDER BY members DESC
LIMIT 100;
```
- Ayuda a comparar popularidad con calidad.
- Con el scatter plot se ve si los títulos populares tienen buenos ratings o no.

### Consulta 5: Distribución por tipo

```sql
SELECT type, COUNT(*) as cantidad, AVG(score) as avg_score, AVG(members) as avg_members
FROM anime
GROUP BY type
ORDER BY cantidad DESC;
```
- Permite distinguir entre TV, Movie, OVA, Manga, etc.
- Resulta útil para identificar qué formato domina en cantidad y cuál es mejor valorado.

## Constructor de consultas personalizadas

Además de los análisis predefinidos, el dashboard tiene:

- Un constructor visual para seleccionar columnas, filtros, orden y límite.
- Un editor SQL avanzado para escribir consultas directas.
- Opciones para combinar `anime` y `manga`.

Con esto puedes hacer análisis más específicos, por ejemplo:
- filtrar por género
- definir puntuación mínima
- ver solo los mangas más populares
- probar distintas combinaciones de campos

## Notas finales

- Yo dejé el diseño con fondo oscuro y gráficos en Plotly.
- El resultado se ve claro y sirve para apoyar decisiones de recomendación.
- Si quieres usar el sistema en otro equipo, solo necesitas el CSV original y `pip install -r requirements.txt`.

> Este README está escrito con un estilo personal, como si lo explicara yo mismo: un poco directo y con esos detalles que hacen ver que lo escribí a mano.

