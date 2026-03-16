
# Peplink-Wifi-Toggle-V2

Automatically enables/disables Peplink Wi-Fi AP based on GPS speed.

- Enables Wi-Fi when speed stays below `STOP_THRESHOLD` for `STOP_SAMPLES` checks.
- Disables Wi-Fi when speed stays at/above `MOVE_THRESHOLD` for `MOVE_SAMPLES` checks.

---

# There are 4 ways to run this:


## Option 1. Use the [Ready-Made Image from Docker Hub](https://hub.docker.com/r/audxiusgithub/peplinkwifitogglev2) (No Build)

Just run this command (replace username/password):

```bash
docker run -d \
	--name peplinkgps \
	-e USERNAME=USERNAME \
	-e PASSWORD=PASSWORD \
	audxiusgithub/peplinkwifitogglev2:stable
```

For advanced settings, add more environment variables:

```bash
docker run -d \
	--name peplinkgps \
	-e ROUTER_URL=https://192.168.50.1 \
	-e USERNAME=USERNAME \
	-e PASSWORD=PASSWORD \
	-e HTTP_TIMEOUT=8 \
	-e POLL_INTERVAL=10 \
	-e STOP_THRESHOLD=1.0 \
	-e MOVE_THRESHOLD=1.0 \
	-e STOP_SAMPLES=5 \
	-e MOVE_SAMPLES=3 \
	audxiusgithub/peplinkwifitogglev2:stable
```

View logs:

```bash
docker logs -f peplinkgps
```

---


## Option 2. Download a Prebuilt Image for Your Architecture (No Build, No Docker Hub)

If you don't want to build or use Docker Hub, just download a prebuilt image for your platform from the [GitHub Releases](https://github.com/Audxius/Peplink-Wifi-Toggle-V2/releases/tag/Release) page. Download the `.tar` file for your architecture, then load it with:
```bash
docker load -i peplinkwifitogglev2-amd64-local.tar
```
Replace `amd64` with `arm64`, or `armv7` if needed.

Run it (replace `amd64` tag if you loaded for `arm64` or `armv7`):
```bash
docker run -d \
	--name peplinkgps \
	-e USERNAME=USERNAME \
	-e PASSWORD=PASSWORD \
	peplinkwifitogglev2:amd64-local
```

View logs:
```bash
docker logs -f peplinkgps
```

---

## Option 3. Build Your Own Image Locally (No Docker Hub)

### How to check your architecture

```bash
uname -m
```
- `x86_64` → amd64
- `aarch64` or `arm64` → arm64
- `armv7l` → armv7

Pick the matching build command below:

### For most Intel/AMD PCs (amd64):
```bash
docker buildx build --platform linux/amd64 -t peplinkwifitogglev2:amd64-local --load .
```

### For Raspberry Pi 4/5 64-bit, Apple Silicon (arm64):
```bash
docker buildx build --platform linux/arm64 -t peplinkwifitogglev2:arm64-local --load .
```

### For older 32-bit ARM devices (armv7):
```bash
docker buildx build --platform linux/arm/v7 -t peplinkwifitogglev2:armv7-local --load .
```

Run it (replace `amd64` tag if you built for arm64 or armv7):
```bash
docker run -d \
	--name peplinkgps \
	-e USERNAME=USERNAME \
	-e PASSWORD=PASSWORD \
	peplinkwifitogglev2:amd64-local
```

View logs:
```bash
docker logs -f peplinkgps
```

To transfer to another PC (replace `amd64` tag if you built for arm64 or armv7):
```bash
docker image save peplinkwifitogglev2:amd64-local -o peplinkwifitogglev2-amd64-local.tar
```
Copy the `.tar` file, then load it on the other PC (replace `amd64` tag if you built for arm64 or armv7):
```bash
docker load -i peplinkwifitogglev2-amd64-local.tar
```

---


## Option 4. Build and Host Your Own Image on Docker Hub

Login to Docker Hub:

```bash
docker login
```

Build and push multi-arch image:

```bash
docker buildx build \
	--platform linux/amd64,linux/arm64,linux/arm/v7 \
	-t YOUR_DOCKERHUB_USERNAME/peplinkwifitogglev2:stable \
	--push .
```

Then run it anywhere:

```bash
docker run -d \
	--name peplinkgps \
	-e USERNAME=USERNAME \
	-e PASSWORD=PASSWORD \
	YOUR_DOCKERHUB_USERNAME/peplinkwifitogglev2:stable
```

---

## Environment Variables

Required:
- `USERNAME` - Router username
- `PASSWORD` - Router password

Optional:
- `ROUTER_URL` - Router API address (default: `https://192.168.50.1`)
- `HTTP_TIMEOUT` - API timeout seconds (default: `8`)
- `POLL_INTERVAL` - Seconds between checks (default: `10`)
- `STOP_THRESHOLD` - Speed below this enables Wi-Fi (default: `1.0`)
- `MOVE_THRESHOLD` - Speed at or above this disables Wi-Fi (default: `1.0`)
- `STOP_SAMPLES` - Consecutive low-speed checks to enable (default: `5`)
- `MOVE_SAMPLES` - Consecutive high-speed checks to disable (default: `3`)

---

## Useful Docker Commands

View logs:
```bash
docker logs -f peplinkgps
```
Start container:
```bash
docker start peplinkgps
```
List containers:
```bash
docker ps -a
```
Stop container:
```bash
docker stop peplinkgps
```
Remove container:
```bash
docker rm -f peplinkgps
```
