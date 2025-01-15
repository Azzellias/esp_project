from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de la base de données PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://esp_data_yshz_user:LUcBbnKHk4OKyBXgfz2YKgvTST1lZOoa@dpg-cu3tdl23esus73fhc0n0-a/esp_data_yshz')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de SQLAlchemy
db = SQLAlchemy(app)

# Modèle pour la table de données
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# Route pour afficher les données en temps réel
@app.route('/')
def index():
    # Récupérer les dernières valeurs de température et humidité
    data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    return render_template('index.html', data=data)

# Route pour fournir les données au format JSON pour l'API
@app.route('/data')
def get_data():
    # Récupérer les dernières valeurs de température et humidité
    data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    return jsonify({
        'temperature': data.temperature,
        'humidity': data.humidity,
        'timestamp': data.timestamp.isoformat() if data else None
    })

# Lancer le serveur Flask
if __name__ == '__main__':
    app.run(debug=True)
