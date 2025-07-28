from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "🍽️ Gastro Mentor API v1.0",
        "status": "online",
        "endpoints": ["/api/health", "/api/planos", "/api/receitas-basicas"]
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "OK", "message": "API funcionando perfeitamente!"})

@app.route('/api/planos', methods=['GET'])
def planos():
    return jsonify({
        "success": True,
        "planos": {
            "basico": {"nome": "Básico", "preco": 0.00, "recursos": ["10 receitas", "Conversor básico"]},
            "premium": {"nome": "Premium", "preco": 29.90, "recursos": ["Receitas ilimitadas", "CMV", "Gestão completa"]}
        }
    })

@app.route('/api/receitas-basicas', methods=['GET'])
def receitas():
    return jsonify({
        "success": True,
        "receitas": [
            {"id": 1, "nome": "Brigadeiro", "categoria": "Doces", "tempo": "30min"},
            {"id": 2, "nome": "Pão de Açúcar", "categoria": "Pães", "tempo": "2h"},
            {"id": 3, "nome": "Lasanha", "categoria": "Massas", "tempo": "1h30min"}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
