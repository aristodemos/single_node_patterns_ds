## A second sidecar example (HTTPS proxy)
Good choice — the **HTTPS sidecar proxy** is closer to real production usage than the logging example. It clearly shows:

👉 You don’t touch the legacy app
👉 Security gets “bolted on” externally
👉 Containers collaborate as one logical service

This tends to click fast with students.

---

# 🧪 Lab: HTTPS Termination Sidecar (Docker Compose)

## Learning goals

Students will:

* Add TLS to an existing HTTP-only service
* See sidecar networking in action
* Understand reverse proxy basics
* Learn why this pattern exists in real systems

Keep reminding them:

> The app stays simple. The sidecar handles HTTPS.

---

# 🧱 Architecture (simple mental model)

```
Browser
   ↓ HTTPS
[Nginx sidecar proxy]
   ↓ HTTP (internal)
[Legacy web app]
```

Key idea:

* Public traffic → sidecar
* Internal container traffic → plain HTTP

---

# 📁 Step 1 — Project structure

Have students create:

```
sidecar-https-lab/
 ├─ docker-compose.yml
 ├─ nginx/
 │   ├─ default.conf
 │   └─ certs/
 └─ app/
     ├─ Dockerfile
     └─ server.py
```

---

# 🧑‍💻 Step 2 — Legacy app container

Make it intentionally basic.

## app/Dockerfile

```dockerfile
FROM python:3.12-alpine
WORKDIR /app
COPY server.py .
CMD ["python", "server.py"]
```

## app/server.py

```python
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8080

print("Starting HTTP server on port", PORT)
HTTPServer(("", PORT), SimpleHTTPRequestHandler).serve_forever()
```

Explain:

* HTTP only
* No TLS support
* Typical “legacy service” scenario

---

# 🔐 Step 3 — Generate self-signed certificate

Have students run (inside `nginx/certs`):

```bash
openssl req -x509 -nodes -days 365 \
-newkey rsa:2048 \
-keyout key.pem \
-out cert.pem \
-subj "/CN=localhost"
```

Explain briefly:

* Self-signed → fine for lab
* Browsers will warn → expected

Don’t get stuck explaining PKI here.

---

# ⚙️ Step 4 — Nginx sidecar config

## nginx/default.conf

```nginx
server {
    listen 443 ssl;

    ssl_certificate /certs/cert.pem;
    ssl_certificate_key /certs/key.pem;

    location / {
        proxy_pass http://app:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Important teaching moment:

👉 `app` = service name from Compose
👉 Automatic DNS resolution inside network

That’s often an “aha” moment.

---

# 🐳 Step 5 — Docker Compose file

## docker-compose.yml

```yaml
version: "3.9"

services:
  app:
    build: ./app
    expose:
      - "8080"

  nginx-sidecar:
    image: nginx:alpine
    ports:
      - "8443:443"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./nginx/certs:/certs
    depends_on:
      - app
```

---

# ▶️ Step 6 — Run the system

Students run:

```bash
docker compose up --build
```

Then open:

```
https://localhost:8443
```

Expect:

⚠️ Browser security warning
→ Accept temporarily
→ HTTP server content appears.

That’s the success moment.

---

# 🧠 Key teaching checkpoints

## 1. Why this is a sidecar

Ask:

* Did we change the app code? → No
* Same deployment unit? → Yes
* Complementary function? → Yes

That’s the definition.

---

## 2. Why not bake TLS into the app?

Typical reasons:

* Legacy apps can’t be modified
* Security handled centrally
* Certificates easier to rotate
* Proxy can add logging/auth/rate limiting

This is how many production stacks work.

---

## 3. Networking insight

Students should grasp:

```
nginx → app:8080
```

works because:

* Compose network
* Built-in DNS
* Service names = hostnames

That knowledge transfers directly to Kubernetes.

---

# 👍 Optional quick experiments (worth doing)

## Change proxy target live

Edit:

```nginx
proxy_pass http://app:8080;
```

Restart nginx container:

```bash
docker compose restart nginx-sidecar
```

Shows container independence.

---

## Kill the app container

```bash
docker compose stop app
```

Observe:

* Proxy returns 502 error
* Sidecar still alive

Good resilience discussion.

---

# ⚠️ Common student friction points

### Cert path mistakes

Most common error:

```
cannot load certificate
```

Usually bad volume mount.

---

### Port conflicts

If 8443 busy:

```yaml
"9443:443"
```

No big deal.

---

### Browser HTTPS warnings confusion

Pre-empt this:

* Self-signed → expected
* Not a bug.

---

# 💬 Honest instructor advice

Don’t rush the discussion part.

Students often:

* Copy commands blindly
* Miss the architectural insight

Make them explain back:

> “Why didn’t we modify the app container?”

That’s the learning objective.

---