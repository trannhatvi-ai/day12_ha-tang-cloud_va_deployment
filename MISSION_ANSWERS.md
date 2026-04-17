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
[Paste your test outputs]
#### 4.1

PS D:\AI_thucchien\Day12\day12_ha-tang-cloud_va_deployment> curl.exe -X POST http://localhost:8000/ask?question=Hi
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}

#### 4.2
PS D:\AI_thucchien\Day12\day12_ha-tang-cloud_va_deployment> curl.exe -X POST http://localhost:8000/ask?question=Hi                                                                                          
Internal Server Error

#### 4.3

PS D:\AI_thucchien\Day12\day12_ha-tang-cloud_va_deployment> Invoke-RestMethod -Uri http://localhost:8000/auth/token -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username": "student", "password": "demo123"}'     

access_token
------------
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MjIwM... 


### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]
```

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
