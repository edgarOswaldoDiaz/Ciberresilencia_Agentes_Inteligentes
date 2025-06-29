# Cyber Resilience with Intelligent Agents 

We need to generate a computational platform that utilizes open-source licensed components, considering the following distribution:

- Ingestion: Using Apache Kafka and Apache NiFi to orchestrate large data flows in a fault-tolerant manner.

- Processing: Utilizing Apache Spark and intelligent agents based on Python (PyTorch/TensorFlow) for automated incident detection and response.

- Storage: To access the Data Lake with MinIO and/or HDFS for parallel processing of large volumes of unstructured data, as well as generating managed catalogs with Open Metadata.

- Container Orchestration: Configure a cluster that allows orchestration with Kubernetes for distributed and scalable deployment of services, microservices, and agents, supported by Apache Airflow for remediation flows.

- Monitoring and Observability: Configure tools that enable visualization of large volumes of data, such as Prometheus for metrics and Grafana for dashboards, defining thresholds for Service Level Agreements (SLAs) and Operational Level Agreements (OLAs).

- Service and Microservice Construction: Package each agent into containers using tools like Podman engine or Docker engine.

- Perform penetration testing and vulnerability analysis of containerized environments with OWASP ZAP and Trivy.

- Generate Automated CI/CD Pipelines based on Git repositories (GitLab/GitHub) with distributed processing flows, implementing DevSecOps & DataSecOps processes.

- Sign container images in a "registry" repository using Notary and Cosign.

________________
> CIMAT - CIMPS 2025 | contact oswaldo.diaz@inegi.org.mx  

