import uvicorn

if __name__ == '__main__':
    # Avoid reload=True to prevent multiprocessing issues in containers
    import argparse

    parser = argparse.ArgumentParser(description="Run YardVision Pro API")
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    uvicorn.run('backend.main:app', host=args.host, port=args.port)
