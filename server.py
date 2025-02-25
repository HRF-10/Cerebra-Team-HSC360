from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# === KONEKSI KE MONGODB ===
uri = "mongodb+srv://cerebrateam:cerebrahsc360@cerebracluster.eor71.mongodb.net/?retryWrites=true&w=majority&appName=CerebraCluster"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client["sensor_data"]  # Nama database
collection = db["esp32_readings"]  # Nama koleksi

# === ROUTE UNTUK MENYIMPAN DATA DARI ESP32 ===
@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.json  # Ambil data dari request ESP32
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Simpan ke MongoDB
        insert_result = collection.insert_one(data)
        return jsonify({"message": "Data inserted", "id": str(insert_result.inserted_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === JALANKAN SERVER ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)