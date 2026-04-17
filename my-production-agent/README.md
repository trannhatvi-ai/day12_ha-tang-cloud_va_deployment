# Part 6 Final Project - My Production Agent

Production-ready AI agent theo checklist Part 6:

- REST API `/ask` with conversation history
- Redis-backed stateless design
- API key auth
- Rate limiting `10 req/min/user`
- Monthly cost guard `$10/user`
- `/health` and `/ready`
- Graceful shutdown (SIGTERM handler)
- Structured JSON logging
- Docker multi-stage build
- Docker Compose with `agent + redis + nginx`

## 1) Run local

```bash
cp .env.example .env
docker compose up --build --scale agent=3
```

## 2) Validate endpoints

```bash
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-this-in-production" \
  -d "{\"question\":\"Hello\",\"user_id\":\"user1\"}"
```

Expected checks:

- No API key -> `401`
- Send >10 requests in 1 minute -> `429`
- Exceed monthly budget -> `402`
- Repeated `/ask` with same `user_id` keeps conversation in Redis

## 3) Railway deploy (public URL)

```bash
npm i -g @railway/cli
railway login
railway init
railway variables set ENVIRONMENT=production
railway variables set REDIS_URL=<your_railway_redis_url>
railway variables set AGENT_API_KEY=<your_secret_api_key>
railway variables set RATE_LIMIT_PER_MINUTE=10
railway variables set MONTHLY_BUDGET_USD=10.0
railway variables set ESTIMATED_COST_PER_REQUEST_USD=0.02
railway up
railway domain
```

Smoke test after deploy:

```bash
curl https://<your-domain>/health
curl https://<your-domain>/ready
curl -X POST https://<your-domain>/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your_secret_api_key>" \
  -d "{\"question\":\"Deploy test\",\"user_id\":\"user-prod\"}"
```

## 4) Render deploy (public URL)

1. Push repo to GitHub.
2. In Render Dashboard, create Blueprint service from `render.yaml`.
3. Set secrets:
   - `REDIS_URL`
   - `AGENT_API_KEY`
4. Deploy and copy the generated service URL.
5. Run same smoke tests above with Render domain.
