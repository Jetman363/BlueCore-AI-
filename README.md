# Moved to BlueCore monorepo

This repository has been **merged into** the main BlueCore platform:

**https://github.com/Jetman363/BlueCore** → `services/ai-assistant/`

Use the monorepo for all development, Docker Compose, and pilot deployments. Start the add-on with:

```bash
./scripts/ensure-pilot-ai-service.sh
```

Or from the BlueCore repo root:

```bash
docker compose -f deployments/docker/docker-compose.yml up -d ai-assistant
```

This repository is kept for history and links only. Do not open new issues or PRs here — use **BlueCore** instead.
