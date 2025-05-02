from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Función para conectar a la base de datos
def get_db():
    conn = sqlite3.connect('game_data.db')  # Nombre del archivo de la base de datos
    conn.row_factory = sqlite3.Row
    return conn

# Crear las tablas necesarias en la base de datos
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    # Tabla de personajes
    cursor.execute('''CREATE TABLE IF NOT EXISTS characters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        race TEXT,
                        class TEXT,
                        level INTEGER,
                        background TEXT,
                        alignment TEXT,
                        abilities TEXT,
                        skills TEXT,
                        hit_points INTEGER,
                        equipment TEXT,
                        notes TEXT)''')

    # Tabla de historia
    cursor.execute('''CREATE TABLE IF NOT EXISTS lore (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT,
                        tags TEXT)''')

    # Tabla de villanos
    cursor.execute('''CREATE TABLE IF NOT EXISTS villains (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        race TEXT,
                        class TEXT,
                        power_level INTEGER,
                        description TEXT,
                        goals TEXT)''')

    # Tabla de lugares
    cursor.execute('''CREATE TABLE IF NOT EXISTS locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        importance TEXT)''')

    # Tabla de misiones
    cursor.execute('''CREATE TABLE IF NOT EXISTS quests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        reward TEXT,
                        status TEXT)''')

    conn.commit()
    conn.close()

# Ruta para almacenar personajes
@app.route('/store_character', methods=['POST'])
def store_character():
    content = request.json
    name = content.get("name")
    race = content.get("race")
    class_type = content.get("class")
    level = content.get("level")
    background = content.get("background")
    alignment = content.get("alignment")
    abilities = content.get("abilities")
    skills = content.get("skills")
    hit_points = content.get("hit_points")
    equipment = content.get("equipment")
    notes = content.get("notes")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO characters (name, race, class, level, background, alignment, abilities, skills, hit_points, equipment, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (name, race, class_type, level, background, alignment, str(abilities), str(skills), hit_points, str(equipment), notes))
    conn.commit()
    conn.close()

    return jsonify({"message": "Character stored successfully", "data": content}), 201

# Ruta para almacenar historia
@app.route('/store_lore', methods=['POST'])
def store_lore():
    content = request.json
    title = content.get("title")
    content_text = content.get("content")
    tags = content.get("tags")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lore (title, content, tags) VALUES (?, ?, ?)", (title, content_text, tags))
    conn.commit()
    conn.close()

    return jsonify({"message": "Lore stored successfully", "data": content}), 201

# Ruta para almacenar villanos
@app.route('/store_villain', methods=['POST'])
def store_villain():
    content = request.json
    name = content.get("name")
    race = content.get("race")
    class_type = content.get("class")
    power_level = content.get("power_level")
    description = content.get("description")
    goals = content.get("goals")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO villains (name, race, class, power_level, description, goals) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, race, class_type, power_level, description, goals))
    conn.commit()
    conn.close()

    return jsonify({"message": "Villain stored successfully", "data": content}), 201

# Ruta para almacenar lugares
@app.route('/store_location', methods=['POST'])
def store_location():
    content = request.json
    name = content.get("name")
    description = content.get("description")
    importance = content.get("importance")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO locations (name, description, importance) VALUES (?, ?, ?)", (name, description, importance))
    conn.commit()
    conn.close()

    return jsonify({"message": "Location stored successfully", "data": content}), 201

# Ruta para almacenar misiones
@app.route('/store_quest', methods=['POST'])
def store_quest():
    content = request.json
    title = content.get("title")
    description = content.get("description")
    reward = content.get("reward")
    status = content.get("status")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quests (title, description, reward, status) VALUES (?, ?, ?, ?)", (title, description, reward, status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Quest stored successfully", "data": content}), 201

if __name__ == '__main__':
    create_tables()  # Crear las tablas si no existen
    app.run(debug=True)
