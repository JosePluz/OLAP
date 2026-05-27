-- anime_queries.sql
-- Consultas SQL para usar con el dataset de anime.

-- Top 12 de animes ordenados por cantidad de reseñas.
SELECT anime, rating, reviews
FROM anime
ORDER BY reviews DESC
LIMIT 12;

-- Top 5 de animes con mejor rating.
SELECT anime, rating, reviews
FROM anime
ORDER BY rating DESC, reviews DESC
LIMIT 5;

-- Top 5 de animes con más reseñas.
SELECT anime, rating, reviews
FROM anime
ORDER BY reviews DESC, rating DESC
LIMIT 5;

-- Recomendación combinada: rating alto y muchas reseñas.
SELECT anime, rating, reviews
FROM anime
ORDER BY rating DESC, reviews DESC
LIMIT 5;

-- Ejemplo de filtro por género (reemplaza 'Action' por el género que quieras).
SELECT anime, rating, reviews, genre
FROM anime
WHERE genre LIKE '%Action%'
ORDER BY reviews DESC
LIMIT 10;
