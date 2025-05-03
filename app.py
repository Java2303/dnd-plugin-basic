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

    # Tabla de personajes
    cursor.execute('''CREATE TABLE IF NOT EXISTS characters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        type TEXT,
                        attributes TEXT,
                        skills TEXT,
                        description TEXT)''')

    # Tabla de lore
    cursor.execute('''CREATE TABLE IF NOT EXISTS lore (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT,
                        tags TEXT)''')

    # Tabla de villanos
    cursor.execute('''CREATE TABLE IF NOT EXISTS villains (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        motivations TEXT,
                        abilities TEXT,
                        description TEXT)''')

    # Tabla de NPCs
    cursor.execute('''CREATE TABLE IF NOT EXISTS npcs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        role TEXT,
                        attributes TEXT,
                        notes TEXT)''')

    # Tabla de historia
    cursor.execute('''CREATE TABLE IF NOT EXISTS story (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        details TEXT,
                        outcomes TEXT)''')

    # Tabla de romances
    cursor.execute('''CREATE TABLE IF NOT EXISTS romances (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        character1 TEXT NOT NULL,
                        character2 TEXT NOT NULL,
                        description TEXT)''')

    # Tabla de facciones
    cursor.execute('''CREATE TABLE IF NOT EXISTS factions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        members TEXT,
                        objectives TEXT,
                        description TEXT)''')

    # Tabla de locaciones
    cursor.execute('''CREATE TABLE IF NOT EXISTS locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        details TEXT,
                        tags TEXT)''')

    conn.commit()
    conn.close()

# Ruta de inicio
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the D&D Plugin API!"})

# Plantilla para rutas de guardar y recuperar
def create_store_and_retrieve_routes(table_name, singular_name):
    # Ruta para almacenar un recurso
    @app.route(f'/store_{singular_name}', methods=['POST'], endpoint=f'store_{singular_name}')
    def store():
        content = request.json
        if not content or not content.get("name"):
            return jsonify({"error": "El nombre es obligatorio."}), 400

        conn = get_db()
        cursor = conn.cursor()
        columns = ", ".join(content.keys())
        placeholders = ", ".join(["?"] * len(content))
        values = tuple(content.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return jsonify({"message": f"{singular_name.capitalize()} almacenado con éxito."}), 201

    # Ruta para recuperar todos los recursos
    @app.route(f'/retrieve_{singular_name}', methods=['GET'], endpoint=f'retrieve_{singular_name}')
    def retrieve():
        conn = get_db()
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        results = [dict(row) for row in rows]
        conn.close()

        return jsonify({f"{singular_name}s": results}), 200

    return store, retrieve


# Generar rutas dinámicamente
entities = [
    ("characters", "character"),
    ("lore", "lore"),
    ("villains", "villain"),
    ("npcs", "npc"),
    ("story", "story"),
    ("romances", "romance"),
    ("factions", "faction"),
    ("locations", "location"),
]

for table, singular in entities:
    store_route, retrieve_route = create_store_and_retrieve_routes(table, singular)
    app.add_url_rule(f'/store_{singular}', view_func=store_route, methods=['POST'])
    app.add_url_rule(f'/retrieve_{singular}s', view_func=retrieve_route, methods=['GET'])

# Descargar la base de datos
@app.route('/download_db', methods=['GET'])
def download_db():
    return send_file('game_data.db', as_attachment=True)

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)
