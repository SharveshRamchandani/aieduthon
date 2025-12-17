# AI Service Docker Guide

## Prereqs
- Docker installed.
- MongoDB reachable; set URI/DB name via env or build args.
- API keys as needed (HuggingFace, Stability, Gemini, Unsplash).

## Build
From repo root:
```
docker build -t ai-service ./ai \
  --build-arg AI_MONGODB_URI_ARG="mongodb://localhost:27017" \
  --build-arg AI_DB_NAME_ARG="ai_db" \
  --build-arg HF_API_KEY_ARG="" \
  --build-arg LLM_PROVIDER_ARG="huggingface" \
  --build-arg STABILITY_API_KEY_ARG="" \
  --build-arg GEMINI_API_KEY_ARG="" \
  --build-arg UNSPLASH_API_KEY_ARG=""
```
You can omit args to use Dockerfile defaults, or override at runtime instead.

## Run
Typical local run (override envs at runtime):
```
docker run --rm -p 8000:8000 \
  -e AI_MONGODB_URI="mongodb://host.docker.internal:27017" \
  -e AI_DB_NAME="ai_db" \
  -e HF_API_KEY="your_hf_key" \
  -e LLM_PROVIDER="huggingface" \
  -e STABILITY_API_KEY="" \
  -e GEMINI_API_KEY="" \
  -e UNSPLASH_API_KEY="" \
  -v "$(pwd)/ai/out:/app/src/out" \
  ai-service
```
Notes:
- `host.docker.internal` works for Mongo on the host (mac/win). On Linux, use your host IP or a Docker network with `--network`.
- Volume mount `ai/out` is optional but keeps generated media/PPTs on the host.

## API
Service listens on `http://localhost:8000`.
- `GET /slides/ping` (if present) or use orchestrate/generate routes defined in `api/routes`.
- Media served at `/media` maps to `/app/src/out/generated_images`.

## .env Option
Instead of `-e` flags, you can mount a `.env` to `/app/src/.env`:
```
docker run --rm -p 8000:8000 \
  --env-file ./ai/.env \
  -v "$(pwd)/ai/out:/app/src/out" \
  ai-service
```

## Common Issues
- Mongo connection fails: check `AI_MONGODB_URI`, network reachability, auth.
- Missing keys for providers: ensure relevant env vars are set.
- LibreOffice/PDF: PDF export uses LibreOffice; install in base image if needed or stick to PPTX.

