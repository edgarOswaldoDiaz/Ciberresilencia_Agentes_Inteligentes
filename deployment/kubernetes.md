# Instalación de Kubernetes en servidor físico 

## Requisitos previos
**Hardware mínimo**

   * CPU: 2 vCPU mínimo (recomendado 4).
   * RAM: 4 GB mínimo (recomendado 8 GB).
   * Almacenamiento: ≥ 20 GB libre.

**Red**

   * Conectividad entre todos los nodos en el puerto TCP 6443 (API server).
   * Conectividad UDP/TCP para el CNI (ej. Flannel usa UDP 8472).

**Sistema Operativo**

   * Ubuntu 24.04 LTS, actualizado y con acceso root o sudo.

**Hostname y resolución**

   * Define hostnames únicos:

     ```bash
     sudo hostnamectl set-hostname k8s-control-plane
     ```
   * Añade mapeos en `/etc/hosts` si no usas DNS interno:

     ```
     10.0.0.10   k8s-control-plane
     10.0.0.11   k8s-worker-1
     10.0.0.12   k8s-worker-2
     ```

---

## Preparar el sistema

**Actualizar paquetes**

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

**Desactivar swap**
   Kubernetes requiere swap desactivado:

   ```bash
   sudo swapoff -a
   # Para desactivar permanentemente, comenta la línea de swap en /etc/fstab
   sudo sed -i.bak '/\sswap\s/s/^/#/' /etc/fstab
   ```

**Ajustes de red (sysctl)**
   Permite al kernel procesar paquetes bridged:

   ```bash
   cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
   net.bridge.bridge-nf-call-ip6tables = 1
   net.bridge.bridge-nf-call-iptables  = 1
   net.ipv4.ip_forward                 = 1
   EOF

   sudo sysctl --system
   ```

---

## Instalar containerd

Kubernetes requiere un runtime OCI; usaremos containerd.

**Instalar dependencias**

   ```bash
   sudo apt install -y ca-certificates curl gnupg lsb-release
   ```

**Agregar repositorio de Docker (para containerd)**

   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
     | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
     https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" \
     | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   ```

**Instalar containerd**

   ```bash
   sudo apt install -y containerd.io
   ```

**Configurar containerd y reiniciar**

   ```bash
   sudo mkdir -p /etc/containerd
   sudo containerd config default | sudo tee /etc/containerd/config.toml
   # Opcional: en config.toml, asegúrate que use cgroup v2 si aplica.
   sudo systemctl restart containerd
   sudo systemctl enable containerd
   ```

---

## Instalar kubeadm, kubelet y kubectl

**Agregar repositorio de Kubernetes**

   ```bash
   curl -fsSL https://dl.k8s.io/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg
   echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" \
     | sudo tee /etc/apt/sources.list.d/kubernetes.list
   sudo apt update
   ```

**Instalar paquetes**

   ```bash
   sudo apt install -y kubelet kubeadm kubectl
   sudo apt-mark hold kubelet kubeadm kubectl
   ```

**Verificar versiones**

   ```bash
   kubeadm version
   kubelet --version
   kubectl version --client
   ```

---

## Inicializar el nodo de control (Control Plane)

En el **control plane** ejecuta:

```bash
sudo kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --apiserver-advertise-address=10.0.0.10
```

* `--pod-network-cidr` debe coincidir con la red del CNI (Flannel, Calico, etc.).
* `--apiserver-advertise-address` es la IP del servidor.

Cuando termine, verás instrucciones para:

**Configurar kubectl para el usuario regular**

   ```bash
   mkdir -p $HOME/.kube
   sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
   sudo chown $(id -u):$(id -g) $HOME/.kube/config
   ```

**Unir nodos de trabajo**
   Será algo como:

   ```bash
   kubeadm join 10.0.0.10:6443 --token <token> \
     --discovery-token-ca-cert-hash sha256:<hash>
   ```

Guardar ese comando: lo usarás en cada worker.

---

## Instalar una red de pods (CNI)

Ejemplo con **Flannel**:

```bash
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```

O, si prefieres **Calico**:

```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

Verifica que los pods de CNI estén corriendo:

```bash
kubectl get pods -n kube-system
```

---

## Unir nodos de trabajo

En cada **worker node**, repite:

1. Actualiza y desactiva swap (igual que en sección 2).
2. Instala containerd y kubeadm/kubelet/kubectl (secciones 3 y 4).
3. Ejecuta el comando `kubeadm join` que generó el `kubeadm init`.
4. Habilita y arranca kubelet:

   ```bash
   sudo systemctl enable kubelet
   sudo systemctl start kubelet
   ```

Verifica en el control plane:

```bash
kubectl get nodes
```

Deberías ver tanto `k8s-control-plane` como tus `k8s-worker-*` en estado `Ready`.

---

## Post-instalación y buenas prácticas

* **Desplegar Dashboard** (opcional):

  ```bash
  kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.8.0/aio/deploy/recommended.yaml
  ```

* **RBAC y usuarios**: crea `ServiceAccounts`, roles y rolebindings según necesidades.

* **Backups**: realiza snapshots de etcd o usa Velero para respaldos.

* **Seguridad**: revisa políticas de PodSecurity y NetworkPolicy.

* **Monitoreo**: considera Prometheus + Grafana.

---

# Instalar Kubernetes contenerizado

```yaml
version: "3.8"

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

  # Ejemplo de agente (opcional – unir más agentes si quieres)
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
```

### Pasos a seguir

**Ajustar el token**

   * La primera vez que inicies, el contenedor `k3s-server` generará un token y lo mostrará en sus logs:

     ```bash
     docker-compose up -d
     docker logs k3s-server | grep "Token:"
     ```
   * Copia ese token y, en tu archivo `.env` (o exportándolo), define `K3S_TOKEN` para el agente.

**Extraer el kubeconfig**
   Una vez que el servicio esté “healthy” puedes copiar el `kubeconfig` a tu máquina local:

   ```bash
   cp kubeconfig/kubeconfig.yaml ~/.kube/config
   chmod 600 ~/.kube/config
   ```

**Verificar el clúster**

   ```bash
   kubectl get nodes
   kubectl get pods -A
   ```

---
> CIMAT - CIMPS 2025 | oswaldo.diaz@inegi.org.mx 
