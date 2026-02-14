-- Tabelle für Tankstellen (Masterdaten)
CREATE TABLE IF NOT EXISTS tankstellen (
    id VARCHAR(50) PRIMARY KEY,      -- UUID der Tankstelle (z. B. "474e5046-deaf-4f9b-9a32-9797b778f047")
    name VARCHAR(255) NOT NULL,      -- Name der Tankstelle
    brand VARCHAR(100),              -- Marke (z. B. "TOTAL")
    street VARCHAR(255),            -- Straße
    house_number VARCHAR(20),        -- Hausnummer
    post_code VARCHAR(10),           -- PLZ
    place VARCHAR(100),              -- Ort
    lat DECIMAL(10, 6),               -- Geographische Breite
    lng DECIMAL(10, 6)               -- Geographische Länge
);

-- Tabelle für Abfragen
CREATE TABLE IF NOT EXISTS abfragen (
    id SERIAL PRIMARY KEY,
    tankstelle_id VARCHAR(50) REFERENCES tankstellen(id),  -- Fremdschlüssel zu tankstellen.id
    diesel DECIMAL(5, 3),             -- Preis für Diesel
    e5 DECIMAL(5, 3),                 -- Preis für E5
    e10 DECIMAL(5, 3),                -- Preis für E10
    is_open BOOLEAN,                  -- Status (offen/geschlossen)
    dist DECIMAL(10, 2),              -- Entfernung zum Suchstandort
    retrieval_time VARCHAR(5),       -- Uhrzeit der Abfrage (z. B. "14:30")
    retrieval_date DATE,              -- Datum der Abfrage (z. B. "2024-06-10")
);