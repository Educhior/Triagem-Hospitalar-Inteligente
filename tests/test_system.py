"""
Testes para o sistema de triagem hospitalar
"""

import unittest
import sys
import os

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agents.triage_agent import TriageAgent, PatientData, RiskLevel
from src.utils.data_generator import TriageDataGenerator
import numpy as np
import pandas as pd

class TestTriageAgent(unittest.TestCase):
    """
    Testes para o agente de triagem
    """
    
    def setUp(self):
        """Configurar teste"""
        self.agent = TriageAgent()
        
    def test_patient_data_creation(self):
        """Testar criação de dados do paciente"""
        patient = PatientData(
            pressao_sistolica=120,
            pressao_diastolica=80,
            frequencia_cardiaca=70,
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
        
        self.assertEqual(patient.idade, 35)
        self.assertEqual(patient.sexo, 'M')
        self.assertFalse(patient.dor_peito)
        
    def test_perceive_function(self):
        """Testar função de percepção"""
        patient = PatientData(
            pressao_sistolica=120,
            pressao_diastolica=80,
            frequencia_cardiaca=70,
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
        
        features = self.agent.perceive(patient)
        
        self.assertIsInstance(features, dict)
        self.assertIn('pressao_sistolica', features)
        self.assertIn('sexo_M', features)
        self.assertEqual(features['sexo_M'], 1)
        
    def test_normal_case_reasoning(self):
        """Testar raciocínio para caso normal"""
        features = {
            'pressao_sistolica': 120,
            'pressao_diastolica': 80,
            'frequencia_cardiaca': 70,
            'saturacao_oxigenio': 98,
            'temperatura': 36.5,
            'idade': 35,
            'sexo_M': 1,
            'dor_peito': 0,
            'dificuldade_respiratoria': 0,
            'febre': 0,
            'tontura': 0,
            'vomito': 0,
            'dor_abdominal': 0
        }
        
        result = self.agent.reason(features)
        
        self.assertIsInstance(result.risk_level, RiskLevel)
        self.assertEqual(result.risk_level, RiskLevel.VERDE)
        self.assertGreater(result.confidence_score, 0)
        self.assertLess(result.confidence_score, 1)
        
    def test_emergency_case_reasoning(self):
        """Testar raciocínio para caso de emergência"""
        features = {
            'pressao_sistolica': 200,
            'pressao_diastolica': 120,
            'frequencia_cardiaca': 140,
            'saturacao_oxigenio': 85,
            'temperatura': 40.0,
            'idade': 70,
            'sexo_M': 1,
            'dor_peito': 1,
            'dificuldade_respiratoria': 1,
            'febre': 1,
            'tontura': 1,
            'vomito': 1,
            'dor_abdominal': 0
        }
        
        result = self.agent.reason(features)
        
        self.assertEqual(result.risk_level, RiskLevel.VERMELHO)
        self.assertGreater(result.confidence_score, 0.7)
        
    def test_full_process(self):
        """Testar processo completo"""
        patient = PatientData(
            pressao_sistolica=140,
            pressao_diastolica=90,
            frequencia_cardiaca=85,
            saturacao_oxigenio=96,
            temperatura=37.2,
            idade=55,
            sexo='F',
            dor_peito=True,
            dificuldade_respiratoria=False,
            febre=True,
            tontura=False,
            vomito=False,
            dor_abdominal=False
        )
        
        result = self.agent.process_patient(patient)
        
        self.assertIsInstance(result, dict)
        self.assertIn('classification', result)
        self.assertIn('confidence', result)
        self.assertIn('reasoning', result)
        self.assertIn('recommendations', result)

class TestDataGenerator(unittest.TestCase):
    """
    Testes para o gerador de dados
    """
    
    def setUp(self):
        """Configurar teste"""
        self.generator = TriageDataGenerator()
        
    def test_generate_synthetic_data(self):
        """Testar geração de dados sintéticos"""
        df = self.generator.generate_synthetic_data(n_samples=100)
        
        self.assertEqual(len(df), 100)
        self.assertIn('risk_level', df.columns)
        self.assertIn('idade', df.columns)
        self.assertIn('pressao_sistolica', df.columns)
        
        # Verificar tipos de dados
        self.assertTrue(df['idade'].dtype in [np.int64, np.int32])
        self.assertTrue(df['pressao_sistolica'].dtype in [np.float64, np.float32])
        
    def test_generate_real_time_patient(self):
        """Testar geração de paciente em tempo real"""
        patient_data = self.generator.generate_real_time_patient()
        
        self.assertIsInstance(patient_data, dict)
        self.assertIn('idade', patient_data)
        self.assertIn('sexo', patient_data)
        self.assertIn('pressao_sistolica', patient_data)
        self.assertIn('true_risk', patient_data)
        
        # Verificar limites
        self.assertGreaterEqual(patient_data['idade'], 18)
        self.assertLessEqual(patient_data['idade'], 95)
        self.assertIn(patient_data['sexo'], ['M', 'F'])
        self.assertIn(patient_data['true_risk'], ['VERDE', 'AMARELO', 'VERMELHO'])
        
    def test_data_quality(self):
        """Testar qualidade dos dados gerados"""
        df = self.generator.generate_synthetic_data(n_samples=1000)
        
        # Verificar distribuição de risco
        risk_counts = df['risk_level'].value_counts()
        self.assertGreater(risk_counts['VERDE'], risk_counts['AMARELO'])
        self.assertGreater(risk_counts['AMARELO'], risk_counts['VERMELHO'])
        
        # Verificar limites fisiológicos
        self.assertTrue(df['pressao_sistolica'].min() >= 60)
        self.assertTrue(df['pressao_sistolica'].max() <= 250)
        self.assertTrue(df['saturacao_oxigenio'].min() >= 60)
        self.assertTrue(df['saturacao_oxigenio'].max() <= 100)
        
        # Verificar correlação pressão arterial
        self.assertTrue((df['pressao_diastolica'] < df['pressao_sistolica']).all())

class TestIntegration(unittest.TestCase):
    """
    Testes de integração
    """
    
    def setUp(self):
        """Configurar teste"""
        self.agent = TriageAgent()
        self.generator = TriageDataGenerator()
        
    def test_end_to_end_workflow(self):
        """Testar fluxo completo"""
        # Gerar dados
        patient_data = self.generator.generate_real_time_patient()
        
        # Converter para PatientData
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
        result = self.agent.process_patient(patient)
        
        # Verificar resultado
        self.assertIsInstance(result, dict)
        self.assertIn('classification', result)
        self.assertIn(result['risk_color'], ['VERDE', 'AMARELO', 'VERMELHO'])
        self.assertIsInstance(result['recommendations'], list)
        self.assertGreater(len(result['recommendations']), 0)
        
    def test_batch_processing(self):
        """Testar processamento em lote"""
        # Gerar múltiplos pacientes
        patients = []
        for _ in range(10):
            patient_data = self.generator.generate_real_time_patient()
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
            patients.append(patient)
        
        # Processar todos
        results = []
        for patient in patients:
            result = self.agent.process_patient(patient)
            results.append(result)
        
        # Verificar resultados
        self.assertEqual(len(results), 10)
        
        # Verificar que todos têm campos necessários
        for result in results:
            self.assertIn('classification', result)
            self.assertIn('confidence', result)
            self.assertIn('reasoning', result)
            self.assertIn('recommendations', result)

if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2)
