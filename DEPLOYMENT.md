# Quick Deployment Guide

## 🚀 Deploy to jobs.slokam.org

### Step 1: Deploy Frontend (Vercel)

1. **Import to Vercel**:
   - Go to https://vercel.com/new
   - Import: `kbrahmateja/aijobapplyportal`
   - **Root Directory**: `apps/web` ← **IMPORTANT**
   - Click Deploy

2. **Add Custom Domain**:
   - Settings → Domains → Add `jobs.slokam.org`
   - Update DNS: CNAME `jobs` → `cname.vercel-dns.com`

3. **Environment Variables** (Settings → Environment Variables):
   ```
   NEXT_PUBLIC_API_URL=https://api-jobs.slokam.org
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxxxx
   CLERK_SECRET_KEY=sk_live_xxxxx
   ```

### Step 2: Setup Database (Supabase)

1. Create project at https://supabase.com
2. Database → Extensions → Enable `vector`
3. Copy connection string (Settings → Database)

### Step 3: Setup Redis (Upstash)

1. Create database at https://upstash.com
2. Copy Redis URL

### Step 4: Deploy Backend (Railway)

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select `kbrahmateja/aijobapplyportal`
4. **Root Directory**: `apps/api` ← **IMPORTANT**
5. Add PostgreSQL service
6. Add Redis service
7. Set environment variables (see .env.example)

### Step 5: Run Migrations

In Railway shell:
```bash
alembic upgrade head
```

### Step 6: Test

Visit https://jobs.slokam.org

---

For detailed instructions, see: deployment_plan.md
