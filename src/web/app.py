"""
Interface Web para o Sistema de Triagem Hospitalar
Flask application com foco em acessibilidade
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.triage_agent import TriageAgent, PatientData
from src.utils.data_generator import TriageDataGenerator
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'triagem_hospitalar_secret_key'

# Instanciar agente e gerador de dados
triage_agent = TriageAgent()
data_generator = TriageDataGenerator()

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/triagem', methods=['GET', 'POST'])
def triagem():
    """Página de triagem"""
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            patient_data = PatientData(
                pressao_sistolica=float(request.form['pressao_sistolica']),
                pressao_diastolica=float(request.form['pressao_diastolica']),
                frequencia_cardiaca=float(request.form['frequencia_cardiaca']),
                saturacao_oxigenio=float(request.form['saturacao_oxigenio']),
                temperatura=float(request.form['temperatura']),
                idade=int(request.form['idade']),
                sexo=request.form['sexo'],
                dor_peito=bool(request.form.get('dor_peito')),
                dificuldade_respiratoria=bool(request.form.get('dificuldade_respiratoria')),
                febre=bool(request.form.get('febre')),
                tontura=bool(request.form.get('tontura')),
                vomito=bool(request.form.get('vomito')),
                dor_abdominal=bool(request.form.get('dor_abdominal'))
            )
            
            # Processar triagem
            result = triage_agent.process_patient(patient_data)
            
            return render_template('resultado.html', result=result)
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            flash(f"Erro no processamento: {str(e)}", 'error')
            return redirect(url_for('triagem'))
    
    return render_template('triagem.html')

@app.route('/api/triagem', methods=['POST'])
def api_triagem():
    """API endpoint para triagem"""
    try:
        data = request.get_json()
        
        # Validar dados recebidos
        required_fields = [
            'pressao_sistolica', 'pressao_diastolica', 'frequencia_cardiaca',
            'saturacao_oxigenio', 'temperatura', 'idade', 'sexo'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Criar objeto PatientData
        patient_data = PatientData(
            pressao_sistolica=float(data['pressao_sistolica']),
            pressao_diastolica=float(data['pressao_diastolica']),
            frequencia_cardiaca=float(data['frequencia_cardiaca']),
            saturacao_oxigenio=float(data['saturacao_oxigenio']),
            temperatura=float(data['temperatura']),
            idade=int(data['idade']),
            sexo=data['sexo'],
            dor_peito=data.get('dor_peito', False),
            dificuldade_respiratoria=data.get('dificuldade_respiratoria', False),
            febre=data.get('febre', False),
            tontura=data.get('tontura', False),
            vomito=data.get('vomito', False),
            dor_abdominal=data.get('dor_abdominal', False)
        )
        
        # Processar triagem
        result = triage_agent.process_patient(patient_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/paciente-exemplo')
def paciente_exemplo():
    """Gerar dados de exemplo para teste"""
    try:
        patient_data = data_generator.generate_real_time_patient()
        return jsonify(patient_data)
        
    except Exception as e:
        logger.error(f"Erro ao gerar exemplo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sobre')
def sobre():
    """Página sobre o projeto"""
    return render_template('sobre.html')

@app.route('/acessibilidade')
def acessibilidade():
    """Página de recursos de acessibilidade"""
    return render_template('acessibilidade.html')

@app.errorhandler(404)
def page_not_found(e):
    """Página de erro 404"""
    return render_template('erro.html', error_code=404, error_message="Página não encontrada"), 404

@app.errorhandler(500)
def internal_error(e):
    """Página de erro 500"""
    return render_template('erro.html', error_code=500, error_message="Erro interno do servidor"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
