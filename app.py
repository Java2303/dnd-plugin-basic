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
@app.route('/auto_save', methods=['POST'])
def auto_save():
    content = request.json

    # Validar que el tipo de datos esté presente
    data_type = content.get("type")
    data = content.get("data")  # Obtener los datos completos desde 'data'

    if not data_type or not data:
        return jsonify({"error": "Missing 'type' or 'data' in the request body."}), 400

    conn = get_db()
    cursor = conn.cursor()

    if data_type == "character":
        # Validar que los datos del personaje estén presentes
        name = data.get("name")  # Obtener el 'name' desde 'data'
        if not name:
            return jsonify({"error": "Character 'name' is required."}), 400

        # Obtener los otros atributos desde 'data'
        race = data.get("race", "")
        character_class = data.get("class", "")
        level = data.get("level", 1)
        alignment = data.get("alignment", "")
        hit_points = data.get("hit_points", 0)
        equipment = data.get("equipment", [])
        notes = data.get("notes", "")

        # Insertar el personaje en la base de datos
        cursor.execute("""
            INSERT INTO characters (name, type, attributes, skills, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            race,  # Usamos el campo 'race' como 'type' según tu código
            json.dumps({"class": character_class, "level": level, "alignment": alignment}),  # Atributos en formato JSON
            json.dumps(equipment),  # Equipos en formato JSON
            f"Notes: {notes}"  # Descripción del personaje
        ))
    elif data_type == "lore":
        # Validar que los datos del lore estén presentes
        title = data.get("title")  # Obtener el 'title' desde 'data'
        if not title:
            return jsonify({"error": "Lore 'title' is required."}), 400

        # Insertar el lore en la base de datos
        cursor.execute("""
            INSERT INTO lore (title, content, tags)
            VALUES (?, ?, ?)
        """, (
            title,
            data.get("content", ""),
            data.get("tags", "")
        ))
    else:
        return jsonify({"error": f"Unsupported type '{data_type}'."}), 400

    conn.commit()
    conn.close()

    return jsonify({"message": f"{data_type.capitalize()} saved successfully."}), 201


# Descargar la base de datos
@app.route('/download_db', methods=['GET'])
def download_db():
    return send_file('game_data.db', as_attachment=True)

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)
