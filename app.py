from flask import Flask, request, jsonify, send_file
import sqlite3
import os

app = Flask(__name__)

# Función para conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect('dnd_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear las tablas en la base de datos si no existen
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        attributes TEXT,
        skills TEXT,
        description TEXT
    );
    CREATE TABLE IF NOT EXISTS lore (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        tags TEXT
    );
    CREATE TABLE IF NOT EXISTS villains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        threat_level TEXT
    );
    CREATE TABLE IF NOT EXISTS npcs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT,
        details TEXT
    );
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        coordinates TEXT
    );
    CREATE TABLE IF NOT EXISTS factions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ideology TEXT,
        influence_level TEXT
    );
    CREATE TABLE IF NOT EXISTS romances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        partner_name TEXT,
        relationship_details TEXT,
        FOREIGN KEY (character_id) REFERENCES characters (id)
    );
    """)
    conn.commit()
    conn.close()

# Endpoint para almacenar un personaje
@app.route('/store_character', methods=['POST'])
def store_character():
    data = request.json
    try:
        name = data.get('name')
        type_ = data.get('type')
        attributes = data.get('attributes', {})
        skills = data.get('skills', [])
        description = data.get('description', '')

        # Serializar los atributos y habilidades
        attributes_str = ';'.join(f"{k}:{v}" for k, v in attributes.items())
        skills_str = ','.join(skills)

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO characters (name, type, attributes, skills, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, type_, attributes_str, skills_str, description)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Character stored successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para recuperar todos los personajes
@app.route('/retrieve_characters', methods=['GET'])
def retrieve_characters():
    try:
        conn = get_db_connection()
        characters = conn.execute("SELECT * FROM characters").fetchall()
        conn.close()

        result = []
        for char in characters:
            attributes = dict(item.split(':') for item in char['attributes'].split(';') if item)
            skills = char['skills'].split(',') if char['skills'] else []
            result.append({
                "id": char['id'],
                "name": char['name'],
                "type": char['type'],
                "attributes": attributes,
                "skills": skills,
                "description": char['description']
            })

        return jsonify({"characters": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para descargar la base de datos
@app.route('/download_db', methods=['GET'])
def download_db():
    return send_file('dnd_data.db', as_attachment=True)

# Ruta de inicio
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the D&D Plugin API!"})

# Crear tablas al inicio
if __name__ == '__main__':
    create_tables()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
