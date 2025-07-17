"""
Gerador de dados sintéticos para triagem hospitalar
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import random
from datetime import datetime, timedelta

class TriageDataGenerator:
    """
    Gerador de dados sintéticos para treinamento do modelo de triagem
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        # Parâmetros para cada nível de risco
        self.risk_profiles = {
            'VERDE': {
                'weight': 0.60,  # 60% dos casos
                'vital_signs': {
                    'pressao_sistolica': (110, 140),
                    'pressao_diastolica': (70, 90),
                    'frequencia_cardiaca': (60, 100),
                    'saturacao_oxigenio': (95, 100),
                    'temperatura': (36.0, 37.5)
                },
                'symptoms_prob': {
                    'dor_peito': 0.05,
                    'dificuldade_respiratoria': 0.10,
                    'febre': 0.20,
                    'tontura': 0.15,
                    'vomito': 0.10,
                    'dor_abdominal': 0.25
                }
            },
            'AMARELO': {
                'weight': 0.30,  # 30% dos casos
                'vital_signs': {
                    'pressao_sistolica': (90, 170),
                    'pressao_diastolica': (60, 100),
                    'frequencia_cardiaca': (50, 120),
                    'saturacao_oxigenio': (90, 97),
                    'temperatura': (37.0, 39.0)
                },
                'symptoms_prob': {
                    'dor_peito': 0.25,
                    'dificuldade_respiratoria': 0.35,
                    'febre': 0.40,
                    'tontura': 0.30,
                    'vomito': 0.25,
                    'dor_abdominal': 0.35
                }
            },
            'VERMELHO': {
                'weight': 0.10,  # 10% dos casos
                'vital_signs': {
                    'pressao_sistolica': (70, 200),
                    'pressao_diastolica': (40, 120),
                    'frequencia_cardiaca': (40, 150),
                    'saturacao_oxigenio': (70, 95),
                    'temperatura': (35.0, 42.0)
                },
                'symptoms_prob': {
                    'dor_peito': 0.60,
                    'dificuldade_respiratoria': 0.70,
                    'febre': 0.50,
                    'tontura': 0.45,
                    'vomito': 0.40,
                    'dor_abdominal': 0.30
                }
            }
        }
    
    def generate_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Gerar dataset sintético
        """
        data = []
        
        for _ in range(n_samples):
            # Selecionar nível de risco baseado nos pesos
            risk_level = np.random.choice(
                list(self.risk_profiles.keys()),
                p=[profile['weight'] for profile in self.risk_profiles.values()]
            )
            
            # Gerar dados baseados no perfil de risco
            patient_data = self._generate_patient_data(risk_level)
            patient_data['risk_level'] = risk_level
            
            data.append(patient_data)
        
        df = pd.DataFrame(data)
        
        # Adicionar variações e ruído para tornar mais realista
        df = self._add_realistic_variations(df)
        
        return df
    
    def _generate_patient_data(self, risk_level: str) -> Dict:
        """
        Gerar dados de um paciente baseado no nível de risco
        """
        profile = self.risk_profiles[risk_level]
        
        # Gerar idade (idosos têm mais risco)
        if risk_level == 'VERMELHO':
            idade = np.random.normal(65, 20)
        elif risk_level == 'AMARELO':
            idade = np.random.normal(55, 25)
        else:  # VERDE
            idade = np.random.normal(40, 20)
        
        idade = max(18, min(95, int(idade)))
        
        # Gerar sexo
        sexo = np.random.choice(['M', 'F'])
        
        # Gerar sinais vitais
        vital_signs = {}
        for vital, (min_val, max_val) in profile['vital_signs'].items():
            if risk_level == 'VERMELHO':
                # Mais variabilidade para casos críticos
                if vital in ['pressao_sistolica', 'pressao_diastolica']:
                    if np.random.random() < 0.3:  # 30% chance de hipertensão
                        vital_signs[vital] = np.random.normal(max_val, 20)
                    elif np.random.random() < 0.2:  # 20% chance de hipotensão
                        vital_signs[vital] = np.random.normal(min_val, 10)
                    else:
                        vital_signs[vital] = np.random.uniform(min_val, max_val)
                else:
                    vital_signs[vital] = np.random.uniform(min_val, max_val)
            else:
                vital_signs[vital] = np.random.uniform(min_val, max_val)
        
        # Gerar sintomas
        symptoms = {}
        for symptom, prob in profile['symptoms_prob'].items():
            # Ajustar probabilidade baseada na idade
            if symptom == 'dor_peito' and idade > 60:
                prob *= 1.5
            elif symptom == 'dificuldade_respiratoria' and idade > 70:
                prob *= 1.3
            
            symptoms[symptom] = np.random.random() < prob
        
        # Combinar todos os dados
        patient_data = {
            'idade': idade,
            'sexo': sexo,
            **vital_signs,
            **symptoms
        }
        
        return patient_data
    
    def _add_realistic_variations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adicionar variações realistas aos dados
        """
        # Arredondar valores
        df['pressao_sistolica'] = df['pressao_sistolica'].round(0)
        df['pressao_diastolica'] = df['pressao_diastolica'].round(0)
        df['frequencia_cardiaca'] = df['frequencia_cardiaca'].round(0)
        df['saturacao_oxigenio'] = df['saturacao_oxigenio'].round(1)
        df['temperatura'] = df['temperatura'].round(1)
        
        # Garantir limites fisiológicos
        df['pressao_sistolica'] = df['pressao_sistolica'].clip(60, 250)
        df['pressao_diastolica'] = df['pressao_diastolica'].clip(30, 150)
        df['frequencia_cardiaca'] = df['frequencia_cardiaca'].clip(30, 200)
        df['saturacao_oxigenio'] = df['saturacao_oxigenio'].clip(60, 100)
        df['temperatura'] = df['temperatura'].clip(34.0, 43.0)
        
        # Adicionar correlações realistas
        # Pressão diastólica não pode ser maior que sistólica
        df['pressao_diastolica'] = np.minimum(
            df['pressao_diastolica'], 
            df['pressao_sistolica'] - 10
        )
        
        return df
    
    def generate_sample_dataset(self, filename: str = None) -> pd.DataFrame:
        """
        Gerar dataset de exemplo e salvar
        """
        # Gerar dados
        df = self.generate_synthetic_data(n_samples=1000)
        
        # Adicionar metadados
        df['timestamp'] = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            periods=len(df)
        )
        
        # Converter colunas booleanas para int
        bool_columns = ['dor_peito', 'dificuldade_respiratoria', 'febre', 'tontura', 'vomito', 'dor_abdominal']
        for col in bool_columns:
            df[col] = df[col].astype(int)
        
        # Converter sexo para dummy
        df['sexo_M'] = (df['sexo'] == 'M').astype(int)
        df = df.drop('sexo', axis=1)
        
        # Reorganizar colunas
        feature_columns = [
            'idade', 'sexo_M', 'pressao_sistolica', 'pressao_diastolica',
            'frequencia_cardiaca', 'saturacao_oxigenio', 'temperatura',
            'dor_peito', 'dificuldade_respiratoria', 'febre', 'tontura',
            'vomito', 'dor_abdominal'
        ]
        
        df = df[feature_columns + ['risk_level', 'timestamp']]
        
        # Salvar se especificado
        if filename:
            df.to_csv(filename, index=False)
            print(f"Dataset salvo como: {filename}")
        
        return df
    
    def generate_real_time_patient(self) -> Dict:
        """
        Gerar dados de um paciente em tempo real
        """
        # Selecionar nível de risco aleatório
        risk_level = np.random.choice(
            list(self.risk_profiles.keys()),
            p=[profile['weight'] for profile in self.risk_profiles.values()]
        )
        
        patient_data = self._generate_patient_data(risk_level)
        
        # Converter para formato compatível com o agente
        formatted_data = {
            'pressao_sistolica': patient_data['pressao_sistolica'],
            'pressao_diastolica': patient_data['pressao_diastolica'],
            'frequencia_cardiaca': patient_data['frequencia_cardiaca'],
            'saturacao_oxigenio': patient_data['saturacao_oxigenio'],
            'temperatura': patient_data['temperatura'],
            'idade': patient_data['idade'],
            'sexo': patient_data['sexo'],
            'dor_peito': patient_data['dor_peito'],
            'dificuldade_respiratoria': patient_data['dificuldade_respiratoria'],
            'febre': patient_data['febre'],
            'tontura': patient_data['tontura'],
            'vomito': patient_data['vomito'],
            'dor_abdominal': patient_data['dor_abdominal'],
            'true_risk': risk_level  # Para validação
        }
        
        return formatted_data
