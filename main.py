import sys
import os

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.web.app import app
from src.utils.data_generator import DataGenerator
from src.agents.triage_agent import TriageAgent, PatientData, RiskLevel
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando Sistema de Triagem Hospitalar Inteligente")
        
        # Verificar se é primeira execução
        if len(sys.argv) > 1 and sys.argv[1] == '--demo':
            run_demo()
        else:
            # Iniciar servidor web
            logger.info("Iniciando servidor web na porta 5000")
            logger.info("Acesse: http://localhost:5000")
            app.run(debug=True, host='0.0.0.0', port=5000)
            
    except KeyboardInterrupt:
        logger.info("Sistema interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao executar sistema: {e}")
        sys.exit(1)

def run_demo():
    logger.info("Executando demonstração do sistema")
    
    # Criar instâncias
    agent = TriageAgent()
    data_generator = DataGenerator()
    
    # Gerar dados de exemplo
    logger.info("Gerando dados de exemplo...")
    sample_data = data_generator.generate_real_time_patient()
    
    # Criar objeto PatientData
    patient = PatientData(
        pressao_sistolica=sample_data['pressao_sistolica'],
        pressao_diastolica=sample_data['pressao_diastolica'],
        frequencia_cardiaca=sample_data['frequencia_cardiaca'],
        saturacao_oxigenio=sample_data['saturacao_oxigenio'],
        temperatura=sample_data['temperatura'],
        idade=sample_data['idade'],
        sexo=sample_data['sexo'],
        dor_peito=sample_data['dor_peito'],
        dificuldade_respiratoria=sample_data['dificuldade_respiratoria'],
        febre=sample_data['febre'],
        tontura=sample_data['tontura'],
        vomito=sample_data['vomito'],
        dor_abdominal=sample_data['dor_abdominal']
    )
    
    # Processar triagem
    logger.info("Processando triagem...")
    result = agent.process_patient(patient)
    
    # Exibir resultados
    print("\n" + "="*50)
    print("DEMONSTRAÇÃO - SISTEMA DE TRIAGEM HOSPITALAR")
    print("="*50)
    print(f"Dados do Paciente:")
    print(f"  Idade: {patient.idade} anos")
    print(f"  Sexo: {patient.sexo}")
    print(f"  Pressão Arterial: {patient.pressao_sistolica}/{patient.pressao_diastolica} mmHg")
    print(f"  Frequência Cardíaca: {patient.frequencia_cardiaca} bpm")
    print(f"  Saturação O2: {patient.saturacao_oxigenio}%")
    print(f"  Temperatura: {patient.temperatura}°C")
    print(f"  Sintomas:")
    symptoms = [
        ("Dor no peito", patient.dor_peito),
        ("Dificuldade respiratória", patient.dificuldade_respiratoria),
        ("Febre", patient.febre),
        ("Tontura", patient.tontura),
        ("Vômito", patient.vomito),
        ("Dor abdominal", patient.dor_abdominal)
    ]
    for symptom, present in symptoms:
        if present:
            print(f"    • {symptom}")
    
    print(f"\nResultado da Triagem:")
    print(f"  Classificação: {result['classification']}")
    print(f"  Nível de Risco: {result['risk_color']}")
    print(f"  Confiança: {result['confidence'] * 100:.1f}%")
    print(f"  Raciocínio: {result['reasoning']}")
    print(f"  Recomendações:")
    for rec in result['recommendations']:
        print(f"    • {rec}")
    
    print(f"\nRisco Real: {sample_data['true_risk']}")
    print("="*50)
    
    # Estatísticas do sistema
    logger.info("Gerando estatísticas do sistema...")
    generate_statistics()

def generate_statistics():
    try:
        logger.info("Gerando dataset de teste...")
        data_generator = DataGenerator()
        
        # Criar dataset de teste
        dataset = data_generator.generate_synthetic_data(n_samples=100)
        
        # Estatísticas básicas
        risk_counts = dataset['risk_level'].value_counts()
        
        print(f"\nEstatísticas do Sistema (100 amostras):")
        print(f"  Distribuição de Risco:")
        for risk, count in risk_counts.items():
            print(f"    {risk}: {count} pacientes ({count/len(dataset)*100:.1f}%)")
        
        print(f"\n  Sinais Vitais Médios:")
        print(f"    Pressão Sistólica: {dataset['pressao_sistolica'].mean():.1f} mmHg")
        print(f"    Pressão Diastólica: {dataset['pressao_diastolica'].mean():.1f} mmHg")
        print(f"    Frequência Cardíaca: {dataset['frequencia_cardiaca'].mean():.1f} bpm")
        print(f"    Saturação O2: {dataset['saturacao_oxigenio'].mean():.1f}%")
        print(f"    Temperatura: {dataset['temperatura'].mean():.1f}°C")
        print(f"    Idade Média: {dataset['idade'].mean():.1f} anos")
        
        # Salvar dataset
        os.makedirs('data', exist_ok=True)
        dataset.to_csv('data/sample_dataset.csv', index=False)
        logger.info("Dataset salvo em: data/sample_dataset.csv")
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {e}")

if __name__ == "__main__":
    main()
