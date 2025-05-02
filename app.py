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

    # Tabla de mapas
    cursor.execute('''CREATE TABLE IF NOT EXISTS maps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        details TEXT)''')

    # Tabla de inventario
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        owner_id INTEGER,
                        FOREIGN KEY (owner_id) REFERENCES characters (id))''')

    conn.commit()
    conn.close()

# Ruta de inicio
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the D&D Plugin API!"})

# Guardar un personaje
@app.route('/store_character', methods=['POST'])
def store_character():
    content = request.json

    # Validar datos obligatorios
    if not content or not content.get("name"):
        return jsonify({"error": "El nombre del personaje es obligatorio."}), 400

    # Extraer y procesar datos
    name = content.get("name")
    race = content.get("race")
    character_class = content.get("class")
    level = content.get("level")
    background = content.get("background")
    alignment = content.get("alignment")
    hit_points = content.get("hit_points")
    equipment = content.get("equipment", [])
    notes = content.get("notes", "")

    attributes = json.dumps({
        "class": character_class,
        "level": level,
        "alignment": alignment,
        "hit_points": hit_points
    })
    skills = json.dumps(equipment)
    description = f"Background: {background}, Notes: {notes}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO characters (name, type, attributes, skills, description)
        VALUES (?, ?, ?, ?, ?)
    """, (name, race, attributes, skills, description))
    conn.commit()
    conn.close()

    return jsonify({"message": "Character stored successfully", "data": content}), 201

# Recuperar todos los personajes
@app.route('/retrieve_characters', methods=['GET'])
def retrieve_characters():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM characters")
    rows = cursor.fetchall()

    characters = []
    for row in rows:
        characters.append({
            "id": row["id"],
            "name": row["name"],
            "type": row["type"],
            "attributes": json.loads(row["attributes"]),
            "skills": json.loads(row["skills"]),
            "description": row["description"]
        })

    conn.close()
    return jsonify({"characters": characters}), 200

# Descargar la base de datos
@app.route('/download_db', methods=['GET'])
def download_db():
    return send_file('game_data.db', as_attachment=True)

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)
