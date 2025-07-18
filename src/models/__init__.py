"""
Módulo de modelos para o Sistema de Triagem Hospitalar
"""

from .person import Person, VitalSigns, Symptoms, MedicalHistory, RiskLevel, Gender
from .person_dao import PersonDAO, InMemoryPersonDAO, FilePersonDAO, EmergencyPersonService

__all__ = [
    'Person',
    'VitalSigns', 
    'Symptoms',
    'MedicalHistory',
    'RiskLevel',
    'Gender',
    'PersonDAO',
    'InMemoryPersonDAO',
    'FilePersonDAO',
    'EmergencyPersonService'
]
