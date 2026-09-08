-- ============================================
-- SQL Analysis: Bengaluru Real Estate Dataset
-- ============================================

USE real_estate_db;

-- 1. Average price by location (top 15 by count, to avoid noise from rare locations)
SELECT location, 
       COUNT(*) AS num_properties, 
       ROUND(AVG(price), 2) AS avg_price_lakhs
FROM properties
GROUP BY location
HAVING COUNT(*) >= 10
ORDER BY avg_price_lakhs DESC
LIMIT 15;

-- 2. Average price per sqft by BHK
SELECT bhk,
       ROUND(AVG(price * 100000 / total_sqft), 2) AS avg_price_per_sqft
FROM properties
WHERE total_sqft > 0
GROUP BY bhk
ORDER BY bhk;

-- 3. Top 10 most expensive localities (by average price, min 5 listings)
SELECT location,
       COUNT(*) AS num_properties,
       ROUND(AVG(price), 2) AS avg_price_lakhs,
       ROUND(AVG(price * 100000 / total_sqft), 2) AS avg_price_per_sqft
FROM properties
GROUP BY location
HAVING COUNT(*) >= 5
ORDER BY avg_price_lakhs DESC
LIMIT 10;

-- 4. Locations with unusually high price-per-sqft (HAVING clause)
SELECT location,
       ROUND(AVG(price * 100000 / total_sqft), 2) AS avg_price_per_sqft,
       COUNT(*) AS num_properties
FROM properties
GROUP BY location
HAVING avg_price_per_sqft > 8000 AND COUNT(*) >= 5
ORDER BY avg_price_per_sqft DESC;

-- 5. Rank localities by average price using a window function
SELECT location,
       avg_price_lakhs,
       RANK() OVER (ORDER BY avg_price_lakhs DESC) AS price_rank
FROM (
    SELECT location, ROUND(AVG(price), 2) AS avg_price_lakhs
    FROM properties
    GROUP BY location
    HAVING COUNT(*) >= 5
) AS location_avg
LIMIT 20;

-- 6. Distribution of BHK types (how many 1BHK, 2BHK, 3BHK etc. exist)
SELECT bhk, COUNT(*) AS count
FROM properties
GROUP BY bhk
ORDER BY bhk;