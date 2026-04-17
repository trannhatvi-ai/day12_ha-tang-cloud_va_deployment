#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Trần Nhật Vĩ  
> **Student ID:** 2A202600497  
> **Date:** 4/17/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1.hard-coded credentials and secrets
2.hard-coded configuration values
3.lack of proper error handling
4.no logging or monitoring
5.lack of authentication and authorization
6.not using a proper environment variable management system
7.no rate limiting or request validation
8.no monitoring or alerting
9.not following security best practices
10.not using version control.

### Exercise 1.2: Test results

#### Develop
PS D:\AI_thucchien\Day12\day12_ha-tang-cloud_va_deployment> curl.exe -X POST http://localhost:8000/ask?question=Hi
{"answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận."}

#### Production
PS D:\AI_thucchien\Day12\day12_ha-tang-cloud_va_deployment> curl.exe -X POST http://localhost:8000/ask?question=Hi
Internal Server Error

-> Nó chạy, nhưng nó báo lỗi Internal Server Error do chưa có API key và chưa có rate limiting và cost guard và không có authentication và authorization. Chỉ có thể chạy được ở localhost


###  Exercise 1.3: So sánh với advanced version

```bash
cd ../production
cp .env.example .env
pip install -r requirements.txt
python app.py
```

**Nhiệm vụ:** So sánh 2 files `app.py`. Điền vào bảng:

| Feature | Basic (develop) | Advanced (production) | Tại sao quan trọng? |
|---------|-----------------|----------------------|---------------------|
| Config | Hardcode `OPENAI_API_KEY`, `DATABASE_URL` trực tiếp trong code | Đọc từ env vars qua `config.py` + `.env` file, có `validate()` fail-fast | Push lên GitHub → key bị lộ, bot quét GitHub tìm key trong vài giây. Env vars cho phép thay đổi config giữa dev/staging/prod mà không sửa code |
| Health check | Không có (`/health` → 404) | Có `/health` (liveness), `/ready` (readiness), `/metrics` | Platform (Railway/K8s) gọi health check định kỳ, nếu fail → tự restart container. Không có thì app crash âm thầm, không ai biết |
| Logging | `print()` kèm log cả secret (`print(OPENAI_API_KEY)`) | Structured JSON logging qua `logging` module, KHÔNG log secrets | JSON logs dễ parse bởi log aggregator (Datadog, Loki). `print()` mất khi container restart, không có timestamp/level, không filter được |
| Shutdown | Đột ngột — `Ctrl+C` kill ngay, request đang xử lý bị mất | Graceful — `SIGTERM` handler + `lifespan` context manager, chờ request hoàn thành rồi mới tắt | Trên cloud, platform gửi SIGTERM trước khi kill. Graceful shutdown đảm bảo không mất data/request đang xử lý |
| Host binding | `localhost` — chỉ truy cập từ máy local | `0.0.0.0` — nhận kết nối từ bên ngoài container | Trong Docker/cloud, traffic đến từ bên ngoài. Bind `localhost` = container chạy nhưng không ai gọi được |
| Port | Hardcode `8000` | Đọc từ `PORT` env var | Railway/Render inject PORT tự động, hardcode sẽ conflict |

###  Checkpoint 1

- [x] Hiểu tại sao hardcode secrets là nguy hiểm → Bot quét GitHub tìm API key trong vài giây, key bị lộ = mất tiền + bị revoke
- [x] Biết cách dùng environment variables → Dùng `os.getenv()` + `.env` file (trong `.gitignore`), centralize qua `config.py` dataclass
- [x] Hiểu vai trò của health check endpoint → Platform dùng `/health` để biết app còn sống, `/ready` để biết sẵn sàng nhận traffic, fail → auto restart
- [x] Biết graceful shutdown là gì → Bắt signal SIGTERM, chờ request đang xử lý xong, đóng connections, rồi mới tắt — không mất data

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: [python:3.11-slim]
2. Working directory: [/app]
3. [EXPOSE 8000]
4. [COPY . .]
5. [RUN pip install...]
...

