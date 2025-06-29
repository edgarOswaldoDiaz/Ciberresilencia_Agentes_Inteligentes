# Install Podman 
## Step 1: Update your system’s package index and upgrade installed packages

Open a terminal and run:

```bash
sudo apt update
sudo apt upgrade -y
```

This ensures you have the latest package listings and security updates before installing new software. ([idroot.us][1], [docs.vultr.com][2])

## Step 2: Install Podman

With your system up‑to‑date, install Podman directly from Ubuntu’s official repositories:

```bash
sudo apt install -y podman
```

Since Ubuntu 20.10, Podman has been included in the default package sources, so this single command pulls in everything you need. ([idroot.us][1])

## Step 3: Verify the installation

Check that Podman installed correctly by querying its version:

```bash
podman --version
```

You should see output like `podman version 4.x.x` confirming the install. ([idroot.us][1])

## Step 4: Run a test container

Finally, test Podman by running a simple OCI container:

```bash
podman run --rm docker.io/library/ubuntu:24.04 echo "Hello from Podman!"
```

You should see `Hello from Podman!` printed, demonstrating that Podman can pull and run containers rootlessly by default. ([devtutorial.io][3])

---

Once these steps are complete, Podman is ready to use on your Ubuntu 24.04 system. You can explore additional features such as `podman pod`, `podman build`, or integrating with Docker Compose using `podman-compose`.

[1]: https://idroot.us/install-podman-ubuntu-24-04/?utm_source=chatgpt.com "How To Install Podman on Ubuntu 24.04 LTS - idroot"
[2]: https://docs.vultr.com/how-to-install-podman-on-ubuntu-24-04?utm_source=chatgpt.com "How to Install Podman on Ubuntu 24.04 - Vultr"
[3]: https://devtutorial.io/how-to-install-and-use-podman-on-ubuntu-24-04-p3481.html?utm_source=chatgpt.com "How to Install and Use Podman on Ubuntu 24.04 - Devtutorial"
