

import pathlib 
import sqlite3 
import pandas as pd 

DATA_DIR =pathlib .Path ("data")
DB_PATH =DATA_DIR /"olap.db"

def setup_database ():



    print (" Cargando datasets...")
    anime_df =pd .read_csv (DATA_DIR /"anime_dataset.csv")
    manga_df =pd .read_csv (DATA_DIR /"manga_dataset.csv")


    anime_df =anime_df [[
    'mal_id','title','type','episodes','status','airing',
    'aired_from','aired_to','rating','score','scored_by','rank',
    'popularity','members','favorites','season','year','genres','studios'
    ]].copy ()

    anime_df ['aired_from']=pd .to_datetime (anime_df ['aired_from'],errors ='coerce')
    anime_df ['aired_to']=pd .to_datetime (anime_df ['aired_to'],errors ='coerce')
    anime_df ['year']=pd .to_numeric (anime_df ['year'],errors ='coerce')
    anime_df ['media_type']='anime'
    anime_df =anime_df .rename (columns ={'episodes':'quantity'})


    manga_df =manga_df [[
    'mal_id','title','type','chapters','volumes','status',
    'publishing','published_from','published_to','score','scored_by',
    'rank','popularity','members','favorites','genres','authors'
    ]].copy ()

    manga_df ['published_from']=pd .to_datetime (manga_df ['published_from'],errors ='coerce')
    manga_df ['published_to']=pd .to_datetime (manga_df ['published_to'],errors ='coerce')
    manga_df ['year']=manga_df ['published_from'].dt .year 
    manga_df ['media_type']='manga'
    manga_df =manga_df .rename (columns ={'chapters':'quantity'})


    print (" Creando base de datos SQLite...")
    conn =sqlite3 .connect (DB_PATH )


    anime_df .to_sql ('anime',conn ,if_exists ='replace',index =False )


    manga_df .to_sql ('manga',conn ,if_exists ='replace',index =False )


    conn .execute ("""
    CREATE VIEW IF NOT EXISTS media_combined AS
    SELECT 
        mal_id, title, type, score, scored_by, rank, popularity, 
        members, favorites, genres, 'anime' as media_type, year, quantity
    FROM anime
    UNION ALL
    SELECT 
        mal_id, title, type, score, scored_by, rank, popularity, 
        members, favorites, genres, 'manga' as media_type, year, quantity
    FROM manga
    """)


    conn .execute ("CREATE INDEX IF NOT EXISTS idx_anime_year ON anime(year)")
    conn .execute ("CREATE INDEX IF NOT EXISTS idx_anime_score ON anime(score DESC)")
    conn .execute ("CREATE INDEX IF NOT EXISTS idx_anime_popularity ON anime(popularity)")
    conn .execute ("CREATE INDEX IF NOT EXISTS idx_manga_year ON manga(year)")
    conn .execute ("CREATE INDEX IF NOT EXISTS idx_manga_score ON manga(score DESC)")

    conn .commit ()
    conn .close ()

    print (f" Base de datos creada en: {DB_PATH }")
    print (f"   - Anime: {len (anime_df )} registros")
    print (f"   - Manga: {len (manga_df )} registros")

if __name__ =="__main__":
    setup_database ()
