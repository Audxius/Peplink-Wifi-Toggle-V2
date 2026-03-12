# Peplink-Wifi-Toggle-V2

`Peplink-Wifi-Toggle-V2` automatically enables or disables your Peplink Wi-Fi Access Point based on GPS speed.

- If speed stays below `STOP_THRESHOLD` for `STOP_SAMPLES`, Wi-Fi is enabled.
- If speed stays at or above `MOVE_THRESHOLD` for `MOVE_SAMPLES`, Wi-Fi is disabled.

This project is an updated version of `audriuspeplink/peplinkgpswifishutdown` with cleaner code and bug fixes. \
Current Docker Hub repository:
`https://hub.docker.com/r/audxiusgithub/peplinkwifitogglev2`

## 1. What You Need

- Docker installed
- Access to your Peplink router API (usually `https://192.168.50.1`)
- Router username and password

Optional:
- Docker Hub account (only needed if you want to push images online)

## 2. Quick Run (Use Existing Docker Hub Image)

Bare minimum (only required values):

```bash
docker run -d \
	--name peplinkgps \
	-e USERNAME=admin \
	-e PASSWORD=Admin12345 \
	audxiusgithub/peplinkwifitogglev2:stable
```

Full example (with all common settings):

```bash
docker run -d \
	--name peplinkgps \
	-e ROUTER_URL=https://192.168.50.1 \
	-e USERNAME=[INSERT USERNAME] \
	-e PASSWORD=[INSERT PASSWORD] \
	-e HTTP_TIMEOUT=8 \
	-e POLL_INTERVAL=10 \
	-e STOP_THRESHOLD=1.0 \
	-e MOVE_THRESHOLD=1.0 \
	-e STOP_SAMPLES=5 \
	-e MOVE_SAMPLES=3 \
	audxiusgithub/peplinkwifitogglev2:stable
```

## 3. Environment Variables

Main settings:

- `ROUTER_URL`: Router API address (usually `https://192.168.50.1`)
- `USERNAME`: Router username
- `PASSWORD`: Router password

Optional settings:

- `POLL_INTERVAL`: Seconds between GPS checks (default `10`)
- `STOP_THRESHOLD`: Speed below this enables Wi-Fi (default `1.0`)
- `MOVE_THRESHOLD`: Speed at or above this disables Wi-Fi (default `1.0`)
- `STOP_SAMPLES`: Stationary readings needed before enabling (default `5`)
- `MOVE_SAMPLES`: Movement readings needed before disabling (default `3`)
- `HTTP_TIMEOUT`: API timeout in seconds (default `8`)

## 4. Build Multi-Arch Without Pushing (No Docker Hub)

Important: a true multi-arch image cannot be loaded to classic local Docker image store with one command.
For local testing, build each architecture separately and load it.

Create/use buildx builder once:

```bash
docker buildx create --name multiarch-builder --use
docker buildx inspect --bootstrap
```

Pick one architecture below and run that exact command.

### Option A: `linux/amd64` (most Intel/AMD PCs)

```bash
docker buildx build \
	--platform linux/amd64 \
	-t peplinkwifitogglev2:amd64-local \
	--load \
	.
```

### Option B: `linux/arm64` (Raspberry Pi 4/5 64-bit, Apple Silicon targets)

```bash
docker buildx build \
	--platform linux/arm64 \
	-t peplinkwifitogglev2:arm64-local \
	--load \
	.
```

### Option C: `linux/arm/v7` (older 32-bit ARM devices)

```bash
docker buildx build \
	--platform linux/arm/v7 \
	-t peplinkwifitogglev2:armv7-local \
	--load \
	.
```

If you need to build for a different architecture than your current machine, export it as a `.tar` file instead of `--load`.

Example: export `arm64` image tar:

```bash
docker buildx build \
	--platform linux/arm64 \
	-t peplinkwifitogglev2:arm64-local \
	--output type=docker,dest=./peplinkwifitogglev2-arm64.tar \
	.
```

## 5. Build Multi-Arch And Push To Docker Hub (Optional)

If you do want Docker Hub distribution:

```bash
docker login
docker buildx build \
	--platform linux/amd64,linux/arm64,linux/arm/v7 \
	-t DOCKER_HUB_USERNAME/DOCKER_HUB_REPOSITORY:stable \
	--push \
	.
```

## 6. Export Local Image To File (Transfer To Another PC)

If you built locally and want to move image to another machine:

First, check which local tag you built:

```bash
docker images | grep peplinkwifitogglev2
```

Then save the matching image to `.tar`:

For `amd64`:

```bash
docker image save peplinkwifitogglev2:amd64-local -o peplinkwifitogglev2-amd64-local.tar
```

For `arm64`:

```bash
docker image save peplinkwifitogglev2:arm64-local -o peplinkwifitogglev2-arm64-local.tar
```

For `arm/v7`:

```bash
docker image save peplinkwifitogglev2:armv7-local -o peplinkwifitogglev2-armv7-local.tar
```

Optional: compress to `.tgz`:

The `.tar` file is enough for transfer.
If needed, you can compress it any way you prefer.

## 7. Load Image On Another PC

Copy the archive to the other PC, then load it:

If file is `.tar`:

```bash
docker load -i peplinkwifitogglev2-amd64-local.tar
```

`docker load` only imports the image. It does not create a container.

First-time run on the new PC:

Bare minimum (only required values):

```bash
docker run -d \
	--name peplinkgps \
	-e USERNAME=admin \
	-e PASSWORD=Admin12345 \
	peplinkwifitogglev2:amd64-local
```

Full example (with all common settings):

```bash
docker run -d \
	--name peplinkgps \
	-e ROUTER_URL=https://192.168.50.1 \
	-e USERNAME=[INSERT USERNAME] \
	-e PASSWORD=[INSERT PASSWORD] \
	-e HTTP_TIMEOUT=8 \
	-e POLL_INTERVAL=10 \
	-e STOP_THRESHOLD=1.0 \
	-e MOVE_THRESHOLD=1.0 \
	-e STOP_SAMPLES=5 \
	-e MOVE_SAMPLES=3 \
	peplinkwifitogglev2:amd64-local
```

If you loaded a different architecture tag, replace image name accordingly:

- `peplinkwifitogglev2:arm64-local`
- `peplinkwifitogglev2:armv7-local`

## 8. Useful Docker Commands

View live logs (follow mode):

```bash
docker logs -f peplinkgps
```

List containers:

```bash
docker ps -a
```

Stop existing container:

```bash
docker stop peplinkgps
```

Start existing container (works only if `peplinkgps` was created before):

```bash
docker start peplinkgps
```

Remove container:

```bash
docker rm -f peplinkgps
```
