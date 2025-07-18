"""
Modelo de Pessoa para Sistema de Triagem Hospitalar
Inclui dados pessoais, histórico médico e classificação de risco
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class RiskLevel(Enum):
    """Classificação de risco baseada no protocolo de Manchester"""
    VERMELHO = "Emergência"      # Atendimento imediato
    AMARELO = "Urgente"          # Até 1 hora
    VERDE = "Não Urgente"        # Até 4 horas

class Gender(Enum):
    """Gênero do paciente"""
    MASCULINO = "M"
    FEMININO = "F"
    OUTRO = "O"

@dataclass
class VitalSigns:
    """Sinais vitais do paciente"""
    pressao_sistolica: float
    pressao_diastolica: float
    frequencia_cardiaca: float
    saturacao_oxigenio: float
    temperatura: float
    frequencia_respiratoria: Optional[float] = None
    dor_escala: Optional[int] = None  # Escala de 0-10
    nivel_consciencia: Optional[str] = None  # Alerta, confuso, inconsciente
    
    def __post_init__(self):
        """Validação dos sinais vitais"""
        if self.pressao_sistolica < 50 or self.pressao_sistolica > 250:
            raise ValueError("Pressão sistólica fora do range válido")
        if self.pressao_diastolica < 30 or self.pressao_diastolica > 150:
            raise ValueError("Pressão diastólica fora do range válido")
        if self.frequencia_cardiaca < 30 or self.frequencia_cardiaca > 200:
            raise ValueError("Frequência cardíaca fora do range válido")
        if self.saturacao_oxigenio < 50 or self.saturacao_oxigenio > 100:
            raise ValueError("Saturação de oxigênio fora do range válido")
        if self.temperatura < 30 or self.temperatura > 45:
            raise ValueError("Temperatura fora do range válido")

@dataclass
class Symptoms:
    """Sintomas apresentados pelo paciente"""
    dor_peito: bool = False
    dificuldade_respiratoria: bool = False
    febre: bool = False
    tontura: bool = False
    vomito: bool = False
    dor_abdominal: bool = False
    convulsoes: bool = False
    sangramento_ativo: bool = False
    perda_consciencia: bool = False
    dor_cabeca_intensa: bool = False
    fraqueza_extrema: bool = False
    palidez_extrema: bool = False
    
    def get_red_flag_symptoms(self) -> List[str]:
        """Retorna sintomas que indicam emergência (vermelho)"""
        red_flags = []
        if self.dor_peito:
            red_flags.append("Dor no peito")
        if self.dificuldade_respiratoria:
            red_flags.append("Dificuldade respiratória")
        if self.convulsoes:
            red_flags.append("Convulsões")
        if self.sangramento_ativo:
            red_flags.append("Sangramento ativo")
        if self.perda_consciencia:
            red_flags.append("Perda de consciência")
        if self.dor_cabeca_intensa:
            red_flags.append("Dor de cabeça intensa")
        return red_flags

@dataclass
class MedicalHistory:
    """Histórico médico do paciente"""
    doencas_cronicas: List[str] = field(default_factory=list)
    medicamentos_uso: List[str] = field(default_factory=list)
    alergias: List[str] = field(default_factory=list)
    cirurgias_anteriores: List[str] = field(default_factory=list)
    historico_familiar: Dict[str, List[str]] = field(default_factory=dict)
    
    def has_cardiac_history(self) -> bool:
        """Verifica se tem histórico cardíaco"""
        cardiac_conditions = [
            "hipertensão", "infarto", "arritmia", "angina", 
            "insuficiência cardíaca", "valvopatia"
        ]
        return any(condition.lower() in [d.lower() for d in self.doencas_cronicas] 
                  for condition in cardiac_conditions)
    
    def has_respiratory_history(self) -> bool:
        """Verifica se tem histórico respiratório"""
        respiratory_conditions = [
            "asma", "dpoc", "pneumonia", "bronquite", 
            "enfisema", "fibrose pulmonar"
        ]
        return any(condition.lower() in [d.lower() for d in self.doencas_cronicas] 
                  for condition in respiratory_conditions)

@dataclass
class Person:
    """Modelo completo de pessoa para triagem hospitalar"""
    # Identificação
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nome: str = ""
    cpf: str = ""
    rg: str = ""
    
    # Dados pessoais
    idade: int = 0
    genero: Gender = Gender.MASCULINO
    telefone: str = ""
    email: str = ""
    endereco: str = ""
    
    # Dados médicos
    sinais_vitais: Optional[VitalSigns] = None
    sintomas: Symptoms = field(default_factory=Symptoms)
    historico_medico: MedicalHistory = field(default_factory=MedicalHistory)
    
    # Dados da triagem
    data_chegada: datetime = field(default_factory=datetime.now)
    queixa_principal: str = ""
    nivel_risco: Optional[RiskLevel] = None
    prioridade: int = 0  # 1 = mais alta, 3 = mais baixa
    tempo_espera_estimado: Optional[int] = None  # em minutos
    
    # Observações
    observacoes_medicas: str = ""
    observacoes_enfermagem: str = ""
    
    def __post_init__(self):
        """Validações e configurações iniciais"""
        if self.idade < 0 or self.idade > 120:
            raise ValueError("Idade deve estar entre 0 e 120 anos")
        
        # Configurar prioridade baseada no nível de risco
        if self.nivel_risco:
            if self.nivel_risco == RiskLevel.VERMELHO:
                self.prioridade = 1
                self.tempo_espera_estimado = 0
            elif self.nivel_risco == RiskLevel.AMARELO:
                self.prioridade = 2
                self.tempo_espera_estimado = 60
            elif self.nivel_risco == RiskLevel.VERDE:
                self.prioridade = 3
                self.tempo_espera_estimado = 240
    
    def is_emergency_case(self) -> bool:
        """Verifica se é caso de emergência (vermelho)"""
        if not self.sinais_vitais:
            return False
        
        # Critérios de sinais vitais para emergência
        emergency_vitals = (
            self.sinais_vitais.pressao_sistolica < 90 or 
            self.sinais_vitais.pressao_sistolica > 180 or
            self.sinais_vitais.saturacao_oxigenio < 90 or
            self.sinais_vitais.frequencia_cardiaca < 50 or
            self.sinais_vitais.frequencia_cardiaca > 120 or
            self.sinais_vitais.temperatura > 39.0
        )
        
        # Critérios de sintomas para emergência
        emergency_symptoms = len(self.sintomas.get_red_flag_symptoms()) > 0
        
        return emergency_vitals or emergency_symptoms
    
    def calculate_risk_score(self) -> float:
        """Calcula score de risco (0-10)"""
        score = 0.0
        
        if not self.sinais_vitais:
            return score
        
        # Idade (0-2 pontos)
        if self.idade > 65:
            score += 2
        elif self.idade > 50:
            score += 1
        
        # Sinais vitais (0-4 pontos)
        if self.sinais_vitais.pressao_sistolica < 90 or self.sinais_vitais.pressao_sistolica > 180:
            score += 2
        if self.sinais_vitais.saturacao_oxigenio < 90:
            score += 2
        if self.sinais_vitais.frequencia_cardiaca < 50 or self.sinais_vitais.frequencia_cardiaca > 120:
            score += 1
        if self.sinais_vitais.temperatura > 39.0:
            score += 1
        
        # Sintomas (0-3 pontos)
        red_flags = len(self.sintomas.get_red_flag_symptoms())
        if red_flags >= 3:
            score += 3
        elif red_flags >= 2:
            score += 2
        elif red_flags >= 1:
            score += 1
        
        # Histórico médico (0-1 ponto)
        if self.historico_medico.has_cardiac_history() or self.historico_medico.has_respiratory_history():
            score += 1
        
        return min(score, 10.0)  # Máximo 10 pontos
    
    def get_recommendations(self) -> List[str]:
        """Retorna recomendações baseadas no estado do paciente"""
        recommendations = []
        
        if self.nivel_risco == RiskLevel.VERMELHO:
            recommendations.extend([
                "Atendimento médico imediato",
                "Monitorização contínua dos sinais vitais",
                "Acesso venoso se necessário",
                "Oxigenoterapia se SpO2 < 90%"
            ])
        
        if self.sinais_vitais:
            if self.sinais_vitais.pressao_sistolica > 180:
                recommendations.append("Controle pressórico urgente")
            if self.sinais_vitais.saturacao_oxigenio < 90:
                recommendations.append("Suporte ventilatório")
            if self.sinais_vitais.temperatura > 39.0:
                recommendations.append("Medidas antitérmicas")
        
        if self.sintomas.dor_peito:
            recommendations.append("ECG imediato")
        if self.sintomas.dificuldade_respiratoria:
            recommendations.append("Raio-X de tórax")
        
        return recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização"""
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'idade': self.idade,
            'genero': self.genero.value,
            'nivel_risco': self.nivel_risco.value if self.nivel_risco else None,
            'prioridade': self.prioridade,
            'data_chegada': self.data_chegada.isoformat(),
            'queixa_principal': self.queixa_principal,
            'sinais_vitais': self.sinais_vitais.__dict__ if self.sinais_vitais else None,
            'sintomas': self.sintomas.__dict__,
            'risk_score': self.calculate_risk_score(),
            'is_emergency': self.is_emergency_case(),
            'recommendations': self.get_recommendations()
        }