### Exercise 2.3: Image size comparison
- Develop: [1700] MB
- Production: [236.44] MB
- Difference: [720]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://03-cloud-deployment-production.up.railway.app
- Screenshot: https://github.com/trannhatvi-ai/day12_ha-tang-cloud_va_deployment/blob/main/Railway_deployment.png

## Part 4: API Security

### Exercise 4.1-4.3: Test results

#### 4.1
- API key được check ở đâu?
- Điều gì xảy ra nếu sai key?
- Làm sao rotate key?
1. Hàm verify_api_key (dòng 39-54), được inject qua Depends tại endpoint /ask.
2. Trả về 401 Unauthorized nếu thiếu key hoặc 403 Forbidden nếu key không khớp.
3. Cập nhật biến môi trường AGENT_API_KEY và khởi động lại service.

PS D:\AI_thucchien\Day12\day12_ha-tang-cloud_va_deployment> curl.exe -X POST http://localhost:8000/ask?question=Hi
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}

#### 4.2
PS D:\AI_thucchien\Day12\day12_ha-tang-cloud_va_deployment> $resp = Invoke-RestMethod -Uri http://localhost:8000/auth/token -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username": "student", "password": "demo123"}'
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MjkxMzcsImV4cCI6MTc3NjQzMjczN30.68r_fAb5CFrsDa4e6CVMW9JMF8yAZ1_J1W750CgjJAA

$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MjkxMzcsImV4cCI6MTc3NjQzMjczN30.68r_fAb5CFrsDa4e6CVMW9JMF8yAZ1_J1W750CgjJAA"

Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -Headers @{"Authorization" = "Bearer $TOKEN"; "Content-Type" = "application/json"} `
  -Body '{"question": "Explain JWT"}'

{"answer":"Agent đang hoạt động tốt! Hỏi thêm câu hỏi đi nhé. @{rate_limit=Limit(10, 60) calls/s, token=175/2500}"}


#### 4.3

- Algorithm nào được dùng? (Token bucket? Sliding window?)
- Limit là bao nhiêu requests/minute?
- Làm sao bypass limit cho admin?

1. Algorithm: Sliding Window Counter — dùng deque lưu timestamps từng request, pop các entry cũ hơn 60s trước mỗi lần check.

2. Limit:

student (role=user): 10 req/minute
teacher (role=admin): 100 req/minute

3. Bypass cho admin: limiter = rate_limiter_admin if role == "admin" else rate_limiter_user

Kết quả sau khi chạy test_ratelimit.ps1:
- Req 1–10: 200 OK, remaining đếm từ 9 → 0
- Req 11–15: HTTP 429 — rate limit hit đúng sau 10 requests/minute

### Exercise 4.4: Cost guard implementation

**Approach:** Tích hợp Redis backend trực tiếp vào `CostGuard.check_budget()` trong `cost_guard.py`.

**Thiết kế:**
- Khi khởi động, thử kết nối Redis (`_r.ping()`). Nếu thành công → `_REDIS_AVAILABLE = True`, nếu không → fallback in-memory.
- **Redis path**: Mỗi user có key `budget:<user_id>:<YYYY-MM>` (ví dụ `budget:student:2026-04`). Dùng `INCRBYFLOAT` để cộng dồn chi phí atomic. TTL 32 ngày → key tự expire sang tháng mới, không cần cron job reset.
- **In-memory fallback**: Giữ nguyên logic cũ dùng `UsageRecord` + daily budget — app vẫn chạy được dù không có Redis.

**Lý do chọn Redis:**
- Persist qua restart (in-memory mất data khi server crash)
- Share state giữa nhiều pod khi scale horizontal
- `INCRBYFLOAT` là atomic → không race condition khi nhiều request cùng lúc

**Trade-off so với solution trong bài:**
- Solution gốc dùng standalone function riêng, approach này tích hợp thẳng vào class để `app.py` không cần thay đổi interface (vẫn gọi `cost_guard.check_budget(user_id)`).
- Thêm `estimated_cost` parameter (default `0.0`) để pre-check trước khi gọi LLM, tránh gọi xong mới biết vượt budget.

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks

Implement 2 endpoints trong `05-scaling-reliability/develop/app.py`:

```python
@app.get("/health")
def health():
    """Liveness probe — container còn sống không?"""
    uptime = round(time.time() - START_TIME, 1)
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/ready")
def ready():
    """Readiness probe — sẵn sàng nhận traffic không?"""
    if not _is_ready:
        raise HTTPException(status_code=503, detail="Agent not ready.")
    return {"ready": True, "in_flight_requests": _in_flight_requests}
