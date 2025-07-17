"""
Demonstração do Sistema de Triagem Hospitalar Inteligente
Execute este arquivo para ver o sistema funcionando
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.triage_agent import TriageAgent, PatientData, RiskLevel
from src.utils.data_generator import TriageDataGenerator
from src.ml.models import TriageMLModel
import pandas as pd
import numpy as np
import time

def main():
    print("="*60)
    print("   SISTEMA DE TRIAGEM HOSPITALAR INTELIGENTE")
    print("="*60)
    print("Demonstração dos algoritmos de IA para classificação de risco")
    print("Baseado em Russell & Norvig - Inteligência Artificial")
    print("="*60)
    print()
    
    # Demonstração 1: Agente Inteligente
    print("🤖 DEMONSTRAÇÃO 1: AGENTE INTELIGENTE")
    print("-" * 40)
    demonstrar_agente()
    
    # Demonstração 2: Geração de Dados
    print("\n📊 DEMONSTRAÇÃO 2: GERAÇÃO DE DADOS SINTÉTICOS")
    print("-" * 40)
    demonstrar_dados()
    
    # Demonstração 3: Casos de Teste
    print("\n🧪 DEMONSTRAÇÃO 3: CASOS DE TESTE")
    print("-" * 40)
    demonstrar_casos()
    
    # Demonstração 4: Análise de Performance
    print("\n📈 DEMONSTRAÇÃO 4: ANÁLISE DE PERFORMANCE")
    print("-" * 40)
    demonstrar_performance()
    
    print("\n✅ Demonstração concluída!")
    print("Para iniciar o sistema web, execute: python main.py")
    print("Para ver a documentação completa, execute: python main.py --demo")

def demonstrar_agente():
    """Demonstrar funcionamento do agente inteligente"""
    try:
        agent = TriageAgent()
        
        # Caso 1: Paciente estável (Verde)
        print("Caso 1: Paciente Estável")
        paciente_verde = PatientData(
            pressao_sistolica=120,
            pressao_diastolica=80,
            frequencia_cardiaca=72,
            saturacao_oxigenio=98,
            temperatura=36.5,
            idade=35,
            sexo='M',
            dor_peito=False,
            dificuldade_respiratoria=False,
            febre=False,
            tontura=False,
            vomito=False,
            dor_abdominal=False
        )
        
        resultado = agent.process_patient(paciente_verde)
        print(f"  Resultado: {resultado['classification']}")
        print(f"  Confiança: {resultado['confidence']:.2f}")
        print(f"  Raciocínio: {resultado['reasoning']}")
        
        # Caso 2: Paciente crítico (Vermelho)
        print("\nCaso 2: Paciente Crítico")
        paciente_vermelho = PatientData(
            pressao_sistolica=200,
            pressao_diastolica=120,
            frequencia_cardiaca=140,
            saturacao_oxigenio=85,
            temperatura=40.0,
            idade=70,
            sexo='F',
            dor_peito=True,
            dificuldade_respiratoria=True,
            febre=True,
            tontura=True,
            vomito=True,
            dor_abdominal=False
        )
        
        resultado = agent.process_patient(paciente_vermelho)
        print(f"  Resultado: {resultado['classification']}")
        print(f"  Confiança: {resultado['confidence']:.2f}")
        print(f"  Raciocínio: {resultado['reasoning']}")
        
        # Caso 3: Paciente moderado (Amarelo)
        print("\nCaso 3: Paciente Moderado")
        paciente_amarelo = PatientData(
            pressao_sistolica=150,
            pressao_diastolica=95,
            frequencia_cardiaca=105,
            saturacao_oxigenio=92,
            temperatura=38.5,
            idade=55,
            sexo='M',
            dor_peito=True,
            dificuldade_respiratoria=False,
            febre=True,
            tontura=False,
            vomito=False,
            dor_abdominal=True
        )
        
        resultado = agent.process_patient(paciente_amarelo)
        print(f"  Resultado: {resultado['classification']}")
        print(f"  Confiança: {resultado['confidence']:.2f}")
        print(f"  Raciocínio: {resultado['reasoning']}")
        
    except Exception as e:
        print(f"Erro na demonstração do agente: {e}")

def demonstrar_dados():
    """Demonstrar geração de dados sintéticos"""
    try:
        generator = TriageDataGenerator()
        
        # Gerar dataset pequeno para demonstração
        dataset = generator.generate_synthetic_data(n_samples=50)
        
        print("Dataset gerado com sucesso!")
        print(f"Tamanho: {len(dataset)} amostras")
        print(f"Colunas: {list(dataset.columns)}")
        
        # Estatísticas por risco
        print("\nDistribuição de Risco:")
        risk_counts = dataset['risk_level'].value_counts()
        for risk, count in risk_counts.items():
            percentage = (count / len(dataset)) * 100
            print(f"  {risk}: {count} pacientes ({percentage:.1f}%)")
        
        # Estatísticas dos sinais vitais
        print("\nSinais Vitais (Médias):")
        vitals = ['pressao_sistolica', 'pressao_diastolica', 'frequencia_cardiaca', 
                 'saturacao_oxigenio', 'temperatura', 'idade']
        
        for vital in vitals:
            if vital in dataset.columns:
                mean_val = dataset[vital].mean()
                std_val = dataset[vital].std()
                print(f"  {vital}: {mean_val:.1f} ± {std_val:.1f}")
        
        # Exemplo de paciente gerado
        print("\nExemplo de Paciente Gerado:")
        sample_patient = generator.generate_real_time_patient()
        print(f"  Idade: {sample_patient['idade']} anos")
        print(f"  Pressão: {sample_patient['pressao_sistolica']}/{sample_patient['pressao_diastolica']}")
        print(f"  FC: {sample_patient['frequencia_cardiaca']} bpm")
        print(f"  SpO2: {sample_patient['saturacao_oxigenio']}%")
        print(f"  Temp: {sample_patient['temperatura']}°C")
        print(f"  Risco Real: {sample_patient['true_risk']}")
        
    except Exception as e:
        print(f"Erro na demonstração de dados: {e}")

def demonstrar_casos():
    """Demonstrar casos específicos de teste"""
    try:
        agent = TriageAgent()
        
        casos_teste = [
            {
                'nome': 'Idoso com pressão alta',
                'paciente': PatientData(
                    pressao_sistolica=180, pressao_diastolica=100,
                    frequencia_cardiaca=95, saturacao_oxigenio=94,
                    temperatura=37.0, idade=75, sexo='M',
                    dor_peito=False, dificuldade_respiratoria=True,
                    febre=False, tontura=True, vomito=False, dor_abdominal=False
                ),
                'esperado': 'AMARELO/VERMELHO'
            },
            {
                'nome': 'Jovem com sintomas leves',
                'paciente': PatientData(
                    pressao_sistolica=115, pressao_diastolica=75,
                    frequencia_cardiaca=68, saturacao_oxigenio=99,
                    temperatura=36.8, idade=25, sexo='F',
                    dor_peito=False, dificuldade_respiratoria=False,
                    febre=False, tontura=False, vomito=True, dor_abdominal=True
                ),
                'esperado': 'VERDE'
            },
            {
                'nome': 'Adulto com dor torácica',
                'paciente': PatientData(
                    pressao_sistolica=140, pressao_diastolica=85,
                    frequencia_cardiaca=110, saturacao_oxigenio=96,
                    temperatura=36.9, idade=50, sexo='M',
                    dor_peito=True, dificuldade_respiratoria=False,
                    febre=False, tontura=False, vomito=False, dor_abdominal=False
                ),
                'esperado': 'AMARELO/VERMELHO'
            }
        ]
        
        for i, caso in enumerate(casos_teste, 1):
            print(f"Caso {i}: {caso['nome']}")
            resultado = agent.process_patient(caso['paciente'])
            print(f"  Classificação: {resultado['classification']}")
            print(f"  Esperado: {caso['esperado']}")
            print(f"  Confiança: {resultado['confidence']:.2f}")
            print(f"  Recomendações: {len(resultado['recommendations'])} itens")
            print()
            
            # Pequena pausa para demonstração
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Erro na demonstração de casos: {e}")

def demonstrar_performance():
    """Demonstrar análise de performance do sistema"""
    try:
        print("Executando análise de performance...")
        
        # Gerar dados de teste
        generator = TriageDataGenerator()
        agent = TriageAgent()
        
        # Teste com múltiplos pacientes
        n_tests = 20
        results = []
        true_risks = []
        
        print(f"Testando com {n_tests} pacientes...")
        
        for i in range(n_tests):
            # Gerar paciente
            patient_data = generator.generate_real_time_patient()
            true_risks.append(patient_data['true_risk'])
            
            # Criar PatientData
            patient = PatientData(
                pressao_sistolica=patient_data['pressao_sistolica'],
                pressao_diastolica=patient_data['pressao_diastolica'],
                frequencia_cardiaca=patient_data['frequencia_cardiaca'],
                saturacao_oxigenio=patient_data['saturacao_oxigenio'],
                temperatura=patient_data['temperatura'],
                idade=patient_data['idade'],
                sexo=patient_data['sexo'],
                dor_peito=patient_data['dor_peito'],
                dificuldade_respiratoria=patient_data['dificuldade_respiratoria'],
                febre=patient_data['febre'],
                tontura=patient_data['tontura'],
                vomito=patient_data['vomito'],
                dor_abdominal=patient_data['dor_abdominal']
            )
            
            # Processar
            result = agent.process_patient(patient)
            results.append(result['risk_color'])
            
            # Mostrar progresso
            if (i + 1) % 5 == 0:
                print(f"  Processados: {i + 1}/{n_tests}")
        
        # Calcular acurácia
        correct = sum(1 for pred, true in zip(results, true_risks) if pred == true)
        accuracy = correct / len(results)
        
        print(f"\nResultados da Performance:")
        print(f"  Acurácia: {accuracy:.2f} ({correct}/{len(results)})")
        
        # Distribuição de resultados
        from collections import Counter
        result_counts = Counter(results)
        true_counts = Counter(true_risks)
        
        print(f"\nDistribuição Predita:")
        for risk, count in result_counts.items():
            print(f"  {risk}: {count} ({count/len(results)*100:.1f}%)")
        
        print(f"\nDistribuição Real:")
        for risk, count in true_counts.items():
            print(f"  {risk}: {count} ({count/len(true_risks)*100:.1f}%)")
        
        # Análise de confiança
        confidences = [agent.process_patient(generator.generate_real_time_patient()) 
                      for _ in range(10)]
        avg_confidence = sum(r['confidence'] for r in confidences) / len(confidences)
        print(f"\nConfiança Média: {avg_confidence:.3f}")
        
        # Tempo de processamento
        import time
        start_time = time.time()
        for _ in range(10):
            patient_data = generator.generate_real_time_patient()
            patient = PatientData(**{k: v for k, v in patient_data.items() 
                                   if k != 'true_risk'})
            agent.process_patient(patient)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"Tempo Médio de Processamento: {avg_time:.3f} segundos")
        
    except Exception as e:
        print(f"Erro na demonstração de performance: {e}")

if __name__ == "__main__":
    main()
