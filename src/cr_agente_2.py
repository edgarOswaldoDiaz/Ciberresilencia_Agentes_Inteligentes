# ____________________________
# Agente 2 - Identify (Evaluación): Modelos de ML que analizan vulnerabilidades pasadas y predice riesgos emergentes, 
# priorizando controles según probabilidad e impacto.
# oswaldo.diaz@inegi.org.mx
# ____________________________
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

class MLAgent:
    """
    MLAgent analiza vulnerabilidades pasadas y predice riesgos emergentes,
    priorizando controles según probabilidad e impacto.
    """
    def __init__(self, data_path):
        """
        Inicializa el agente con la ruta al dataset de vulnerabilidades.
        :param data_path: Ruta al archivo CSV con datos históricos de vulnerabilidades.
        """
        self.data_path = data_path
        self.model = None
        self.controls = None

    def load_data(self):
        """
        Carga los datos de vulnerabilidades desde un CSV y muestra las primeras filas.
        """
        df = pd.read_csv(self.data_path)
        print("Datos cargados (primeras 5 filas):")
        print(df.head())
        return df

    def preprocess(self, df):
        """
        Preprocesa los datos:
        - Convierte categorías en variables dummy.
        - Llena valores faltantes con la mediana.
        - Separa características (X) y etiquetas (y) si existen.
        """
        # Suponiendo que 'risk_label' es la columna objetivo (alto, medio, bajo)
        df = df.copy()
        df.fillna(df.median(numeric_only=True), inplace=True)

        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_cols = [col for col in categorical_cols if col != 'risk_label']
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

        X = df.drop('risk_label', axis=1)
        y = df['risk_label'].map({'bajo': 0, 'medio': 1, 'alto': 2})
        return X, y

    def train_model(self, X, y):
        """
        Entrena un modelo de clasificación Random Forest para predecir niveles de riesgo.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                            test_size=0.3, 
                                                            random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print(classification_report(y_test, y_pred, target_names=['bajo', 'medio', 'alto']))

        self.model = clf
        return clf

    def predict_risks(self, new_vuln_df):
        """
        Predice el nivel de riesgo para nuevas vulnerabilidades.
        :param new_vuln_df: DataFrame con nuevas vulnerabilidades, mismas columnas que X.
        :return: DataFrame con predicciones y puntajes.
        """
        X_new = pd.get_dummies(new_vuln_df)
        # Alinea columnas con las usadas en entrenamiento
        X_new = X_new.reindex(columns=self.model.feature_names_in_, fill_value=0)

        probs = self.model.predict_proba(X_new)
        pred_labels = self.model.predict(X_new)

        results = new_vuln_df.copy()
        results['predicted_risk'] = pred_labels
        # Tomamos la probabilidad de la clase alta (índice 2)
        results['probability'] = probs[:, 2]
        return results

    def prioritize_controls(self, results_df, controls_mapping):
        """
        Prioriza controles basados en probabilidad e impacto.
        :param results_df: DataFrame con columnas 'predicted_risk' y 'probability'.
        :param controls_mapping: dict que mapea nivel de riesgo a lista de controles posibles y su impacto.
                                 Ej: {'alto': [('ControlA', 5), ('ControlB', 4)], ...}
        :return: DataFrame con controles priorizados.
        """
        prioritized_list = []
        for _, row in results_df.iterrows():
            risk_level = ['bajo','medio','alto'][row['predicted_risk']]
            prob = row['probability']
            controls = controls_mapping.get(risk_level, [])
            # Calcular puntaje de control = probabilidad * impacto
            scored = [(ctrl, prob * impacto) for ctrl, impacto in controls]
            # Orden descendente de puntaje
            scored.sort(key=lambda x: x[1], reverse=True)
            prioritized_list.append(scored)

        results_df['prioritized_controls'] = prioritized_list
        return results_df

if __name__ == "__main__":
    # Ejemplo de uso
    agent = MLAgent(data_path='vulnerabilidades_historicas.csv')
    df = agent.load_data()
    X, y = agent.preprocess(df)
    agent.train_model(X, y)

    # Nuevas vulnerabilidades a evaluar
    nuevas = pd.DataFrame([
        {'severity_score': 7.2, 'exploit_count': 3, 'category': 'web'},
        {'severity_score': 4.1, 'exploit_count': 1, 'category': 'network'}
    ])

    results = agent.predict_risks(nuevas)
    controls_map = {
        'alto': [('WAF', 5), ('Patch immediately', 4)],
        'medio': [('Monitor traffic', 3), ('Apply updates', 2)],
        'bajo': [('Document', 1)]
    }
    prioritized = agent.prioritize_controls(results, controls_map)
    print(prioritized)
