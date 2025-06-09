# LandVision Pro

This repository contains an initial scaffold for the YardVision Pro backend and documentation.

## Running the API

Install dependencies and start the development server with Uvicorn:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Alternatively, you may run the small helper module:

```bash
python -m backend.run --host 0.0.0.0 --port 8000
```

Both approaches serve the FastAPI app (use `--port` to change the port).

### Frontend

A minimal React application lives in the `frontend/` directory. Start it in development mode with:

```bash
cd frontend
npm start
```

The `package.json` is configured with `proxy: "http://localhost:8000"` so API calls will automatically be forwarded to the backend during local development.

### Available Endpoints

- `POST /v1/design-jobs` – submit a design request
- `GET /v1/design-jobs/{job_id}` – check job status
- `POST /v1/credits/purchase` – add credits to a tenant wallet
- `POST /v1/credits/deduct` – consume credits
- `GET /v1/rate-card?tenant_id=...` – fetch a tenant's rate card
