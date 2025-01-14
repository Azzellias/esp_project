from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///esp_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle pour stocker les données
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.String(50), nullable=False)
    humidity = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)

# Créer la base de données si elle n'existe pas
with app.app_context():
    db.create_all()

# Route pour afficher l'interface HTML
@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# Route pour recevoir les données de l'ESP
@app.route('/updateData', methods=['GET'])
def update_data():
    temperature = request.args.get('temperature')
    humidity = request.args.get('humidity')
    timestamp = request.args.get('timestamp')  # Assurez-vous de récupérer le timestamp

    # Affichage des données pour le débogage
    print(f"Température: {temperature}, Humidité: {humidity}, Timestamp: {timestamp}")

    if temperature and humidity and timestamp:
        # Ajouter les données dans la base de données
        new_data = Data(temperature=temperature, humidity=humidity, timestamp=timestamp)
        db.session.add(new_data)
        db.session.commit()

        return f"Données reçues : Température = {temperature}, Humidité = {humidity}, Timestamp = {timestamp}"
    else:
        return "Paramètres manquants.", 400

# Route pour récupérer les dernières données (pour l'affichage en temps réel)
@app.route('/getData', methods=['GET'])
def get_data():
    latest_data = Data.query.order_by(Data.id.desc()).first()
    if latest_data:
        return jsonify({
            'temperature': latest_data.temperature,
            'humidity': latest_data.humidity,
            'timestamp': latest_data.timestamp  # Assurez-vous d'envoyer le timestamp ici
        })
    else:
        return "Aucune donnée disponible.", 404

# Route pour télécharger les données sous forme d'Excel
@app.route('/downloadData', methods=['GET'])
def download_data():
    data = Data.query.all()
    if data:
        excel_file = os.path.join(app.root_path, "esp_data.xlsx")
        
        # Regénérer le fichier à chaque appel
        df = pd.DataFrame([{
            'Temperature': item.temperature,
            'Humidity': item.humidity,
            'Timestamp': item.timestamp
        } for item in data])
        df.to_excel(excel_file, index=False)

        # Forcer le téléchargement sans mise en cache
        response = make_response(send_from_directory(app.root_path, "esp_data.xlsx", as_attachment=True))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        return "Aucune donnée à télécharger.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
