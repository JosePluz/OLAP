import pathlib 
import sqlite3 
import sys 
import zipfile 

import pandas as pd 

try :
    import kagglehub 
except ImportError :
    kagglehub =None 

DATA_DIR =pathlib .Path ("data")
DATA_DIR .mkdir (exist_ok =True )
CSV_CANDIDATES =["top_anime_2024.csv","top_anime.csv","anime.csv"]
DB_PATH =DATA_DIR /"anime.db"
SQL_PATH =pathlib .Path ("anime_queries.sql")


def find_csv ():
    for name in CSV_CANDIDATES :
        candidate =DATA_DIR /name 
        if candidate .exists ():
            return candidate 
        candidate =pathlib .Path (name )
        if candidate .exists ():
            return candidate 
    csv_files =sorted (DATA_DIR .glob ("*.csv"))
    return csv_files [0 ]if csv_files else None 


def load_csv_to_dataframe (csv_path ):
    df =pd .read_csv (csv_path )
    available_cols ={col .lower ():col for col in df .columns }

    name_col =next ((available_cols [c ]for c in ["name","title","anime_name","anime"]if c in available_cols ),None )
    rating_col =next ((available_cols [c ]for c in ["rating","score","avg_rating","ratings"]if c in available_cols ),None )
    review_col =next ((available_cols [c ]for c in ["rating_count","reviews","members","votes"]if c in available_cols ),None )
    genre_col =next ((available_cols [c ]for c in ["genre","genres"]if c in available_cols ),None )

    if name_col is None or rating_col is None :
        raise ValueError ("El CSV no contiene columnas válidas para anime y rating.")

    if review_col is None and "members"in available_cols :
        review_col =available_cols ["members"]
    if review_col is None :
        raise ValueError ("El CSV no contiene columnas válidas para reseñas / members.")

    selected =[name_col ,rating_col ,review_col ]
    if genre_col :
        selected .append (genre_col )

    clean_df =df [selected ].copy ()
    rename_map ={name_col :"anime",rating_col :"rating",review_col :"reviews"}
    if genre_col :
        rename_map [genre_col ]="genre"
    clean_df =clean_df .rename (columns =rename_map )

    clean_df ["anime"]=clean_df ["anime"].astype (str )
    clean_df ["rating"]=pd .to_numeric (clean_df ["rating"],errors ="coerce")
    clean_df ["reviews"]=pd .to_numeric (clean_df ["reviews"],errors ="coerce")
    clean_df =clean_df .dropna (subset =["anime","rating"])
    clean_df ["reviews"]=clean_df ["reviews"].fillna (0 ).astype (int )

    return clean_df 


def create_sqlite_db (csv_path ):
    df =load_csv_to_dataframe (csv_path )
    with sqlite3 .connect (DB_PATH )as conn :
        df .to_sql ("anime",conn ,if_exists ="replace",index =False )
    print (f"Base creada en: {DB_PATH }")


def read_sql_file ():
    if not SQL_PATH .exists ():
        raise FileNotFoundError (f"No se encontró el archivo SQL: {SQL_PATH }")
    return SQL_PATH .read_text (encoding ="utf-8")


def download_dataset ():
    if kagglehub is None :
        return None 

    try :
        downloaded =pathlib .Path (kagglehub .dataset_download ("bhavyadhingra00020/top-anime-dataset-2024"))
        if not downloaded .exists ():
            return None 

        if downloaded .suffix ==".zip":
            with zipfile .ZipFile (downloaded ,"r")as archive :
                archive .extractall (DATA_DIR )
            return find_csv ()

        if downloaded .suffix ==".csv":
            destination =DATA_DIR /downloaded .name 
            if downloaded .parent !=DATA_DIR :
                downloaded .replace (destination )
            return destination 

        return find_csv ()
    except Exception as exc :
        print ("No se pudo descargar el dataset automáticamente:",exc )
        return None 


def load_queries ():
    sql_text =read_sql_file ()
    return [stmt .strip ()for stmt in sql_text .split (";")if stmt .strip ()]


def execute_sql_statements (statements ,selected_indexes =None ):
    with sqlite3 .connect (DB_PATH )as conn :
        for i ,statement in enumerate (statements ,start =1 ):
            if selected_indexes and i not in selected_indexes :
                continue 
            print (f"\n--- Ejecutando consulta {i } ---")
            if statement .upper ().startswith ("SELECT"):
                df =pd .read_sql_query (statement ,conn )
                print (df .head (20 ).to_string (index =False ))
            else :
                conn .execute (statement )
                conn .commit ()
                print ("Consulta ejecutada:",statement )


def parse_query_selection (arg ,max_index ):
    names ={
    "top_reviews":1 ,
    "mejor_rating":2 ,
    "mas_reseñas":3 ,
    "mas_reseñas":3 ,
    "combinado":4 ,
    "filtro_genero":5 ,
    }
    if arg .isdigit ():
        selection =int (arg )
        if 1 <=selection <=max_index :
            return {selection }
    return {names .get (arg .lower (),0 )}if names .get (arg .lower ())else None 


if __name__ =="__main__":
    csv_path =find_csv ()
    if csv_path is None :
        csv_path =download_dataset ()

    if csv_path is None :
        raise FileNotFoundError (
        "No se encontró el CSV del dataset. Coloca `top_anime_2024.csv`, `top_anime.csv` o `anime.csv` en la carpeta data/ o en la raíz."
        )

    create_sqlite_db (csv_path )
    statements =load_queries ()

    selected_indexes =None 
    if len (sys .argv )>1 :
        selected_indexes =parse_query_selection (sys .argv [1 ],len (statements ))
        if selected_indexes is None :
            print ("Argumento no válido. Usa un número de consulta o nombre como top_reviews, mejor_rating, mas_reseñas, combinado, filtro_genero.")
            sys .exit (1 )

    execute_sql_statements (statements ,selected_indexes )
