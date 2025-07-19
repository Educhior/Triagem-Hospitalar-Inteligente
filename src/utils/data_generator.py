
            
# Gerar dados baseados no perfil de risco
def generate_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
data = []
for _ in range(n_samples):
    risk_level = np.random.choice(
        list(self.risk_profiles.keys()),
        p=[profile['weight'] for profile in self.risk_profiles.values()]
    )
    patient_data = self._generate_patient_data(risk_level)
    patient_data['risk_level'] = risk_level
    data.append(patient_data)
df = pd.DataFrame(data)
# Adicionar variações e ruído para tornar mais realista
df = self._add_realistic_variations(df)
return df

def _generate_patient_data(self, risk_level: str) -> Dict:
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
