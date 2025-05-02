from flask import Flask, request, jsonify
import sqlite3
import json

app = Flask(__name__)

# Función para conectar a la base de datos
def get_db():
    conn = sqlite3.connect('game_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla en la base de datos si no existe
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

# Guardar datos genéricos
@app.route('/store', methods=['GET', 'POST'])
def store_data():
    if request.method == 'GET':
        return jsonify({"message": "This endpoint requires a POST request with JSON data."}), 405
    
    content = request.json
    key = content.get("key")
    value = content.get("value")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lore (title, content, tags) VALUES (?, ?, ?)", (key, value, ""))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data stored successfully", "data": content}), 201

# Recuperar todos los datos
@app.route('/retrieve', methods=['GET'])
def retrieve_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lore")
    rows = cursor.fetchall()
    data = [{"id": row["id"], "title": row["title"], "content": row["content"], "tags": row["tags"]} for row in rows]
    conn.close()
    return jsonify(data), 200

# Limpiar todos los datos de la base de datos
@app.route('/clear', methods=['POST'])
def clear_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lore")
    conn.commit()
    conn.close()
    return jsonify({"message": "Data cleared successfully"}), 200

# Guardar un personaje
@app.route('/store_character', methods=['POST'])
def store_character():
    content = request.json

    # Extraer los datos enviados
    name = content.get("name")
    race = content.get("race")
    character_class = content.get("class")
    level = content.get("level")
    background = content.get("background")
    alignment = content.get("alignment")
    hit_points = content.get("hit_points")
    equipment = content.get("equipment", [])
    notes = content.get("notes", "")

    # Crear el diccionario de atributos
    attributes = {
        "class": character_class,
        "level": level,
        "alignment": alignment
    }
    
    # Convertir los atributos a JSON
    attributes_json = json.dumps(attributes)

    # Conexión a la base de datos
    conn = get_db()
    cursor = conn.cursor()

    # Insertar en la base de datos
    cursor.execute(""" 
        INSERT INTO characters 
        (name, type, attributes, skills, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,  # name
        race,  # type (puedes cambiar el nombre de este campo en la tabla)
        attributes_json,  # attributes como JSON
        json.dumps(equipment),  # skills como JSON
        f"Background: {background}, Notes: {notes}"  # description
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Character stored successfully",
        "data": content
    }), 201

@app.route('/download_db', methods=['GET'])
def download_db():
    from flask import send_file
    return send_file('game_data.db', as_attachment=True)

# Recuperar todos los personajes
@app.route('/retrieve_characters', methods=['GET'])
def retrieve_characters():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM characters")
    rows = cursor.fetchall()

    characters = []
    for row in rows:
        # Convertir los atributos de JSON a un diccionario
        attributes = json.loads(row["attributes"]) if row["attributes"] else {}
        
        # Convertir las habilidades de JSON a lista
        skills = json.loads(row["skills"]) if row["skills"] else []

        character = {
            "id": row["id"],
            "name": row["name"],
            "type": row["type"],
            "attributes": attributes,  # atributos como diccionario
            "skills": skills,  # habilidades como lista
            "description": row["description"]
        }
        characters.append(character)

    conn.close()

    return jsonify({"characters": characters}), 200

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)
