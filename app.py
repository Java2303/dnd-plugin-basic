from flask import Flask, request, jsonify, send_file
import sqlite3
import json

app = Flask(__name__)

# Función para conectar a la base de datos
def get_db():
    conn = sqlite3.connect('game_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear las tablas en la base de datos si no existen
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    tables = {
        "characters": """
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                attributes TEXT,
                skills TEXT,
                description TEXT
            )
        """,
        "lore": """
            CREATE TABLE IF NOT EXISTS lore (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT
            )
        """,
        "villains": """
            CREATE TABLE IF NOT EXISTS villains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                threat_level TEXT
            )
        """,
        "npcs": """
            CREATE TABLE IF NOT EXISTS npcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT,
                details TEXT
            )
        """,
        "locations": """
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                coordinates TEXT
            )
        """,
        "factions": """
            CREATE TABLE IF NOT EXISTS factions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ideology TEXT,
                influence_level TEXT
            )
        """,
        "romances": """
            CREATE TABLE IF NOT EXISTS romances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER,
                partner_name TEXT,
                relationship_details TEXT,
                FOREIGN KEY (character_id) REFERENCES characters (id)
            )
        """,
    }

    for table_name, table_query in tables.items():
        cursor.execute(table_query)

    conn.commit()
    conn.close()

# Función para crear rutas genéricas de almacenamiento y recuperación
def create_store_and_retrieve_routes(table_name, singular_name):
    # Función para manejar la inserción de datos
    def store(content):
        conn = get_db()
        cursor = conn.cursor()
        columns = ", ".join(content.keys())
        placeholders = ", ".join(["?"] * len(content))
        values = tuple(content.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    # Función para manejar la recuperación de datos
    def retrieve():
        conn = get_db()
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # Definir la ruta para almacenar datos
    app.add_url_rule(
        f'/store_{singular_name}',
        view_func=lambda: (store(request.json), jsonify({"message": f"{singular_name.capitalize()} almacenado con éxito."}), 201),
        methods=['POST'],
        endpoint=f'store_{singular_name}'
    )

    # Definir la ruta para recuperar datos
    app.add_url_rule(
        f'/retrieve_{singular_name}',
        view_func=lambda: jsonify({f"{singular_name}s": retrieve()}),
        methods=['GET'],
        endpoint=f'retrieve_{singular_name}'
    )

# Crear rutas para cada tabla
entities = {
    "characters": "character",
    "lore": "lore",
    "villains": "villain",
    "npcs": "npc",
    "locations": "location",
    "factions": "faction",
    "romances": "romance",
}

for table, singular in entities.items():
    create_store_and_retrieve_routes(table, singular)

# Ruta para descargar la base de datos
@app.route('/download_db', methods=['GET'])
def download_db():
    return send_file('game_data.db', as_attachment=True)

# Ruta de inicio
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the D&D Plugin API!"})

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)
