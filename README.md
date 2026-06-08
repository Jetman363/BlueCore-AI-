# BlueCore AI

Optional add-on for the [BlueCore Public Safety Platform](https://github.com/Jetman363/BlueCore): an AI Law Enforcement Assistant and Threat Assessment module that agencies can enable without modifying core BlueCore deployment.

**Repository:** `git@github.com:Jetman363/BlueCore-AI-.git`

## Modules

| Module | Description |
|--------|-------------|
| **Law Enforcement Assistant** | CAD/RMS support, narrative drafting, BOLOs, briefings, policy-compliant guidance |
| **Threat Assessment** | Explainable officer-safety intelligence with agency-configurable policy profiles |

Both modules ship with versioned system prompts in `prompts/` and require human review before official record submission.

## Quick Start

```bash
git clone git@github.com:Jetman363/BlueCore-AI-.git
cd BlueCore-AI-
cp .env.example .env
pip install -r requirements.txt
cd service && PYTHONPATH=app uvicorn app.main:app --reload --port 8095
```

Or with Docker:

```bash
docker compose up --build
curl http://localhost:8095/healthz
```

## BlueCore Integration

This service is **not bundled** with BlueCore. Enable it per agency:

1. Deploy this service alongside BlueCore (same JWT secrets).
2. Set `BLUECORE_AI_ASSISTANT_ENABLED=true` in BlueCore gateway config.
3. Enable the `ai_assistant` module in System Architect Portal.

See [docs/bluecore-integration.md](docs/bluecore-integration.md) for full integration steps.

## Security

- JWT authentication compatible with BlueCore gateway tokens
- CJIS-oriented data handling; treat all inputs as CJI
- Threat assessments exclude protected characteristics
- All assistant and threat operations are audit-logged
- Stub LLM provider for development; configure Ollama or Azure OpenAI for production

## API

See [docs/api-reference.md](docs/api-reference.md).

## License

Proprietary — BlueCore Public Safety Platform add-on.
