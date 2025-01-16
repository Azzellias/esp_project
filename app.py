from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Configuration des logs SQLAlchemy pour débogage (désactiver pour production)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de la base de données PostgreSQL
db_url = os.getenv(
    'DATABASE_URL', 
    'postgresql://esp_data_yshz_user:LUcBbnKHk4OKyBXgfz2YKgvTST1lZOoa@dpg-cu3tdl23esus73fhc0n0-a.oregon-postgres.render.com/esp_data_yshz?sslmode=require'
)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)

# Modèle pour la table de données
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    timestamp = db.Column(db.String(100))

# Créer la table si elle n'existe pas encore
with app.app_context():
    db.create_all()

# Route pour afficher les données en temps réel
@app.route('/')
def index():
    try:
        # Récupérer les dernières données
        data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
        if not data:
            data = SensorData(temperature=None, humidity=None, timestamp="No data available")
    except Exception as e:
        data = SensorData(temperature=None, humidity=None, timestamp=f"Error: {e}")
    return render_template('index.html', data=data)

# Route pour fournir les données au format JSON pour l'API
@app.route('/data')
def get_data():
    try:
        # Récupérer les dernières données
        data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
        if not data:
            return jsonify({'message': 'No data available'}), 404
        return jsonify({
            'temperature': data.temperature,
            'humidity': data.humidity,
            'timestamp': data.timestamp
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour recevoir les données envoyées depuis le serveur local
@app.route('/updateData', methods=['POST'])
def update_data():
    try:
        # Lire les données JSON envoyées
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extraire les valeurs de la requête JSON
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        timestamp = data.get("timestamp")

        # Valider les champs requis
        if not all([temperature, humidity, timestamp]):
            return jsonify({"error": "Missing required fields"}), 400

        # Valider les types des données
        if not isinstance(temperature, (int, float)) or not isinstance(humidity, (int, float)):
            return jsonify({"error": "Temperature and humidity must be numbers"}), 400

        # Enregistrer dans la base de données
        new_data = SensorData(temperature=temperature, humidity=humidity, timestamp=timestamp)
        db.session.add(new_data)
        db.session.commit()

        return jsonify({"message": "Data successfully received and stored"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lancer le serveur Flask
if __name__ == '__main__':
    # Désactiver debug=True pour production
    app.run(debug=False, host='0.0.0.0', port=5000)
