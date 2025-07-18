if __name__ == "__main__":
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
"""
Modelos de Machine Learning para Triagem Hospitalar
Implementação de Naive Bayes e Random Forest
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import logging

logger = logging.getLogger(__name__)

class TriageMLModel:
    """
    Modelo de Machine Learning para classificação de risco na triagem
    """
    
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
    def carregar_dados_csv(caminho_csv: str = 'data.csv') -> pd.DataFrame:
        """
        Carrega os dados do arquivo data.csv para DataFrame
        """
        df = pd.read_csv(caminho_csv)
        return df

    @classmethod
    def treinar_com_csv(cls, caminho_csv: str = 'data.csv', model_type: str = 'naive_bayes'):
        """
        Cria e treina o modelo usando os dados do data.csv
        """
        df = cls.carregar_dados_csv(caminho_csv)
        # Separar features e target
        X = df.drop(['risk_level', 'timestamp'], axis=1)
        y = df['risk_level']
        model = cls(model_type=model_type)
        resultados = model.train(X, y)
        return model, resultados
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preparar features para treinamento
        """
        try:
            # Criar features derivadas
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
        """
        Treinar o modelo
        """
        try:
            # Preparar features
            X_prepared = self.prepare_features(X)
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X_prepared, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Codificar labels
            y_train_encoded = self.label_encoder.fit_transform(y_train)
            y_test_encoded = self.label_encoder.transform(y_test)
            
            # Treinar modelo
            self.model.fit(X_train_scaled, y_train_encoded)
            self.is_trained = True
            
            # Avaliar modelo
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test_encoded, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train_encoded, cv=5)
            
            # Relatório de classificação
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
        """
        Fazer predições
        """
        try:
            if not self.is_trained:
                raise ValueError("Modelo não foi treinado")
            
            # Preparar features
            X_prepared = self.prepare_features(X)
            
            # Escalar features
            X_scaled = self.scaler.transform(X_prepared)
            
            # Fazer predição
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)
            
            # Decodificar labels
            predictions_decoded = self.label_encoder.inverse_transform(predictions)
            
            return predictions_decoded, probabilities
            
        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            return np.array([]), np.array([])
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Obter importância das features (apenas para Random Forest)
        """
        try:
            if self.model_type != 'random_forest':
                return pd.DataFrame()
            
            if not self.is_trained:
                raise ValueError("Modelo não foi treinado")
            
            # Nomes das features (assumindo ordem padrão)
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
        """
        Salvar modelo treinado
        """
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
        """
        Carregar modelo salvo
        """
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

class BayesianTriageModel:
    """
    Modelo Bayesiano especializado para triagem
    Implementa raciocínio probabilístico
    """
    
    def __init__(self):
        self.prior_probabilities = {}
        self.conditional_probabilities = {}
        self.is_trained = False
    
    def calculate_priors(self, y: pd.Series):
        """
        Calcular probabilidades a priori
        """
        try:
            total_samples = len(y)
            self.prior_probabilities = {
                risk_level: count / total_samples 
                for risk_level, count in y.value_counts().items()
            }
            
            logger.info(f"Probabilidades a priori: {self.prior_probabilities}")
            
        except Exception as e:
            logger.error(f"Erro no cálculo de priors: {e}")
    
    def calculate_likelihoods(self, X: pd.DataFrame, y: pd.Series):
        """
        Calcular verossimilhanças (P(sintoma|risco))
        """
        try:
            self.conditional_probabilities = {}
            
            for risk_level in y.unique():
                risk_data = X[y == risk_level]
                
                self.conditional_probabilities[risk_level] = {}
                
                # Para cada feature, calcular P(feature|risk_level)
                for feature in X.columns:
                    if X[feature].dtype == 'bool' or X[feature].dtype == 'int':
                        # Features categóricas/binárias
                        self.conditional_probabilities[risk_level][feature] = {
                            1: (risk_data[feature] == 1).sum() / len(risk_data),
                            0: (risk_data[feature] == 0).sum() / len(risk_data)
                        }
                    else:
                        # Features contínuas - usar distribuição normal
                        mean = risk_data[feature].mean()
                        std = risk_data[feature].std()
                        self.conditional_probabilities[risk_level][feature] = {
                            'mean': mean,
                            'std': std if std > 0 else 1e-6
                        }
            
            logger.info("Verossimilhanças calculadas")
            
        except Exception as e:
            logger.error(f"Erro no cálculo de verossimilhanças: {e}")
    
    def train(self, X: pd.DataFrame, y: pd.Series):
        """
        Treinar modelo Bayesiano
        """
        try:
            self.calculate_priors(y)
            self.calculate_likelihoods(X, y)
            self.is_trained = True
            
            logger.info("Modelo Bayesiano treinado")
            
        except Exception as e:
            logger.error(f"Erro no treinamento Bayesiano: {e}")
    
    def predict_proba(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Calcular probabilidades posteriores
        """
        try:
            if not self.is_trained:
                raise ValueError("Modelo não foi treinado")
            
            posteriors = []
            
            for _, patient in X.iterrows():
                patient_probs = {}
                
                for risk_level in self.prior_probabilities.keys():
                    # Começar com probabilidade a priori
                    prob = self.prior_probabilities[risk_level]
                    
                    # Multiplicar pelas verossimilhanças
                    for feature, value in patient.items():
                        if feature in self.conditional_probabilities[risk_level]:
                            feature_prob = self.conditional_probabilities[risk_level][feature]
                            
                            if isinstance(feature_prob, dict) and 'mean' in feature_prob:
                                # Feature contínua
                                mean = feature_prob['mean']
                                std = feature_prob['std']
                                prob *= self._normal_pdf(value, mean, std)
                            else:
                                # Feature categórica
                                prob *= feature_prob.get(int(value), 1e-6)
                    
                    patient_probs[risk_level] = prob
                
                # Normalizar probabilidades
                total_prob = sum(patient_probs.values())
                if total_prob > 0:
                    patient_probs = {k: v/total_prob for k, v in patient_probs.items()}
                
                posteriors.append(patient_probs)
            
            return pd.DataFrame(posteriors)
            
        except Exception as e:
            logger.error(f"Erro na predição Bayesiana: {e}")
            return pd.DataFrame()
    
    def _normal_pdf(self, x, mean, std):
        """
        Função densidade de probabilidade normal
        """
        return (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
