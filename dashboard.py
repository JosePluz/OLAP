

import sqlite3 
import pathlib 
from datetime import datetime 
import pandas as pd 
import plotly .express as px 
import plotly .graph_objects as go 
import streamlit as st 




st .set_page_config (
page_title ="OLAP - Anime & Manga Analytics",
page_icon ="",
layout ="wide",
initial_sidebar_state ="expanded"
)


st .markdown ("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        color: #ecf0f1;
    }
    .stApp {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
        font-weight: 700;
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 20px;
        color: #ecf0f1;
    }
    </style>
""",unsafe_allow_html =True )


DATA_DIR =pathlib .Path ("data")
DB_PATH =DATA_DIR /"olap.db"





@st .cache_resource 
def get_db_connection ():

    return sqlite3 .connect (DB_PATH ,check_same_thread =False )

def execute_query (query :str ,params =None ):

    try :
        conn =get_db_connection ()
        if params :
            df =pd .read_sql_query (query ,conn ,params =params )
        else :
            df =pd .read_sql_query (query ,conn )
        return df 
    except Exception as e :
        st .error (f"Error en consulta SQL: {e }")
        return None 

def create_genre_lists (df ):

    genres =set ()
    for genre_str in df ['genres'].dropna ():
        if pd .notna (genre_str ):
            genre_list =str (genre_str ).split (',')
            genres .update ([g .strip ()for g in genre_list if g .strip ()])
    return sorted (list (genres ))





st .title (" OLAP - Anime & Manga Analytics")
st .markdown ("**Sistema de toma de decisiones basado en datos de MyAnimeList**")
st .markdown ("---")


with st .sidebar :
    st .markdown ("###  Opciones del Dashboard")

    media_type =st .radio (
    "Selecciona tipo de media:",
    ["Anime","Manga","Combinado"],
    help ="Elige entre análisis de anime, manga o ambos"
    )

    st .markdown ("---")
    st .markdown ("### ℹ️ Información")
    st .info ("""
    Este dashboard proporciona:
    - 5 análisis predefinidos con visualizaciones
    - Consultas SQL personalizadas
    - Soporte para toma de decisiones
    """)





st .markdown ("##  Análisis Predefinidos")


tab1 ,tab2 ,tab3 ,tab4 ,tab5 =st .tabs ([
" Top Rated",
" Géneros Populares",
" Tendencia Temporal",
" Popularidad",
" Distribución de Tipos"
])




with tab1 :
    st .markdown ("###  Top 20 por Puntuación")

    if media_type =="Anime":
        query ="""
        SELECT title, score, scored_by, type, year, genres
        FROM anime
        WHERE score IS NOT NULL AND score > 0
        ORDER BY score DESC, scored_by DESC
        LIMIT 20
        """
    elif media_type =="Manga":
        query ="""
        SELECT title, score, scored_by, type, year, genres
        FROM manga
        WHERE score IS NOT NULL AND score > 0
        ORDER BY score DESC, scored_by DESC
        LIMIT 20
        """
    else :
        query ="""
        SELECT title, score, scored_by, type, year, 'anime' as media_type, genres
        FROM anime
        WHERE score IS NOT NULL AND score > 0
        UNION ALL
        SELECT title, score, scored_by, type, year, 'manga' as media_type, genres
        FROM manga
        WHERE score IS NOT NULL AND score > 0
        ORDER BY score DESC, scored_by DESC
        LIMIT 20
        """

    df_top =execute_query (query )

    if df_top is not None and len (df_top )>0 :

        fig =px .bar (
        df_top [::-1 ],
        x ="score",
        y ="title",
        orientation ="h",
        color ="score",
        color_continuous_scale ="Viridis",
        labels ={"title":"Título","score":"Puntuación"},
        height =600 
        )
        fig .update_layout (
        plot_bgcolor ="rgba(0,0,0,0)",
        paper_bgcolor ="rgba(15,52,96,0.3)",
        font_color ="#e0e0e0",
        showlegend =False 
        )
        st .plotly_chart (fig ,width ="stretch")


        col1 ,col2 =st .columns (2 )
        with col1 :
            st .metric ("Máxima puntuación",f"{df_top ['score'].max ():.2f}")
        with col2 :
            st .metric ("Promedio de puntuación",f"{df_top ['score'].mean ():.2f}")

        st .dataframe (df_top [['title','score','scored_by','type','year']],width ="stretch")




with tab2 :
    st .markdown ("###  Distribución de Géneros")

    if media_type =="Anime":
        query ="SELECT genres, COUNT(*) as count, AVG(score) as avg_score FROM anime GROUP BY genres ORDER BY count DESC LIMIT 15"
    elif media_type =="Manga":
        query ="SELECT genres, COUNT(*) as count, AVG(score) as avg_score FROM manga GROUP BY genres ORDER BY count DESC LIMIT 15"
    else :
        query ="""
        SELECT genres, COUNT(*) as count, AVG(score) as avg_score 
        FROM (
            SELECT genres, score FROM anime
            UNION ALL
            SELECT genres, score FROM manga
        ) 
        GROUP BY genres ORDER BY count DESC LIMIT 15
        """

    df_genres =execute_query (query )

    if df_genres is not None and len (df_genres )>0 :

        df_genres_clean =df_genres .head (10 ).copy ()

        fig =px .bar (
        df_genres_clean ,
        x ="count",
        y ="genres",
        orientation ="h",
        color ="avg_score",
        color_continuous_scale ="RdYlGn",
        labels ={"genres":"Género","count":"Cantidad","avg_score":"Puntuación Promedio"},
        height =500 
        )
        fig .update_layout (
        plot_bgcolor ="rgba(0,0,0,0)",
        paper_bgcolor ="rgba(15,52,96,0.3)",
        font_color ="#e0e0e0"
        )
        st .plotly_chart (fig ,width ="stretch")

        col1 ,col2 ,col3 =st .columns (3 )
        with col1 :
            st .metric ("Total de géneros",len (df_genres ))
        with col2 :
            top_genre =str (df_genres .iloc [0 ]['genres'])[:30 ]if df_genres .iloc [0 ]['genres']else "N/A"
            st .metric ("Género más frecuente",top_genre )
        with col3 :
            st .metric ("Mejor puntuación promedio",f"{df_genres ['avg_score'].max ():.2f}")




with tab3 :
    st .markdown ("###  Tendencia por Año")

    if media_type =="Anime":
        query ="""
        SELECT year, COUNT(*) as cantidad, AVG(score) as avg_score
        FROM anime
        WHERE year >= 2000 AND year IS NOT NULL
        GROUP BY year
        ORDER BY year
        """
    elif media_type =="Manga":
        query ="""
        SELECT year, COUNT(*) as cantidad, AVG(score) as avg_score
        FROM manga
        WHERE year >= 2000 AND year IS NOT NULL
        GROUP BY year
        ORDER BY year
        """
    else :
        query ="""
        SELECT year, COUNT(*) as cantidad, AVG(score) as avg_score
        FROM (
            SELECT year, score FROM anime WHERE year >= 2000 AND year IS NOT NULL
            UNION ALL
            SELECT year, score FROM manga WHERE year >= 2000 AND year IS NOT NULL
        )
        GROUP BY year
        ORDER BY year
        """

    df_timeline =execute_query (query )

    if df_timeline is not None and len (df_timeline )>0 :

        fig =go .Figure ()

        fig .add_trace (go .Scatter (
        x =df_timeline ['year'],
        y =df_timeline ['cantidad'],
        mode ='lines',
        name ='Cantidad',
        line =dict (color ='#00bcd4',width =3 ),
        fill ='tozeroy'
        ))

        fig .update_layout (
        title ="Evolución de cantidad vs puntuación promedio",
        xaxis_title ="Año",
        yaxis_title ="Cantidad",
        plot_bgcolor ="rgba(0,0,0,0)",
        paper_bgcolor ="rgba(15,52,96,0.3)",
        font_color ="#e0e0e0",
        height =500 ,
        hovermode ='x unified'
        )

        st .plotly_chart (fig ,width ="stretch")

        col1 ,col2 ,col3 =st .columns (3 )
        with col1 :
            st .metric ("Año con más registros",int (df_timeline .loc [df_timeline ['cantidad'].idxmax (),'year']))
        with col2 :
            st .metric ("Año actual (datos más recientes)",int (df_timeline ['year'].max ()))
        with col3 :
            st .metric ("Promedio general de puntuación",f"{df_timeline ['avg_score'].mean ():.2f}")




with tab4 :
    st .markdown ("###  Análisis de Popularidad vs Puntuación")

    if media_type =="Anime":
        query ="""
        SELECT title, members, score, type, genres
        FROM anime
        WHERE members > 0 AND score IS NOT NULL AND score > 0
        ORDER BY members DESC
        LIMIT 100
        """
    elif media_type =="Manga":
        query ="""
        SELECT title, members, score, type, genres
        FROM manga
        WHERE members > 0 AND score IS NOT NULL AND score > 0
        ORDER BY members DESC
        LIMIT 100
        """
    else :
        query ="""
        SELECT title, members, score, type, genres
        FROM anime
        WHERE members > 0 AND score IS NOT NULL AND score > 0
        UNION ALL
        SELECT title, members, score, type, genres
        FROM manga
        WHERE members > 0 AND score IS NOT NULL AND score > 0
        ORDER BY members DESC
        LIMIT 100
        """

    df_popularity =execute_query (query )

    if df_popularity is not None and len (df_popularity )>0 :

        fig =px .scatter (
        df_popularity ,
        x ="members",
        y ="score",
        size ="score",
        color ="score",
        hover_name ="title",
        hover_data ={'members':':,','score':':.2f','type':True },
        color_continuous_scale ="Plasma",
        labels ={"members":"Miembros","score":"Puntuación"},
        height =500 ,
        log_x =True 
        )
        fig .update_layout (
        plot_bgcolor ="rgba(0,0,0,0.2)",
        paper_bgcolor ="rgba(15,52,96,0.3)",
        font_color ="#e0e0e0"
        )
        st .plotly_chart (fig ,width ="stretch")

        col1 ,col2 ,col3 =st .columns (3 )
        with col1 :
            st .metric ("Mayor número de miembros",f"{df_popularity ['members'].max ():,}")
        with col2 :
            st .metric ("Correlación Members-Score",f"{df_popularity ['members'].corr (df_popularity ['score']):.3f}")
        with col3 :
            st .metric ("Media de miembros",f"{df_popularity ['members'].mean ():,.0f}")




with tab5 :
    st .markdown ("###  Distribución de Tipos/Formatos")

    if media_type =="Anime":
        query ="""
        SELECT type, COUNT(*) as cantidad, AVG(score) as avg_score, AVG(members) as avg_members
        FROM anime
        GROUP BY type
        ORDER BY cantidad DESC
        """
    elif media_type =="Manga":
        query ="""
        SELECT type, COUNT(*) as cantidad, AVG(score) as avg_score, AVG(members) as avg_members
        FROM manga
        GROUP BY type
        ORDER BY cantidad DESC
        """
    else :
        query ="""
        SELECT type, COUNT(*) as cantidad, AVG(score) as avg_score, AVG(members) as avg_members
        FROM (
            SELECT type, score, members FROM anime
            UNION ALL
            SELECT type, score, members FROM manga
        )
        GROUP BY type
        ORDER BY cantidad DESC
        """

    df_types =execute_query (query )

    if df_types is not None and len (df_types )>0 :
        col1 ,col2 =st .columns (2 )

        with col1 :
            fig =px .pie (
            df_types ,
            values ="cantidad",
            names ="type",
            title ="Distribución por Tipo",
            color_discrete_sequence =px .colors .sequential .RdBu 
            )
            fig .update_layout (
            paper_bgcolor ="rgba(15,52,96,0.3)",
            font_color ="#e0e0e0"
            )
            st .plotly_chart (fig ,width ="stretch")

        with col2 :
            fig =px .bar (
            df_types ,
            x ="type",
            y ="avg_score",
            color ="avg_members",
            title ="Puntuación Promedio por Tipo",
            color_continuous_scale ="Viridis"
            )
            fig .update_layout (
            plot_bgcolor ="rgba(0,0,0,0)",
            paper_bgcolor ="rgba(15,52,96,0.3)",
            font_color ="#e0e0e0"
            )
            st .plotly_chart (fig ,width ="stretch")

        st .dataframe (df_types ,width ="stretch")





st .markdown ("---")
st .markdown ("##  Constructor de Consultas Personalizadas")
st .markdown ("**Crea tu propia consulta SQL para análisis específicos**")


tab_query_builder ,tab_advanced =st .tabs (["Constructor Amigable","SQL Avanzado"])

with tab_query_builder :
    st .markdown ("###  Constructor Visual de Consultas")

    col1 ,col2 ,col3 =st .columns (3 )

    with col1 :
        query_media =st .selectbox (
        "1️⃣ Selecciona la fuente de datos:",
        ["Anime","Manga","Combinado"]
        )

    with col2 :
        if query_media =="Anime":
            available_cols =['title','type','episodes','score','scored_by','rank','popularity','members','year','genres','studios']
        elif query_media =="Manga":
            available_cols =['title','type','chapters','volumes','score','scored_by','rank','popularity','members','year','genres']
        else :
            available_cols =['title','type','score','scored_by','rank','popularity','members','year','genres']

        selected_cols =st .multiselect (
        "2️⃣ Selecciona columnas a mostrar:",
        available_cols ,
        default =['title','score']
        )

    with col3 :
        sort_by =st .selectbox (
        "3️⃣ Ordenar por:",
        available_cols ,
        index =3 
        )


    st .markdown ("#### Filtros (Opcional)")
    col1 ,col2 ,col3 =st .columns (3 )

    with col1 :
        min_score =st .slider ("Puntuación mínima:",0.0 ,10.0 ,0.0 )

    with col2 :
        min_members =st .slider ("Miembros mínimos:",0 ,100000 ,0 ,step =1000 )

    with col3 :
        limit =st .number_input ("Cantidad de resultados:",1 ,1000 ,20 )


    if 'genres'in selected_cols or query_media in ['Anime','Manga']:
        st .markdown ("#### Filtro por Género (Opcional)")


        if query_media =="Anime":
            genres_query ="SELECT DISTINCT genres FROM anime"
        elif query_media =="Manga":
            genres_query ="SELECT DISTINCT genres FROM manga"
        else :
            genres_query ="SELECT DISTINCT genres FROM anime UNION SELECT DISTINCT genres FROM manga"

        genres_df =execute_query (genres_query )
        if genres_df is not None and len (genres_df )>0 :
            genre_options =[]
            for g in genres_df ['genres'].dropna ():
                if pd .notna (g ):
                    genre_options .extend ([x .strip ()for x in str (g ).split (',')if x .strip ()])
            genre_options =sorted (list (set (genre_options )))

            selected_genre =st .multiselect ("Selecciona géneros:",genre_options )
        else :
            selected_genre =[]
    else :
        selected_genre =[]


    if selected_cols :

        cols_str =", ".join (selected_cols )

        if query_media =="Anime":
            query_builder =f"SELECT {cols_str } FROM anime WHERE 1=1"
        elif query_media =="Manga":
            query_builder =f"SELECT {cols_str } FROM manga WHERE 1=1"
        else :
            query_builder =f"SELECT {cols_str } FROM (SELECT {cols_str } FROM anime UNION ALL SELECT {cols_str } FROM manga) WHERE 1=1"


        if min_score >0 :
            query_builder +=f" AND score >= {min_score }"
        if min_members >0 :
            query_builder +=f" AND members >= {min_members }"


        if selected_genre :
            genre_conditions =" OR ".join ([f"genres LIKE '%{g }%'"for g in selected_genre ])
            query_builder +=f" AND ({genre_conditions })"

        query_builder +=f" ORDER BY {sort_by } DESC LIMIT {limit }"

        if st .button (" Ejecutar Consulta",type ="primary"):
            df_custom =execute_query (query_builder )

            if df_custom is not None and len (df_custom )>0 :
                st .success (f" {len (df_custom )} resultados encontrados")


                st .dataframe (df_custom ,width ="stretch")


                st .markdown ("####  Visualizaciones Sugeridas")

                if 'score'in df_custom .columns and 'title'in df_custom .columns :
                    fig =px .bar (
                    df_custom .head (15 )[::-1 ],
                    x ="score",
                    y ="title",
                    orientation ="h",
                    color ="score",
                    color_continuous_scale ="Viridis",
                    height =400 
                    )
                    fig .update_layout (
                    plot_bgcolor ="rgba(0,0,0,0)",
                    paper_bgcolor ="rgba(15,52,96,0.3)",
                    font_color ="#e0e0e0"
                    )
                    st .plotly_chart (fig ,width ="stretch")
            else :
                st .warning ("️ No se encontraron resultados con los filtros especificados")
    else :
        st .warning ("️ Selecciona al menos una columna para mostrar")




with tab_advanced :
    st .markdown ("### ️ Editor SQL Avanzado")
    st .info ("""
    **Tablas disponibles:**
    - `anime` - Tabla principal de anime
    - `manga` - Tabla principal de manga
    
    **Columnas principales anime:** title, type, episodes, status, rating, score, scored_by, rank, popularity, members, year, genres, studios
    
    **Columnas principales manga:** title, type, chapters, volumes, status, score, scored_by, rank, popularity, members, year, genres, authors
    """)

    sql_query =st .text_area (
    "Escribe tu consulta SQL:",
    value ="SELECT title, score, members FROM anime ORDER BY score DESC LIMIT 10",
    height =150 
    )

    if st .button (" Ejecutar SQL",type ="primary"):
        df_sql =execute_query (sql_query )

        if df_sql is not None :
            st .success (f" Consulta ejecutada: {len (df_sql )} filas")
            st .dataframe (df_sql ,width ="stretch")


            with st .expander (" Estadísticas de columnas numéricas"):
                numeric_cols =df_sql .select_dtypes (include =['float64','int64']).columns 
                if len (numeric_cols )>0 :
                    st .write (df_sql [numeric_cols ].describe ())




st .markdown ("---")
st .markdown ("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>Dashboard OLAP v1.0 | Datos de MyAnimeList | Última actualización: 2026</p>
    <p>Desarrollado para análisis y toma de decisiones basada en datos</p>
</div>
""",unsafe_allow_html =True )
