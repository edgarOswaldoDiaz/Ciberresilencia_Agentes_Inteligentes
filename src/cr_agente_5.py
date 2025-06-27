# ___________________________
# Agente 5 - Detect (Monitoreo): Con el uso de Inteligencia Artificial (redes neuronales, clustering) 
# para identificar anomalías en logs y tráfico, correlacionando eventos dispersos para detectar ataques avanzados.
# oswaldo.diaz@inegi.org.mx
# -*- coding: utf-8 -*-
# ___________________________
"""
Sistema de Detección de Ataques Avanzados mediante Autoencoders y Clustering
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, Input, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import seaborn as sns

# Configuración de visualización
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
np.random.seed(42)

# 1. Generación de datos sintéticos de logs y tráfico de red
def generar_datos_sinteticos(n_muestras=10000, ratio_anomalias=0.05):
    """
    Genera un dataset sintético de logs de red con características típicas
    Incluye patrones normales y 5 tipos de ataques avanzados
    """
    # Características base (comportamiento normal)
    datos = {
        'duracion': np.random.exponential(scale=0.5, size=n_muestras),
        'bytes_env': np.random.lognormal(mean=3, sigma=1.5, size=n_muestras),
        'bytes_rec': np.random.lognormal(mean=4, sigma=1.2, size=n_muestras),
        'paquetes': np.random.randint(1, 100, size=n_muestras),
        'protocolo': np.random.choice([0, 1, 2], size=n_muestras, p=[0.6, 0.3, 0.1]),
        'frecuencia': np.random.uniform(0.1, 5.0, size=n_muestras)
    }
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Generar anomalías (ataques avanzados)
    n_anomalias = int(n_muestras * ratio_anomalias)
    indices_ataque = np.random.choice(n_muestras, n_anomalias, replace=False)
    
    # Tipos de ataques (0=normal, 1-5=tipos de ataque)
    df['tipo_ataque'] = 0
    
    # Patrones de ataque específicos
    for i in indices_ataque:
        tipo_ataque = np.random.choice([1, 2, 3, 4, 5])
        df.at[i, 'tipo_ataque'] = tipo_ataque
        
        # Modificar características según tipo de ataque
        if tipo_ataque == 1:  # DDoS
            df.at[i, 'bytes_rec'] *= 50
            df.at[i, 'paquetes'] = np.random.randint(500, 1000)
            df.at[i, 'frecuencia'] *= 10
        elif tipo_ataque == 2:  # Exfiltración
            df.at[i, 'bytes_env'] *= 100
            df.at[i, 'duracion'] = np.random.uniform(10, 30)
        elif tipo_ataque == 3:  # Escaneo
            df.at[i, 'paquetes'] = np.random.randint(300, 600)
            df.at[i, 'protocolo'] = 2
        elif tipo_ataque == 4:  # Comando remoto
            df.at[i, 'frecuencia'] *= 20
            df.at[i, 'duracion'] = np.random.uniform(5, 15)
        elif tipo_ataque == 5:  # Ataque sigiloso
            df.at[i, 'bytes_rec'] *= 0.1
            df.at[i, 'bytes_env'] *= 0.1
            df.at[i, 'frecuencia'] *= 0.05
    
    return df

# 2. Preprocesamiento de datos
def preprocesar_datos(df):
    """
    Preprocesa los datos: normalización, codificación y preparación de características
    """
    # Separar características y etiquetas
    X = df.drop('tipo_ataque', axis=1)
    y = df['tipo_ataque']
    
    # Normalización de características numéricas
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, scaler

# 3. Autoencoder para detección de anomalías
def construir_autoencoder(n_caracteristicas):
    """
    Construye un autoencoder profundo para aprendizaje de representaciones normales
    """
    # Capas del encoder
    input_layer = Input(shape=(n_caracteristicas,))
    encoder = Dense(32, activation='relu')(input_layer)
    encoder = Dropout(0.2)(encoder)
    encoder = Dense(16, activation='relu')(encoder)
    encoder = Dropout(0.2)(encoder)
    cuello_botella = Dense(8, activation='relu')(encoder)
    
    # Capas del decoder
    decoder = Dense(16, activation='relu')(cuello_botella)
    decoder = Dropout(0.2)(decoder)
    decoder = Dense(32, activation='relu')(decoder)
    decoder = Dropout(0.2)(decoder)
    output_layer = Dense(n_caracteristicas, activation='linear')(decoder)
    
    # Modelo completo
    autoencoder = Model(inputs=input_layer, outputs=output_layer)
    encoder_model = Model(inputs=input_layer, outputs=cuello_botella)
    
    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder, encoder_model

# 4. Clustering para correlación de eventos
def detectar_patrones_ocultos(representaciones, eps=0.5, min_samples=5):
    """
    Detecta patrones ocultos usando DBSCAN para agrupar eventos dispersos
    """
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(representaciones)
    etiquetas = clustering.labels_
    return etiquetas

# 5. Visualización de resultados
def visualizar_resultados(X, errores, etiquetas_cluster, y_real, umbral):
    """
    Visualiza los resultados de detección y clustering
    """
    # Visualización de errores de reconstrucción
    plt.figure(figsize=(14, 6))
    
    plt.subplot(1, 2, 1)
    sns.histplot(errores, bins=50, kde=True)
    plt.axvline(umbral, color='r', linestyle='--', label=f'Umbral: {umbral:.2f}')
    plt.title('Distribución de Errores de Reconstrucción')
    plt.xlabel('Error MSE')
    plt.legend()
    
    # Visualización de clusters (usando PCA para reducción dimensional)
    pca = PCA(n_components=2)
    componentes = pca.fit_transform(X)
    
    plt.subplot(1, 2, 2)
    scatter = plt.scatter(
        componentes[:, 0], 
        componentes[:, 1], 
        c=etiquetas_cluster, 
        cmap='viridis',
        alpha=0.6,
        s=10
    )
    plt.colorbar(scatter, label='Cluster')
    plt.title('Agrupación de Eventos por Patrón Oculto')
    plt.xlabel('Componente PCA 1')
    plt.ylabel('Componente PCA 2')
    
    # Resaltar ataques reales
    ataque_idx = np.where(y_real > 0)[0]
    plt.scatter(
        componentes[ataque_idx, 0], 
        componentes[ataque_idx, 1], 
        edgecolors='red', 
        facecolors='none',
        s=50,
        label='Ataques Reales'
    )
    plt.legend()
    plt.tight_layout()
    plt.show()

# --- Pipeline Principal ---
if __name__ == "__main__":
    # Paso 1: Generar datos sintéticos
    print("Generando datos sintéticos...")
    df = generar_datos_sinteticos(n_muestras=15000, ratio_anomalias=0.07)
    
    # Paso 2: Preprocesamiento
    print("Preprocesando datos...")
    X, y, scaler = preprocesar_datos(df)
    
    # Paso 3: Entrenar Autoencoder
    print("Construyendo y entrenando autoencoder...")
    autoencoder, encoder = construir_autoencoder(X.shape[1])
    
    # Dividir datos (solo datos normales para entrenamiento)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_train_normal = X_train[y_train == 0]
    
    # Entrenamiento
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    historia = autoencoder.fit(
        X_train_normal, X_train_normal,
        epochs=100,
        batch_size=128,
        validation_split=0.15,
        callbacks=[early_stop],
        verbose=1
    )
    
    # Paso 4: Detección de anomalías
    print("Detectando anomalías...")
    reconstrucciones = autoencoder.predict(X_test)
    errores = np.mean(np.square(X_test - reconstrucciones), axis=1)
    
    # Calcular umbral dinámico (percentil 95)
    umbral = np.percentile(errores, 95)
    anomalias = errores > umbral
    
    # Evaluar rendimiento
    y_test_bin = (y_test > 0).astype(int)
    print("\nReporte de Detección de Anomalías:")
    print(classification_report(y_test_bin, anomalias))
    
    # Paso 5: Extraer representaciones latentes
    print("Extrayendo representaciones latentes...")
    representaciones = encoder.predict(X_test)
    
    # Paso 6: Detectar patrones ocultos con clustering
    print("Detectando patrones ocultos con DBSCAN...")
    etiquetas_cluster = detectar_patrones_ocultos(representaciones, eps=0.8, min_samples=3)
    
    # Identificar clusters relacionados con ataques
    cluster_ataque = []
    for cluster_id in np.unique(etiquetas_cluster):
        if cluster_id == -1:  # Ruido
            continue
        indices_cluster = np.where(etiquetas_cluster == cluster_id)[0]
        ratio_ataque = np.mean(y_test.iloc[indices_cluster] > 0)
        if ratio_ataque > 0.7:  # Clusters con >70% de ataques
            cluster_ataque.append(cluster_id)
    
    print(f"\nClusters maliciosos detectados: {cluster_ataque}")
    
    # Paso 7: Visualización
    print("Visualizando resultados...")
    visualizar_resultados(X_test, errores, etiquetas_cluster, y_test, umbral)
    
    # Paso 8: Sistema integrado de alerta
    print("\nSistema de Alerta Integrado:")
    for i in np.where(anomalias)[0]:
        cluster_id = etiquetas_cluster[i]
        tipo_ataque = y_test.iloc[i]
        if cluster_id in cluster_ataque:
            print(f"[ALERTA CRÍTICA] Evento {i} - Cluster {cluster_id}: "
                  f"Ataque de tipo {tipo_ataque} (Confianza: {errores[i]:.2f})")
        elif anomalias[i]:
            print(f"[ALERTA] Evento {i}: Comportamiento anómalo detectado "
                  f"(Error: {errores[i]:.2f})")