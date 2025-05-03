from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('dnd_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/store_character', methods=['POST'])
def store_character():
    data = request.json
    name = data.get('name')
    type_ = data.get('type')
    attributes = data.get('attributes', {})
    skills = data.get('skills', [])
    description = data.get('description', '')

    # Serialize attributes and skills
    attributes_str = ';'.join(f"{k}:{v}" for k, v in attributes.items())
    skills_str = ','.join(skills)

    try:
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

# Similar adjustments for other endpoints (e.g., lores, villains, etc.)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
