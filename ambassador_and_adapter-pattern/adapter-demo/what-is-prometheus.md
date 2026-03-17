# Prometheus — Introduction & Hands-On (Instructor Script)

## 1. Why Do We Need Prometheus?

Today I want to answer a simple question:

> How do we understand what our system is doing *right now*?

Logs are useful, but they are:

* unstructured
* hard to aggregate
* hard to query in real time

Metrics give us:

* numbers over time
* fast aggregation
* simple queries

Prometheus is a system designed specifically for **metrics**.

---

## 2. What Is Prometheus?

Prometheus is a **time-series database + monitoring system**.

It does three main things:

1. Scrapes metrics from services
2. Stores them as time-series data
3. Lets us query and visualize them

Mental model:

```
Service → /metrics → Prometheus → Query → Graph
```

---

## 3. Pull vs Push Model

Important concept.

Prometheus uses **pull (scraping)**:

```
Prometheus → HTTP GET /metrics → Service
```

Why this is powerful:

* Prometheus controls collection
* Easier service discovery
* More reliable than push systems

---

## 4. What Is a Time Series?

A time series is:

```
(metric name, labels) → value over time
```

Example:

```
http_requests_total{method="GET"}
```

Prometheus stores values like:

```
time → value
```

---

## 5. Metric Types

I explain these clearly before coding.

* **Counter** → only increases
* **Gauge** → goes up and down
* **Histogram** → distribution (latency buckets)
* **Summary** → percentiles

In our lab we mostly use:

* counters
* gauges

---

## 6. The Exposition Format (Core Idea)

Prometheus expects a **plain text format**.

Why?

* language-agnostic
* trivial to implement
* easy to debug with curl

Structure:

```
metric_name{label="value"} number
```

---

## 7. Example Metrics Output

```
# HELP legacy_requests_total Total requests handled
# TYPE legacy_requests_total counter
legacy_requests_total 57

# HELP legacy_errors_total Total errors
# TYPE legacy_errors_total counter
legacy_errors_total 14
```

Explain:

* `# HELP` → documentation
* `# TYPE` → metric type
* last line → actual data

---

## 8. Labels — The Real Power

Labels turn one metric into many dimensions.

```
http_requests_total{method="GET",status="200"}
http_requests_total{method="POST",status="500"}
```

Prometheus treats these as separate time series.

This enables aggregation like:

```
sum by(method)(http_requests_total)
```

---

## 9. How Prometheus Works Internally

I describe the flow step by step:

1. Prometheus scrapes `/metrics`
2. Parses text format
3. Stores time-series in TSDB
4. Allows querying with PromQL
5. Visualizes in UI or Grafana

---

## 10. Running Prometheus

I show them a minimal setup.

`docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

`prometheus.yml`:

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "app"
    static_configs:
      - targets: ["app:8000"]
```

---

## 11. Running the System

I run:

```bash
docker compose up
```

Then open:

```
http://localhost:9090
```

---

## 12. First Query (Make It Click)

I type:

```promql
legacy_requests_total
```

Students see a line going up.

Then I explain:

> This is a counter — it only increases.

---

## 13. Rates (Most Important Concept)

Counters alone are boring.

We use:

```promql
rate(legacy_requests_total[30s])
```

This gives:

> requests per second

This is where Prometheus becomes useful.

---

## 14. Error Ratio (Real Monitoring)

```promql
100 * rate(legacy_errors_total[30s])
  / rate(legacy_requests_total[30s])
```

This shows system reliability.

I emphasize:

> This is what production dashboards look like.

---

## 15. Gauges (Instant Values)

```promql
legacy_queue_depth
```

Explain:

* reflects current system state
* not cumulative

---

## 16. Generating Data (Live Demo)

I run a load generator:

```bash
python loadgen.py
```

Students see graphs move in real time.

---

## 17. How Reports/Dashboards Are Built

Prometheus itself provides:

* basic graphs

For real dashboards we use Grafana.

Flow:

```
Prometheus → PromQL → Grafana Panels
```

In Grafana we:

* create panels
* define queries
* build dashboards

---

## 18. Example Dashboard Metrics

I typically include:

* request rate
  n- error rate
* latency
* queue depth

These give a complete system picture.

---

## 19. Why This Design Works

I summarize key ideas:

* text format → simple and universal
* pull model → reliable
* labels → powerful aggregation
* PromQL → expressive queries

---

## 20. Key Takeaway

I close with this message:

> If you can expose metrics, you can understand your system.

Prometheus gives you a **mathematical view of your system over time**.
