"""
Exemplo de uso do modelo Person com DAO em estágio vermelho
Demonstra como criar, gerenciar e consultar pacientes de emergência
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.models import (
    Person, VitalSigns, Symptoms, MedicalHistory, 
    RiskLevel, Gender, InMemoryPersonDAO, FilePersonDAO, 
    EmergencyPersonService
)

def create_emergency_patient_example():
    """Exemplo de criação de paciente de emergência"""
    print("=== Criando Paciente de Emergência ===\n")
    
    # Criar sinais vitais críticos
    vital_signs = VitalSigns(
        pressao_sistolica=70,  # Hipotensão severa
        pressao_diastolica=40,
        frequencia_cardiaca=140,  # Taquicardia
        saturacao_oxigenio=85,    # Hipoxemia
        temperatura=39.5,         # Febre alta
        dor_escala=9,            # Dor intensa
        nivel_consciencia="Confuso"
    )
    
    # Criar sintomas de emergência
    symptoms = Symptoms(
        dor_peito=True,
        dificuldade_respiratoria=True,
        palidez_extrema=True,
        fraqueza_extrema=True,
        tontura=True
    )
    
    # Criar histórico médico
    medical_history = MedicalHistory(
        doencas_cronicas=["Hipertensão", "Diabetes"],
        medicamentos_uso=["Losartana", "Metformina"],
        alergias=["Penicilina"],
        cirurgias_anteriores=["Apendicectomia"]
    )
    
    # Criar pessoa
    person = Person(
        nome="João Silva",
        cpf="123.456.789-00",
        idade=65,
        genero=Gender.MASCULINO,
        telefone="(11) 99999-9999",
        queixa_principal="Dor no peito intensa e falta de ar",
        sinais_vitais=vital_signs,
        sintomas=symptoms,
        historico_medico=medical_history,
        nivel_risco=RiskLevel.VERMELHO
    )
    
    print(f"Paciente criado: {person.nome}")
    print(f"ID: {person.id}")
    print(f"Nível de risco: {person.nivel_risco.value}")
    print(f"Prioridade: {person.prioridade}")
    print(f"É emergência: {person.is_emergency_case()}")
    print(f"Score de risco: {person.calculate_risk_score():.1f}/10")
    print(f"Tempo de espera estimado: {person.tempo_espera_estimado} minutos")
    
    print("\n=== Sintomas de Alerta ===")
    red_flags = person.sintomas.get_red_flag_symptoms()
    for symptom in red_flags:
        print(f"- {symptom}")
    
    print("\n=== Recomendações ===")
    recommendations = person.get_recommendations()
    for rec in recommendations:
        print(f"- {rec}")
    
    return person

def dao_operations_example():
    """Exemplo de operações com DAO"""
    print("\n\n=== Operações com DAO ===\n")
    
    # Usar DAO em memória
    dao = InMemoryPersonDAO()
    emergency_service = EmergencyPersonService(dao)
    
    # Criar múltiplos pacientes de emergência
    patients = []
    
    # Paciente 1: Infarto agudo
    patient1 = emergency_service.create_emergency_patient(
        nome="Maria Santos",
        idade=55,
        cpf="987.654.321-00",
        queixa_principal="Dor no peito irradiando para braço esquerdo"
    )
    
    emergency_service.add_vital_signs(
        patient1,
        pressao_sistolica=85,
        pressao_diastolica=50,
        frequencia_cardiaca=110,
        saturacao_oxigenio=92,
        temperatura=36.5
    )
    
    emergency_service.add_symptoms(
        patient1,
        dor_peito=True,
        palidez_extrema=True,
        fraqueza_extrema=True
    )
    
    # Paciente 2: Crise asmática severa
    patient2 = emergency_service.create_emergency_patient(
        nome="Carlos Oliveira",
        idade=40,
        cpf="456.789.123-00",
        queixa_principal="Falta de ar severa"
    )
    
    emergency_service.add_vital_signs(
        patient2,
        pressao_sistolica=130,
        pressao_diastolica=80,
        frequencia_cardiaca=125,
        saturacao_oxigenio=88,
        temperatura=37.0
    )
    
    emergency_service.add_symptoms(
        patient2,
        dificuldade_respiratoria=True,
        palidez_extrema=True
    )
    
    # Paciente 3: Convulsão
    patient3 = emergency_service.create_emergency_patient(
        nome="Ana Costa",
        idade=28,
        cpf="789.123.456-00",
        queixa_principal="Convulsão tônico-clônica"
    )
    
    emergency_service.add_vital_signs(
        patient3,
        pressao_sistolica=160,
        pressao_diastolica=100,
        frequencia_cardiaca=95,
        saturacao_oxigenio=94,
        temperatura=38.8
    )
    
    emergency_service.add_symptoms(
        patient3,
        convulsoes=True,
        perda_consciencia=True
    )
    
    # Salvar pacientes
    patients = [patient1, patient2, patient3]
    for patient in patients:
        emergency_service.save_emergency_patient(patient)
        print(f"Paciente salvo: {patient.nome} (Score: {patient.calculate_risk_score():.1f})")
    
    # Consultar fila de emergência
    print("\n=== Fila de Emergência (Ordenada por Prioridade) ===")
    emergency_queue = emergency_service.get_emergency_queue()
    for i, patient in enumerate(emergency_queue, 1):
        print(f"{i}. {patient.nome} - Score: {patient.calculate_risk_score():.1f} - "
              f"Chegada: {patient.data_chegada.strftime('%H:%M:%S')}")
    
    # Pacientes críticos
    print("\n=== Pacientes Críticos (Score > 7) ===")
    critical_patients = emergency_service.get_critical_patients()
    for patient in critical_patients:
        print(f"- {patient.nome} (Score: {patient.calculate_risk_score():.1f})")
    
    # Estatísticas de emergência
    print("\n=== Estatísticas de Emergência ===")
    stats = emergency_service.get_emergency_stats()
    print(f"Total de pacientes de emergência: {stats['total_emergency']}")
    print(f"Pacientes críticos: {stats['critical_count']}")
    print(f"Score médio de risco: {stats['average_risk_score']:.1f}")
    print(f"Score máximo de risco: {stats['max_risk_score']:.1f}")
    print(f"Tempo máximo de espera: {stats['oldest_patient_waiting']:.1f} minutos")
    print(f"Tempo médio de espera: {stats['average_waiting_time']:.1f} minutos")
    
    return patients

def file_persistence_example():
    """Exemplo de persistência em arquivo"""
    print("\n\n=== Persistência em Arquivo ===\n")
    
    # Criar DAO com persistência em arquivo
    file_dao = FilePersonDAO("data/emergency_patients.json")
    emergency_service = EmergencyPersonService(file_dao)
    
    # Criar paciente de emergência
    patient = emergency_service.create_emergency_patient(
        nome="Pedro Almeida",
        idade=72,
        cpf="321.654.987-00",
        queixa_principal="Dor abdominal intensa"
    )
    
    # Adicionar dados críticos
    emergency_service.add_vital_signs(
        patient,
        pressao_sistolica=190,  # Hipertensão severa
        pressao_diastolica=110,
        frequencia_cardiaca=100,
        saturacao_oxigenio=96,
        temperatura=37.8
    )
    
    emergency_service.add_symptoms(
        patient,
        dor_abdominal=True,
        vomito=True,
        palidez_extrema=True
    )
    
    # Salvar no arquivo
    success = emergency_service.save_emergency_patient(patient)
    print(f"Paciente salvo em arquivo: {success}")
    print(f"Arquivo: data/emergency_patients.json")
    
    # Verificar se foi salvo
    retrieved_patient = file_dao.get_by_id(patient.id)
    if retrieved_patient:
        print(f"Paciente recuperado: {retrieved_patient.nome}")
        print(f"Score de risco: {retrieved_patient.calculate_risk_score():.1f}")
    
    return patient

def main():
    """Função principal com exemplos"""
    print("Sistema de Triagem Hospitalar - Modelo Person com DAO")
    print("=" * 60)
    
    # Exemplo 1: Criar paciente de emergência
    emergency_patient = create_emergency_patient_example()
    
    # Exemplo 2: Operações com DAO
    dao_patients = dao_operations_example()
    
    # Exemplo 3: Persistência em arquivo
    file_patient = file_persistence_example()
    
    print("\n\n=== Resumo dos Exemplos ===")
    print("✅ Modelo Person criado com validações")
    print("✅ DAO implementado (em memória e arquivo)")
    print("✅ Serviço de emergência especializado")
    print("✅ Exemplos de pacientes em estágio vermelho")
    print("✅ Persistência e recuperação de dados")
    print("✅ Cálculo automático de scores de risco")
    print("✅ Fila de prioridade para emergências")

if __name__ == "__main__":
    main()
