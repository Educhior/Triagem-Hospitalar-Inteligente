from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os
from abc import ABC, abstractmethod

from .person import Person, RiskLevel, Gender, VitalSigns, Symptoms, MedicalHistory

class PersonDAO(ABC):
    
    @abstractmethod
    def save(self, person: Person) -> bool:
        pass
    
    @abstractmethod
    def get_by_id(self, person_id: str) -> Optional[Person]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Person]:
        pass
    
    @abstractmethod
    def update(self, person: Person) -> bool:
        pass
    
    @abstractmethod
    def delete(self, person_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_by_risk_level(self, risk_level: RiskLevel) -> List[Person]:
        pass

class InMemoryPersonDAO(PersonDAO):
    
    def __init__(self):
        self._data: Dict[str, Person] = {}
    
    def save(self, person: Person) -> bool:
        try:
            self._data[person.id] = person
            return True
        except Exception as e:
            print(f"Erro ao salvar pessoa: {e}")
            return False
    
    def get_by_id(self, person_id: str) -> Optional[Person]:
        return self._data.get(person_id)
    
    def get_all(self) -> List[Person]:
        return list(self._data.values())
    
    def update(self, person: Person) -> bool:
        if person.id in self._data:
            self._data[person.id] = person
            return True
        return False
    
    def delete(self, person_id: str) -> bool:
        if person_id in self._data:
            del self._data[person_id]
            return True
        return False
    
    def get_by_risk_level(self, risk_level: RiskLevel) -> List[Person]:
        return [person for person in self._data.values() 
                if person.nivel_risco == risk_level]
    
    def get_emergency_queue(self) -> List[Person]:
        emergency_patients = self.get_by_risk_level(RiskLevel.VERMELHO)
        return sorted(emergency_patients, key=lambda p: p.data_chegada)
    
    def get_waiting_time_stats(self) -> Dict[str, Any]:
        patients = self.get_all()
        if not patients:
            return {}
        
        now = datetime.now()
        waiting_times = [(now - p.data_chegada).total_seconds() / 60 
                        for p in patients]
        
        return {
            'total_patients': len(patients),
            'average_waiting_time': sum(waiting_times) / len(waiting_times),
            'max_waiting_time': max(waiting_times),
            'min_waiting_time': min(waiting_times),
            'emergency_count': len(self.get_by_risk_level(RiskLevel.VERMELHO)),
            'urgent_count': len(self.get_by_risk_level(RiskLevel.AMARELO)),
            'non_urgent_count': len(self.get_by_risk_level(RiskLevel.VERDE))
        }

class FilePersonDAO(PersonDAO):
    
    def __init__(self, file_path: str = "data/persons.json"):
        self.file_path = file_path
        self._ensure_directory()
        self._load_data()
    
    def _ensure_directory(self):
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _load_data(self) -> Dict[str, Dict]:
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return {}
    
    def _save_data(self, data: Dict[str, Dict]) -> bool:
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False
    
    def _dict_to_person(self, data: Dict) -> Person:
        vital_signs = None
        if data.get('sinais_vitais'):
            vital_signs = VitalSigns(**data['sinais_vitais'])
        
        symptoms = Symptoms(**data.get('sintomas', {}))
        
        medical_history = MedicalHistory(**data.get('historico_medico', {}))
        
        person_data = data.copy()
        person_data['sinais_vitais'] = vital_signs
        person_data['sintomas'] = symptoms
        person_data['historico_medico'] = medical_history
        person_data['genero'] = Gender(data.get('genero', 'M'))
        person_data['data_chegada'] = datetime.fromisoformat(data.get('data_chegada', datetime.now().isoformat()))
        
        if data.get('nivel_risco'):
            person_data['nivel_risco'] = RiskLevel(data['nivel_risco'])
        
        return Person(**person_data)
    
    def _person_to_dict(self, person: Person) -> Dict:
        data = {
            'id': person.id,
            'nome': person.nome,
            'cpf': person.cpf,
            'rg': person.rg,
            'idade': person.idade,
            'genero': person.genero.value,
            'telefone': person.telefone,
            'email': person.email,
            'endereco': person.endereco,
            'data_chegada': person.data_chegada.isoformat(),
            'queixa_principal': person.queixa_principal,
            'nivel_risco': person.nivel_risco.value if person.nivel_risco else None,
            'prioridade': person.prioridade,
            'tempo_espera_estimado': person.tempo_espera_estimado,
            'observacoes_medicas': person.observacoes_medicas,
            'observacoes_enfermagem': person.observacoes_enfermagem,
            'sinais_vitais': person.sinais_vitais.__dict__ if person.sinais_vitais else None,
            'sintomas': person.sintomas.__dict__,
            'historico_medico': person.historico_medico.__dict__
        }
        return data
    
    def save(self, person: Person) -> bool:
        try:
            data = self._load_data()
            data[person.id] = self._person_to_dict(person)
            return self._save_data(data)
        except Exception as e:
            print(f"Erro ao salvar pessoa: {e}")
            return False
    
    def get_by_id(self, person_id: str) -> Optional[Person]:
        try:
            data = self._load_data()
            if person_id in data:
                return self._dict_to_person(data[person_id])
            return None
        except Exception as e:
            print(f"Erro ao buscar pessoa: {e}")
            return None
    
    def get_all(self) -> List[Person]:
        try:
            data = self._load_data()
            return [self._dict_to_person(person_data) for person_data in data.values()]
        except Exception as e:
            print(f"Erro ao buscar todas as pessoas: {e}")
            return []
    
    def update(self, person: Person) -> bool:
        try:
            data = self._load_data()
            if person.id in data:
                data[person.id] = self._person_to_dict(person)
                return self._save_data(data)
            return False
        except Exception as e:
            print(f"Erro ao atualizar pessoa: {e}")
            return False
    
    def delete(self, person_id: str) -> bool:
        try:
            data = self._load_data()
            if person_id in data:
                del data[person_id]
                return self._save_data(data)
            return False
        except Exception as e:
            print(f"Erro ao remover pessoa: {e}")
            return False
    
    def get_by_risk_level(self, risk_level: RiskLevel) -> List[Person]:
        try:
            all_persons = self.get_all()
            return [person for person in all_persons 
                    if person.nivel_risco == risk_level]
        except Exception as e:
            print(f"Erro ao buscar por nível de risco: {e}")
            return []

class EmergencyPersonService:
    
    def __init__(self, dao: PersonDAO):
        self.dao = dao
    
    def create_emergency_patient(self, nome: str, idade: int, cpf: str = "", 
                                queixa_principal: str = "") -> Person:
        person = Person(
            nome=nome,
            idade=idade,
            cpf=cpf,
            queixa_principal=queixa_principal,
            nivel_risco=RiskLevel.VERMELHO,
            data_chegada=datetime.now()
        )
        return person
    
    def add_vital_signs(self, person: Person, pressao_sistolica: float,
                       pressao_diastolica: float, frequencia_cardiaca: float,
                       saturacao_oxigenio: float, temperatura: float) -> bool:
        try:
            person.sinais_vitais = VitalSigns(
                pressao_sistolica=pressao_sistolica,
                pressao_diastolica=pressao_diastolica,
                frequencia_cardiaca=frequencia_cardiaca,
                saturacao_oxigenio=saturacao_oxigenio,
                temperatura=temperatura
            )
            
            # Recalcular nível de risco baseado nos sinais vitais
            if person.is_emergency_case():
                person.nivel_risco = RiskLevel.VERMELHO
            
            return self.dao.update(person)
        except Exception as e:
            print(f"Erro ao adicionar sinais vitais: {e}")
            return False
    
    def add_symptoms(self, person: Person, **symptoms) -> bool:
        try:
            for symptom, value in symptoms.items():
                if hasattr(person.sintomas, symptom):
                    setattr(person.sintomas, symptom, value)
            
            # Recalcular nível de risco baseado nos sintomas
            if person.is_emergency_case():
                person.nivel_risco = RiskLevel.VERMELHO
            
            return self.dao.update(person)
        except Exception as e:
            print(f"Erro ao adicionar sintomas: {e}")
            return False
    
    def get_emergency_queue(self) -> List[Person]:
        emergency_patients = self.dao.get_by_risk_level(RiskLevel.VERMELHO)
        return sorted(emergency_patients, key=lambda p: (
            p.calculate_risk_score(),  # Maior score primeiro
            p.data_chegada  # Mais antigo primeiro
        ), reverse=True)
    
    def get_critical_patients(self) -> List[Person]:
        emergency_patients = self.get_emergency_queue()
        return [p for p in emergency_patients if p.calculate_risk_score() > 7]
    
    def save_emergency_patient(self, person: Person) -> bool:
        person.nivel_risco = RiskLevel.VERMELHO
        return self.dao.save(person)
    
    def get_emergency_stats(self) -> Dict[str, Any]:
        emergency_patients = self.get_emergency_queue()
        critical_patients = self.get_critical_patients()
        
        if not emergency_patients:
            return {
                'total_emergency': 0,
                'critical_count': 0,
                'average_risk_score': 0,
                'oldest_patient_waiting': 0
            }
        
        risk_scores = [p.calculate_risk_score() for p in emergency_patients]
        now = datetime.now()
        waiting_times = [(now - p.data_chegada).total_seconds() / 60 
                        for p in emergency_patients]
        
        return {
            'total_emergency': len(emergency_patients),
            'critical_count': len(critical_patients),
            'average_risk_score': sum(risk_scores) / len(risk_scores),
            'max_risk_score': max(risk_scores),
            'oldest_patient_waiting': max(waiting_times),
            'average_waiting_time': sum(waiting_times) / len(waiting_times)
        }
