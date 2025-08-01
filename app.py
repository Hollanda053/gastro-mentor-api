from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
import hashlib

app = Flask(__name__)
CORS(app)

# Configurações
SECRET_KEY = os.environ.get('SECRET_KEY', 'gastro_mentor_2024_secret_key')
app.config['SECRET_KEY'] = SECRET_KEY

# Simulação de banco de dados em memória
users_db = {}
receitas_db = {}
ingredientes_db = {}

@app.route('/')
def home():
    return jsonify({
        "message": "🍽️ API Gastro Mentor V2.0 - Sistema Completo",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/api/health",
            "registro": "POST /api/registro",
            "login": "POST /api/login",
            "receitas": "GET/POST /api/receitas",
            "ingredientes": "GET/POST /api/ingredientes",
            "cmv": "POST /api/cmv/calcular",
            "precificacao": "POST /api/precificacao/calcular",
            "conversoes": "POST /api/conversoes/peso ou /api/conversoes/volume",
            "relatorios": "GET /api/relatorios/financeiro ou /api/relatorios/estoque"
        },
        "documentacao": "Acesse os endpoints acima para usar o sistema"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "OK",
        "message": "API Gastro Mentor funcionando perfeitamente!",
        "timestamp": datetime.now().isoformat(),
        "database": "conectado",
        "version": "2.0"
    })

