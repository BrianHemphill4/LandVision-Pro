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

### Accessing the Demo UI

The repository includes a very small front end that interacts with the API. After starting the server, open `http://localhost:8000/ui/` in your browser to try it out.

### Available Endpoints

- `POST /v1/design-jobs` – submit a design request
- `GET /v1/design-jobs/{job_id}` – check job status
- `POST /v1/credits/purchase` – add credits to a tenant wallet
- `POST /v1/credits/deduct` – consume credits
- `GET /v1/rate-card?tenant_id=...` – fetch a tenant's rate card
