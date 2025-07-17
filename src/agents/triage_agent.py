"""
Agente Inteligente para Triagem Hospitalar
Implementação baseada em arquitetura PEAS
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Classificação de risco baseada no protocolo de Manchester"""
    VERMELHO = "Emergência"      # Atendimento imediato
    AMARELO = "Urgente"          # Até 1 hora
    VERDE = "Não Urgente"        # Até 4 horas

@dataclass
class PatientData:
    """Dados do paciente para triagem"""
    # Sinais vitais
    pressao_sistolica: float
    pressao_diastolica: float
    frequencia_cardiaca: float
    saturacao_oxigenio: float
    temperatura: float
    
    # Dados demográficos
    idade: int
    sexo: str  # 'M' ou 'F'
    
    # Sintomas principais
    dor_peito: bool
    dificuldade_respiratoria: bool
    febre: bool
    tontura: bool
    vomito: bool
    dor_abdominal: bool

@dataclass
class TriageResult:
    """Resultado da triagem"""
    risk_level: RiskLevel
    confidence_score: float
    reasoning: str
    recommendations: List[str]

class TriageAgent:
    """
    Agente Inteligente para Triagem Hospitalar
    Arquitetura PEAS:
    - Performance: Acurácia, F1-Score, tempo de resposta
    - Environment: Sistema hospitalar simulado
    - Actuators: Interface de classificação
    - Sensors: Formulário de entrada de dados
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        
    def perceive(self, patient_data: PatientData) -> Dict:
        """
        Sensors: Percepção dos dados do paciente
        """
        try:
            # Converter dados do paciente para formato processável
            features = {
                'pressao_sistolica': patient_data.pressao_sistolica,
                'pressao_diastolica': patient_data.pressao_diastolica,
                'frequencia_cardiaca': patient_data.frequencia_cardiaca,
                'saturacao_oxigenio': patient_data.saturacao_oxigenio,
                'temperatura': patient_data.temperatura,
                'idade': patient_data.idade,
                'sexo_M': 1 if patient_data.sexo == 'M' else 0,
                'dor_peito': 1 if patient_data.dor_peito else 0,
                'dificuldade_respiratoria': 1 if patient_data.dificuldade_respiratoria else 0,
                'febre': 1 if patient_data.febre else 0,
                'tontura': 1 if patient_data.tontura else 0,
                'vomito': 1 if patient_data.vomito else 0,
                'dor_abdominal': 1 if patient_data.dor_abdominal else 0
            }
            
            logger.info(f"Dados percebidos: {features}")
            return features
            
        except Exception as e:
            logger.error(f"Erro na percepção: {e}")
            return {}
    
    def reason(self, features: Dict) -> TriageResult:
        """
        Raciocínio probabilístico para classificação
        Implementa regras baseadas em conhecimento médico
        """
        try:
            # Lógica de raciocínio baseada em regras
            risk_score = 0
            reasoning_factors = []
            
            # Avaliar sinais vitais críticos
            if features['pressao_sistolica'] > 180 or features['pressao_sistolica'] < 90:
                risk_score += 3
                reasoning_factors.append("Pressão arterial crítica")
            
            if features['frequencia_cardiaca'] > 120 or features['frequencia_cardiaca'] < 50:
                risk_score += 3
                reasoning_factors.append("Frequência cardíaca alterada")
            
            if features['saturacao_oxigenio'] < 90:
                risk_score += 4
                reasoning_factors.append("Saturação de oxigênio baixa")
            
            if features['temperatura'] > 39.5:
                risk_score += 2
                reasoning_factors.append("Febre alta")
            
            # Avaliar sintomas críticos
            if features['dor_peito'] and features['idade'] > 50:
                risk_score += 4
                reasoning_factors.append("Dor no peito em paciente > 50 anos")
            
            if features['dificuldade_respiratoria']:
                risk_score += 3
                reasoning_factors.append("Dificuldade respiratória")
            
            # Determinar nível de risco
            if risk_score >= 7:
                risk_level = RiskLevel.VERMELHO
                confidence = min(0.95, 0.7 + (risk_score - 7) * 0.05)
            elif risk_score >= 3:
                risk_level = RiskLevel.AMARELO
                confidence = min(0.90, 0.6 + (risk_score - 3) * 0.075)
            else:
                risk_level = RiskLevel.VERDE
                confidence = min(0.85, 0.5 + risk_score * 0.1)
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(risk_level, reasoning_factors)
            
            return TriageResult(
                risk_level=risk_level,
                confidence_score=confidence,
                reasoning="; ".join(reasoning_factors) if reasoning_factors else "Sinais vitais estáveis",
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Erro no raciocínio: {e}")
            return TriageResult(
                risk_level=RiskLevel.AMARELO,
                confidence_score=0.5,
                reasoning="Erro na avaliação - requer avaliação médica",
                recommendations=["Consulta médica imediata"]
            )
    
    def _generate_recommendations(self, risk_level: RiskLevel, factors: List[str]) -> List[str]:
        """Gerar recomendações baseadas no nível de risco"""
        recommendations = []
        
        if risk_level == RiskLevel.VERMELHO:
            recommendations.extend([
                "Atendimento médico IMEDIATO",
                "Preparar sala de emergência",
                "Monitorização contínua",
                "Acesso venoso imediato"
            ])
        elif risk_level == RiskLevel.AMARELO:
            recommendations.extend([
                "Atendimento em até 1 hora",
                "Reavaliação em 30 minutos",
                "Monitorização periódica"
            ])
        else:  # VERDE
            recommendations.extend([
                "Atendimento em até 4 horas",
                "Orientações gerais",
                "Reavaliação se piora"
            ])
        
        return recommendations
    
    def act(self, triage_result: TriageResult) -> Dict:
        """
        Actuators: Ação do agente - retorna resultado da triagem
        """
        try:
            action = {
                'classification': triage_result.risk_level.value,
                'risk_color': triage_result.risk_level.name,
                'confidence': round(triage_result.confidence_score, 2),
                'reasoning': triage_result.reasoning,
                'recommendations': triage_result.recommendations,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            logger.info(f"Ação executada: {action}")
            return action
            
        except Exception as e:
            logger.error(f"Erro na ação: {e}")
            return {
                'classification': 'Erro',
                'risk_color': 'AMARELO',
                'confidence': 0.0,
                'reasoning': 'Erro no sistema',
                'recommendations': ['Avaliação médica manual'],
                'timestamp': pd.Timestamp.now().isoformat()
            }
    
    def evaluate_performance(self, true_labels: List[str], predicted_labels: List[str]) -> Dict:
        """
        Performance: Avaliação do desempenho do agente
        """
        try:
            from sklearn.metrics import accuracy_score, f1_score, classification_report
            
            accuracy = accuracy_score(true_labels, predicted_labels)
            f1 = f1_score(true_labels, predicted_labels, average='weighted')
            
            performance = {
                'accuracy': round(accuracy, 3),
                'f1_score': round(f1, 3),
                'classification_report': classification_report(true_labels, predicted_labels)
            }
            
            logger.info(f"Performance: {performance}")
            return performance
            
        except Exception as e:
            logger.error(f"Erro na avaliação: {e}")
            return {'accuracy': 0.0, 'f1_score': 0.0, 'error': str(e)}
    
    def process_patient(self, patient_data: PatientData) -> Dict:
        """
        Processo completo de triagem de um paciente
        """
        try:
            # Percepção
            features = self.perceive(patient_data)
            
            # Raciocínio
            triage_result = self.reason(features)
            
            # Ação
            action = self.act(triage_result)
            
            return action
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            return {
                'classification': 'Erro',
                'risk_color': 'AMARELO',
                'confidence': 0.0,
                'reasoning': f'Erro no sistema: {str(e)}',
                'recommendations': ['Avaliação médica manual imediata'],
                'timestamp': pd.Timestamp.now().isoformat()
            }