@app.route('/api/registro', methods=['POST'])
def registro():
    try:
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        
        if not all([nome, email, senha]):
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
            
        if email in users_db:
            return jsonify({"erro": "Email já cadastrado"}), 400
            
        # Hash da senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        # Salvar usuário
        users_db[email] = {
            "nome": nome,
            "email": email,
            "senha": senha_hash,
            "data_cadastro": datetime.now().isoformat()
        }
        
        return jsonify({
            "message": "Usuário cadastrado com sucesso!",
            "usuario": {"nome": nome, "email": email}
        }), 201
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not all([email, senha]):
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400
            
        user = users_db.get(email)
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404
            
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        if user['senha'] != senha_hash:
            return jsonify({"erro": "Senha incorreta"}), 401
            
        # Token simples (em produção usar JWT)
        token = hashlib.sha256(f"{email}{datetime.now()}".encode()).hexdigest()
        
        return jsonify({
            "message": "Login realizado com sucesso!",
            "token": token,
            "usuario": {"nome": user['nome'], "email": user['email']}
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/receitas', methods=['GET', 'POST'])
def receitas():
    if request.method == 'GET':
        return jsonify({
            "receitas": list(receitas_db.values()),
            "total": len(receitas_db)
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            nome = data.get('nome')
            ingredientes = data.get('ingredientes', [])
            modo_preparo = data.get('modo_preparo', '')
            tempo_preparo = data.get('tempo_preparo', 0)
            rendimento = data.get('rendimento', 1)
            
            if not nome:
                return jsonify({"erro": "Nome da receita é obrigatório"}), 400
                
            receita_id = len(receitas_db) + 1
            receita = {
                "id": receita_id,
                "nome": nome,
                "ingredientes": ingredientes,
                "modo_preparo": modo_preparo,
                "tempo_preparo": tempo_preparo,
                "rendimento": rendimento,
                "data_criacao": datetime.now().isoformat()
            }
            
            receitas_db[receita_id] = receita
            
            return jsonify({
                "message": "Receita criada com sucesso!",
                "receita": receita
            }), 201
            
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

@app.route('/api/ingredientes', methods=['GET', 'POST'])
def ingredientes():
    if request.method == 'GET':
        return jsonify({
            "ingredientes": list(ingredientes_db.values()),
            "total": len(ingredientes_db)
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            nome = data.get('nome')
            preco_unitario = data.get('preco_unitario', 0)
            unidade = data.get('unidade', 'kg')
            estoque_atual = data.get('estoque_atual', 0)
            
            if not nome:
                return jsonify({"erro": "Nome do ingrediente é obrigatório"}), 400
                
            ingrediente_id = len(ingredientes_db) + 1
            ingrediente = {
                "id": ingrediente_id,
                "nome": nome,
                "preco_unitario": float(preco_unitario),
                "unidade": unidade,
                "estoque_atual": float(estoque_atual),
                "data_cadastro": datetime.now().isoformat()
            }
            
            ingredientes_db[ingrediente_id] = ingrediente
            
            return jsonify({
                "message": "Ingrediente cadastrado com sucesso!",
                "ingrediente": ingrediente
            }), 201
            
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

@app.route('/api/cmv/calcular', methods=['POST'])
def calcular_cmv():
    try:
        data = request.get_json()
        ingredientes = data.get('ingredientes', [])
        
        custo_total = 0
        detalhes = []
        
        for item in ingredientes:
            nome = item.get('nome')
            quantidade = float(item.get('quantidade', 0))
            preco_unitario = float(item.get('preco_unitario', 0))
            
            custo_item = quantidade * preco_unitario
            custo_total += custo_item
            
            detalhes.append({
                "ingrediente": nome,
                "quantidade": quantidade,
                "preco_unitario": preco_unitario,
                "custo_total": round(custo_item, 2)
            })
        
        return jsonify({
            "cmv": round(custo_total, 2),
            "detalhes": detalhes,
            "data_calculo": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/precificacao/calcular', methods=['POST'])
def calcular_precificacao():
    try:
        data = request.get_json()
        cmv = float(data.get('cmv', 0))
        margem_lucro = float(data.get('margem_lucro', 30))  # 30% padrão
        
        preco_venda = cmv / (1 - (margem_lucro / 100))
        lucro_unitario = preco_venda - cmv
        
        return jsonify({
            "cmv": round(cmv, 2),
            "margem_lucro": margem_lucro,
            "preco_venda": round(preco_venda, 2),
            "lucro_unitario": round(lucro_unitario, 2),
            "data_calculo": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/conversoes/peso', methods=['POST'])
def converter_peso():
    try:
        data = request.get_json()
        valor = float(data.get('valor', 0))
        de = data.get('de', 'g')
        para = data.get('para', 'kg')
        
        # Conversões para gramas
        conversoes = {
            'mg': 0.001,
            'g': 1,
            'kg': 1000,
            'lb': 453.592,
            'oz': 28.3495
        }
        
        if de not in conversoes or para not in conversoes:
            return jsonify({"erro": "Unidade não suportada"}), 400
            
        # Converter para gramas primeiro, depois para unidade final
        valor_gramas = valor * conversoes[de]
        resultado = valor_gramas / conversoes[para]
        
        return jsonify({
            "valor_original": valor,
            "unidade_original": de,
            "valor_convertido": round(resultado, 4),
            "unidade_final": para,
            "data_conversao": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/conversoes/volume', methods=['POST'])
def converter_volume():
    try:
        data = request.get_json()
        valor = float(data.get('valor', 0))
        de = data.get('de', 'ml')
        para = data.get('para', 'l')
        
        # Conversões para mililitros
        conversoes = {
            'ml': 1,
            'cl': 10,
            'dl': 100,
            'l': 1000,
            'cup': 240,
            'tbsp': 15,
            'tsp': 5
        }
        
        if de not in conversoes or para not in conversoes:
            return jsonify({"erro": "Unidade não suportada"}), 400
            
        # Converter para ml primeiro, depois para unidade final
        valor_ml = valor * conversoes[de]
        resultado = valor_ml / conversoes[para]
        
        return jsonify({
            "valor_original": valor,
            "unidade_original": de,
            "valor_convertido": round(resultado, 4),
            "unidade_final": para,
            "data_conversao": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/relatorios/financeiro', methods=['GET'])
def relatorio_financeiro():
    try:
        total_receitas = len(receitas_db)
        total_ingredientes = len(ingredientes_db)
        
        # Calcular custos médios
        custo_medio = 0
        if ingredientes_db:
            custos = [ing['preco_unitario'] for ing in ingredientes_db.values()]
            custo_medio = sum(custos) / len(custos)
        
        return jsonify({
            "relatorio": "Financeiro",
            "data_geracao": datetime.now().isoformat(),
            "resumo": {
                "total_receitas": total_receitas,
                "total_ingredientes": total_ingredientes,
                "custo_medio_ingredientes": round(custo_medio, 2)
            },
            "receitas": list(receitas_db.values()),
            "ingredientes": list(ingredientes_db.values())
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/relatorios/estoque', methods=['GET'])
def relatorio_estoque():
    try:
        estoque_total = 0
        valor_total = 0
        alertas = []
        
        for ingrediente in ingredientes_db.values():
            estoque = ingrediente['estoque_atual']
            preco = ingrediente['preco_unitario']
            
            estoque_total += estoque
            valor_total += estoque * preco
            
            if estoque < 10:  # Alerta para estoque baixo
                alertas.append({
                    "ingrediente": ingrediente['nome'],
                    "estoque_atual": estoque,
                    "status": "ESTOQUE BAIXO"
                })
        
        return jsonify({
            "relatorio": "Estoque",
            "data_geracao": datetime.now().isoformat(),
            "resumo": {
                "total_ingredientes": len(ingredientes_db),
                "estoque_total": round(estoque_total, 2),
                "valor_total_estoque": round(valor_total, 2),
                "alertas_estoque_baixo": len(alertas)
            },
            "alertas": alertas,
            "ingredientes": list(ingredientes_db.values())
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/planos', methods=['GET'])
def planos():
    return jsonify({
        "planos": [
            {
                "nome": "Básico",
                "preco": "R$ 29,90/mês",
                "recursos": ["Até 50 receitas", "CMV básico", "Suporte email"]
            },
            {
                "nome": "Profissional",
                "preco": "R$ 59,90/mês",
                "recursos": ["Receitas ilimitadas", "Relatórios avançados", "Suporte prioritário"]
            },
            {
                "nome": "Enterprise",
                "preco": "R$ 99,90/mês",
                "recursos": ["Tudo do Profissional", "API personalizada", "Suporte 24/7"]
            }
        ]
    })

@app.route('/api/receitas-publicas', methods=['GET'])
def receitas_publicas():
    receitas_exemplo = [
        {
            "id": 1,
            "nome": "Brigadeiro Gourmet",
            "ingredientes": ["Leite condensado", "Chocolate em pó", "Manteiga"],
            "tempo_preparo": 20,
            "rendimento": 30
        },
        {
            "id": 2,
            "nome": "Pão de Açúcar",
            "ingredientes": ["Farinha", "Açúcar", "Ovos", "Fermento"],
            "tempo_preparo": 45,
            "rendimento": 8
        }
    ]
    
    return jsonify({
        "receitas_publicas": receitas_exemplo,
        "total": len(receitas_exemplo)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

