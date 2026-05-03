# Render Deployment Guide

## Overview

This project is configured for deployment on [Render](https://render.com) using the `render.yaml` blueprint configuration.

## Services

The blueprint deploys the following services:

### 1. Frontend (Next.js)
- **Name:** nexus-frontend
- **Runtime:** Node.js
- **Port:** 3000
- **Build:** `cd frontend && npm install && npm run build`
- **Start:** `cd frontend && npm run start`

### 2. Backend (FastAPI)
- **Name:** nexus-backend
- **Runtime:** Python 3.12
- **Port:** 8000
- **Build:** `cd backend && pip install -r requirements.txt`
- **Start:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 3. Database
- **Type:** PostgreSQL 16
- **Name:** nexus_db
- **Initial DB:** nexus_wellness
- **Default User:** nexus_user

### 4. Cache
- **Type:** Redis
- **Name:** nexus-cache

## Deployment Steps

1. **Connect Repository to Render**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Select your GitHub repository (sivlejsk-dev/Nexus-welless)
   - Render will auto-detect the `render.yaml`

2. **Environment Variables**
   - Database URL is auto-configured
   - Redis URL is auto-configured
   - Frontend API URL points to backend automatically

3. **Deploy**
   - Click "Create Blueprint"
   - Render will provision all services
   - Deployment takes 5-10 minutes

## Service URLs

After deployment, you'll receive URLs for:
- Frontend: `https://nexus-frontend-xxxx.onrender.com`
- Backend API: `https://nexus-backend-xxxx.onrender.com`

## Post-Deployment

1. **Database Initialization**
   ```bash
   # Connect to PostgreSQL and run migrations
   # Configure initial data as needed
   ```

2. **Environment Variables** (if needed)
   - Add custom API keys
   - Configure third-party integrations
   - Set feature flags

3. **Monitoring**
   - Check logs in Render dashboard
   - Monitor resource usage
   - Set up alerts

## Troubleshooting

### Build Failures
- Check `render.yaml` syntax
- Verify all dependencies are listed in `requirements.txt`
- Ensure `package.json` scripts are correct

### Runtime Errors
- View logs: Dashboard → Service → Logs
- Check environment variables are set
- Verify database connectivity

### Performance
- Monitor database connections
- Check Redis connectivity
- Scale services if needed (paid feature)

## Local Testing

Before deploying, test locally:

```bash
# Using Docker Compose
docker compose up -d

# Frontend
cd frontend && npm run dev

# Backend
cd backend && uvicorn app.main:app --reload
```

## Support

- [Render Documentation](https://render.com/docs)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
