# Single-Node Patterns Lab Pack

This pack contains two Docker-based live-coding demos:

1. `ambassador-demo/` – request splitting via a Python ambassador proxy
2. `adapter-demo/` – metrics normalization via a Python adapter exporter

Run everything:

```bash
docker compose up --build
```

Optional Prometheus profile:

```bash
docker compose --profile observability up --build
```

Main endpoints:

- App: http://localhost:8000
- Ambassador stats: http://localhost:8001/stats
- Legacy app: http://localhost:8100/work
- Metrics adapter: http://localhost:9101/metrics
- Prometheus (optional): http://localhost:9090
