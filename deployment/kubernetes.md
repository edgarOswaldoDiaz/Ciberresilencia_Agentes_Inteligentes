services:
  k3s-server:
    image: rancher/k3s:v1.27.5-k3s1
    container_name: k3s-server
    privileged: true                      # necesario para acceso a cgroups y networking
    network_mode: "host"                  # expone puertos directamente en el host
    restart: unless-stopped
    environment:
      # Genera el kubeconfig en /output/kubeconfig.yaml dentro del contenedor
      K3S_KUBECONFIG_OUTPUT: "/output/kubeconfig.yaml"
      # Permisos del archivo kubeconfig
      K3S_KUBECONFIG_MODE: "644"
      # Token para unir agentes (se crea en la primera ejecución)
      # K3S_TOKEN: "cambia-esto-por-un-token-seguro"
    volumes:
      - k3s-data:/var/lib/rancher/k3s   # datos persistentes etcd, certificados, etc.
      - ./kubeconfig:/output            # volumen local para extraer el kubeconfig

  # Add agents 
  k3s-agent:
    image: rancher/k3s:v1.27.5-k3s1
    container_name: k3s-agent
    privileged: true
    network_mode: "host"
    restart: unless-stopped
    command: agent
    depends_on:
      - k3s-server
    environment:
      # Dirección del servidor y token para unirse
      K3S_URL: "https://127.0.0.1:6443"
      K3S_TOKEN: "${K3S_TOKEN}"         # debe coincidir con el del servidor
    volumes:
      - k3s-data:/var/lib/rancher/k3s

volumes:
  k3s-data:
