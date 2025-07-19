if __name__ == "__main__":
    from models import TriageMLModel
    print("Treinando modelo de triagem hospitalar com dados reais (data.csv)...")
    modelo, resultados = TriageMLModel.treinar_com_csv('data.csv', model_type='random_forest')
    print("\nResumo do Treinamento:")
    print(f"Acurácia: {resultados.get('accuracy', 0):.3f}")
    print(f"Acurácia média (cross-val): {resultados.get('cv_mean', 0):.3f} ± {resultados.get('cv_std', 0):.3f}")
    print("\nMatriz de Confusão:")
    for linha in resultados.get('confusion_matrix', []):
        print(linha)
    print("\nRelatório de Classificação:")
    for classe, metrica in resultados.get('classification_report', {}).items():
        if isinstance(metrica, dict):
            print(f"Classe {classe}: precisão={metrica.get('precision', 0):.2f}, revocação={metrica.get('recall', 0):.2f}, f1={metrica.get('f1-score', 0):.2f}")
    # Exemplo de como salvar o modelo treinado
    modelo.save_model('modelo_triagem.joblib')
    print("\nModelo salvo em 'modelo_triagem.joblib'.")

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import logging

logger = logging.getLogger(__name__)

class TriageMLModel:
    # Modelo de Machine Learning para triagem hospitalar
    
    def __init__(self, model_type='naive_bayes'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
        # Inicializar modelo baseado no tipo
        if model_type == 'naive_bayes':
            self.model = GaussianNB()
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
        else:
            raise ValueError(f"Tipo de modelo não suportado: {model_type}")

    @staticmethod
    def carregar_dados_csv(caminho_csv: str = 'data_utf8.csv') -> pd.DataFrame:
        # Carrega dados de um CSV com codificação UTF-8
        try:
            df = pd.read_csv(caminho_csv, delimiter=';', encoding='latin1')
            return df
        except Exception as e:
            logger.error(f"Erro ao ler o CSV: {e}")
            raise

    @classmethod
    def treinar_com_csv(cls, caminho_csv: str = 'data_utf8.csv', model_type: str = 'naive_bayes'):
        # Treina o modelo com dados do CSV
        df = cls.carregar_dados_csv(caminho_csv)

        # Mapeamento de colunas do CSV para nomes esperados
        col_map = {
            'SBP': 'pressao_sistolica',
            'DBP': 'pressao_diastolica',
            'HR': 'frequencia_cardiaca',
            'Saturation': 'saturacao_oxigenio',
            'BT': 'temperatura',
            'Age': 'idade',
            'Sex': 'sexo_M',
            
        }
        for old, new in col_map.items():
            if old in df.columns:
                df[new] = df[old]

        # Converter sexo para binário (1 = masculino, 0 = feminino)
        if 'sexo_M' in df.columns:
            df['sexo_M'] = df['sexo_M'].apply(lambda x: 1 if str(x).strip() in ['1', 'M', 'm', 'Masculino', 'masculino'] else 0)
        else:
            df['sexo_M'] = 0

        # Criar colunas de sintomas como 0 (não presentes)
        sintomas = ['dor_peito', 'dificuldade_respiratoria', 'febre', 'tontura', 'vomito', 'dor_abdominal']
        for sint in sintomas:
            if sint not in df.columns:
                df[sint] = 0

        # Selecionar apenas as colunas numéricas esperadas pelo modelo
        features_cols = [
            'pressao_sistolica', 'pressao_diastolica', 'frequencia_cardiaca',
            'saturacao_oxigenio', 'temperatura', 'idade', 'sexo_M',
            'dor_peito', 'dificuldade_respiratoria', 'febre', 'tontura', 'vomito', 'dor_abdominal'
        ]
        X = df[features_cols].copy()
        # Converter para numérico e tratar valores inválidos
        for col in features_cols:
            X[col] = pd.to_numeric(X[col], errors='coerce')
            if X[col].isnull().any():
                mediana = X[col].median()
                X[col] = X[col].fillna(mediana)

        y = df['KTAS_RN']

        model = cls(model_type=model_type)
        resultados = model.train(X, y)
        return model, resultados
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        # Preparar features para treinamento
        try:
            features = data.copy()
            
            # Pressão arterial média
            features['pressao_media'] = (features['pressao_sistolica'] + 2 * features['pressao_diastolica']) / 3
            
            # Índice de choque (FC/PAS)
            features['indice_choque'] = features['frequencia_cardiaca'] / features['pressao_sistolica']
            
            # Score de risco por idade
            features['risco_idade'] = np.where(features['idade'] > 65, 2, 
                                             np.where(features['idade'] > 50, 1, 0))
            
            # Combinação de sintomas críticos
            features['sintomas_criticos'] = (
                features['dor_peito'].astype(int) + 
                features['dificuldade_respiratoria'].astype(int) + 
                features['febre'].astype(int)
            )
            
            logger.info(f"Features preparadas: {features.shape}")
            return features
            
        except Exception as e:
            logger.error(f"Erro na preparação das features: {e}")
            return data
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        try:
            # Treinamento do modelo
            X_prepared = self.prepare_features(X)
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_prepared, y, test_size=0.2, random_state=42, stratify=y
            )
            
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            y_train_encoded = self.label_encoder.fit_transform(y_train)
            y_test_encoded = self.label_encoder.transform(y_test)
            
            self.model.fit(X_train_scaled, y_train_encoded)
            self.is_trained = True
            
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test_encoded, y_pred)
            
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train_encoded, cv=5)
            
            report = classification_report(
                y_test_encoded, y_pred, 
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
            
            training_results = {
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': report,
                'confusion_matrix': confusion_matrix(y_test_encoded, y_pred).tolist()
            }
            
            logger.info(f"Modelo treinado com acurácia: {accuracy:.3f}")
            return training_results
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {e}")
            return {'error': str(e)}
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        # Fazer predições 
        try:
            if not self.is_trained:
                raise ValueError("Modelo não foi treinado")
            
            X_prepared = self.prepare_features(X)
            
            X_scaled = self.scaler.transform(X_prepared)
            
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)
            
            predictions_decoded = self.label_encoder.inverse_transform(predictions)
            
            return predictions_decoded, probabilities
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            return np.array([]), np.array([])
    
    def get_feature_importance(self) -> pd.DataFrame:
        try:
            if self.model_type != 'random_forest':
                return pd.DataFrame()
            
            if not self.is_trained:
                raise ValueError("Modelo não foi treinado")
            
            feature_names = [
                'pressao_sistolica', 'pressao_diastolica', 'frequencia_cardiaca',
                'saturacao_oxigenio', 'temperatura', 'idade', 'sexo_M',
                'dor_peito', 'dificuldade_respiratoria', 'febre', 'tontura',
                'vomito', 'dor_abdominal', 'pressao_media', 'indice_choque',
                'risco_idade', 'sintomas_criticos'
            ]
            
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
            
        except Exception as e:
            logger.error(f"Erro ao obter importância: {e}")
            return pd.DataFrame()
    
    def save_model(self, filepath: str):
        try:
            if not self.is_trained:
                raise ValueError("Modelo não foi treinado")
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'model_type': self.model_type,
                'is_trained': self.is_trained
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Modelo salvo em: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo: {e}")
    
    def load_model(self, filepath: str):
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoder = model_data['label_encoder']
            self.model_type = model_data['model_type']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Modelo carregado de: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")

