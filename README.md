# Cyber Resilience with Intelligent Agents 

Generar una plataforma computacional que considere componentes con licenciamiento tipo “open source” considerando la siguiente distribución.

- **Ingesta**: utilizando (Apache Kafka, Apache NiFi) para orquestar grandes flujos de datos de forma tolerante a fallos.
- **Procesamiento**: utilizando (Apache Spark) y agentes inteligentes basados en Python PyTorch/TensorFlow para detección y respuesta automatizada de incidentes.
- **Almacenamiento**: Para tener acceso al Data Lake con MinIO y/o HDFS, para procesar de forma paralela grandes volúmenes de datos no estructurados, así como también generar catálogos gestionados con Open Metadata.
- **Orquestación de contenedores**: configurar un clúester que permita orquestación con Kubernetes para despliegue distribuido y escalable de servicios y/o microservicios y agentes, con apoyo de Apache Airflow para flujos de remediación.
- **Monitoreo y observabilidad**: Configurar herramientas que permiten visualización de grandes volúmenes de datos como Prometheus para métricas y Grafana para tableros de control (dashboards), definiendo los umbrales para niveles de servicio (SLA´s) y niveles de operación (OLA´s).
- **Construcción de servicios y/o microservicios**: empaquetar cada agente en contenedores apoyándose de las herramientas como Podman engine o Docker engine.
- **Realizar pruebas** de penetración y análisis de vulnerabilidades de los entornos contenerizados con las herramientas (OWASP ZAP, Trivy).
- **Generar Pipelines CI/CD Automatizados con base en repositorios Git**: GitLab/GitHub con flujos de procesamiento distribuido realizando procesos de DevSecOps & DataSecOps
- **Firmado de imágenes de contenedores** en un repositorio de “registro” utilizando (Notary, Cosign).

________________
> CIMAT - CIMPS 2025 | oswaldo.diaz@inegi.org.mx  