```

**Phân biệt liveness vs readiness:**
- `/health` (liveness): process còn chạy không → nếu fail → platform **restart** container.
- `/ready` (readiness): dependencies (Redis, DB) đã connect, model đã load → nếu fail → load balancer **ngừng route** traffic vào instance này nhưng không restart.

### Exercise 5.2: Graceful shutdown

`develop/app.py` dùng FastAPI `lifespan` context manager để handle graceful shutdown:

```python
def shutdown_handler(signum, frame):
    """Handle SIGTERM từ container orchestrator"""
    # 1. Đánh dấu không nhận request mới
    _is_ready = False
    # 2. Chờ request đang xử lý hoàn thành (tối đa 30 giây)
    timeout, elapsed = 30, 0
    while _in_flight_requests > 0 and elapsed < timeout:
        time.sleep(1); elapsed += 1
    # 3. Close connections → uvicorn xử lý
    # 4. Exit → uvicorn tự exit sau lifespan shutdown
    logger.info("Shutdown complete")

signal.signal(signal.SIGTERM, shutdown_handler)
```

Kết quả test: khi gửi SIGTERM, request đang chạy vẫn hoàn thành bình thường, không bị cắt giữa chừng. `timeout_graceful_shutdown=30` trong uvicorn config đảm bảo điều này.

### Exercise 5.3: Stateless design

**Anti-pattern (stateful):**
```python
conversation_history = {}  # chỉ tồn tại trong 1 instance

@app.post("/ask")
def ask(user_id: str, question: str):
    history = conversation_history.get(user_id, [])  # instance 2 không có!
```

**Correct (stateless với Redis):**
```python
@app.post("/chat")
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())
    append_to_history(session_id, "user", body.question)  # → ghi vào Redis
    session = load_session(session_id)                     # → đọc từ Redis
    answer = ask(body.question)
    append_to_history(session_id, "assistant", answer)
    return {"session_id": session_id, "answer": answer, "served_by": INSTANCE_ID}
```

Mỗi request mang `session_id` → bất kỳ instance nào cũng đọc được từ Redis → scale ngang tự do.

### Exercise 5.4: Load balancing

```bash
docker compose up --scale agent=3
```

Nginx (`nginx.conf`) dùng `upstream` với round-robin mặc định phân đều traffic:
- 3 agent instances chạy song song, mỗi instance có `INSTANCE_ID` riêng.
- Response field `"served_by"` cho thấy request được phân tán qua các instance khác nhau.
- Nếu 1 instance die, Nginx tự loại ra và chỉ route sang 2 instance còn lại.

### Exercise 5.5: Test stateless

```bash
python test_stateless.py
```

Script thực hiện:
1. Gọi `/chat` lần 1 → nhận `session_id`
2. Gọi `/chat` lần 2 với cùng `session_id` → kiểm tra history vẫn còn
3. (Nếu có Docker) Kill random instance → gọi lần 3 → session vẫn tồn tại trong Redis

Kết quả kỳ vọng: conversation history persist dù instance thay đổi → xác nhận thiết kế stateless thành công.


---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
