from flask import Flask, request, jsonify
from flask_cors import CORS
from marshmallow import ValidationError
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Usuario
from schemas import UsuarioSchema
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
CORS(app)
app.config.from_object('config')
db.init_app(app)

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

def validar_cpf(cpf: str) -> bool:
    return bool(re.fullmatch(r'\d{11}', cpf))

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    try:
        json_data = request.get_json(force=True)
    except Exception:
        return jsonify({"erro": "Requisição malformada. Envie dados em formato JSON."}), 400

    if 'cpf' in json_data and not validar_cpf(json_data['cpf']):
        return jsonify({"erro": "CPF inválido. Use 11 dígitos numéricos."}), 400

    if 'email' in json_data:
        existente = Usuario.query.filter_by(email=json_data['email']).first()
        if existente:
            return jsonify({"erro": "Email já cadastrado."}), 400

    try:
        dados = usuario_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Hash da senha antes de salvar
    if 'senha' in dados:
        dados['senha'] = generate_password_hash(dados['senha'])

    novo_usuario = Usuario(**dados)
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify(usuario_schema.dump(novo_usuario)), 201

@app.route('/login', methods=['POST'])
def login():
    json_data = request.get_json(force=True)
    email = json_data.get('email')
    senha = json_data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios."}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({"erro": "Email ou senha inválidos."}), 401

    # Retorno de token simples (em produção usar JWT)
    token = f"token_simples_{usuario.id}"
    return jsonify({"token": token, "user": usuario_schema.dump(usuario)}), 200

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(usuarios))

@app.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
