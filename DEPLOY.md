# Deploying Finance Worklog to Railway

Railway is a modern deployment platform perfect for Python/Flask applications. Here's how to deploy:

## Prerequisites

- GitHub account with the repository pushed
- Railway account (free tier available)
- Access to your Railway dashboard

---

## Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Click "Start Project"
3. Sign up with GitHub
4. Authorize Railway to access your GitHub repos

---

## Step 2: Deploy from GitHub

### Option A: Deploy Directly (Recommended)

1. **Go to Railway Dashboard:** https://railway.app
2. **Click "+ New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Find your repository:** `muhammadzain-boop/finance-worklog`
5. **Click to deploy**

Railway will:
- Detect Python project
- Install requirements.txt
- Run Procfile command
- Start the web service

### Option B: Deploy with Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or with pip
pip install railway

# Login
railway login

# Deploy
cd C:\Users\Hp\Desktop\Nairobi
railway up

# View logs
railway logs
```

---

## Step 3: Configure Environment

Railway automatically sets `PORT` environment variable. Your app reads it:

```python
port = int(os.getenv('PORT', 5000))
```

### Add Custom Environment Variables (if needed)

1. Go to Railway Dashboard
2. Select your project
3. Click "Variables"
4. Add environment variables:
   - `FLASK_ENV=production`
   - `DEBUG=False`

---

## Step 4: View Your Deployment

Once deployed, Railway will provide:

- **Public URL:** `https://your-project-name.railway.app`
- **Logs:** Real-time application logs
- **Metrics:** CPU, Memory, Network usage

Visit your URL to see the Finance Worklog dashboard!

---

## Step 5: Connect Your GitHub Repo for Auto-Deploy

1. **In Railway Dashboard:**
   - Select your project
   - Go to "Settings"
   - Enable "Auto Deploy" for the `main` branch

2. **Now, every push to GitHub will:**
   - Trigger a new build
   - Deploy automatically
   - Show status in Railway logs

---

## File Structure for Railway

Railway needs these files in your repo:

```
finance-worklog/
├── serve.py              ← Your Flask app
├── Procfile              ← How to start the app
├── requirements.txt      ← Python dependencies
├── railway.json          ← Optional Railway config
├── .railwayignore        ← Files to ignore
└── README.md
```

✅ All these files are already in your repository!

---

## Troubleshooting

### App keeps crashing

Check logs in Railway dashboard:
```
railway logs -f  # Follow logs in real-time
```

Look for:
- Missing dependencies in requirements.txt
- Syntax errors in serve.py
- Port binding issues

### PORT is not set

Railway sets PORT automatically. Make sure your code reads it:
```python
port = int(os.getenv('PORT', 5000))
```

### Static files not loading

Railway serves everything through gunicorn. For static files, add them to `static/` folder:
```
static/
├── css/
├── js/
└── images/
```

Then reference in templates:
```html
<link rel="stylesheet" href="/static/css/style.css">
```

### Build timeout

If build takes too long:
- Check requirements.txt for unnecessary packages
- Remove large files from .gitignore compliance
- Split into multiple services

---

## Monitoring Your App

### View Logs

```bash
railway logs -f
```

### View Metrics

In Railway Dashboard:
- CPU usage
- Memory usage
- Restart count
- Error rates

### Set Up Alerts

Railway Pro features include:
- Email notifications on errors
- Uptime monitoring
- Performance alerts

---

## Adding the Parser Job

Once the web dashboard is live, add the background job:

```yaml
# railway.json (updated)
{
  "services": [
    {
      "name": "web",
      "build": "python",
      "startCommand": "gunicorn serve:app"
    },
    {
      "name": "job",
      "build": "python",
      "startCommand": "python schedule.py"
    }
  ]
}
```

This will run:
- `web`: Flask dashboard
- `job`: Parser running every 5 minutes

---

## Cost

Railway pricing:
- **Free tier:** $5/month usage allowance (ample for testing)
- **Pro:** $12/month base + usage
- **Usage:** ~$0.50/hour for small app

Your Finance Worklog dashboard:
- Very lightweight
- ~$1-2/month on free tier

---

## Next Steps

1. ✅ Push changes to GitHub
2. ✅ Go to Railway.app
3. ✅ Deploy from GitHub repo
4. ✅ Get public URL
5. ✅ Share with team!

---

## Useful Links

- Railway Docs: https://docs.railway.app
- Python Guide: https://docs.railway.app/guides/python
- GitHub Integration: https://docs.railway.app/guides/github
- Environment Variables: https://docs.railway.app/develop/variables

---

## Commands Reference

```bash
# Check Railway CLI version
railway --version

# Login to Railway
railway login

# Deploy current directory
railway up

# View project info
railway status

# View real-time logs
railway logs -f

# Run commands in production
railway shell

# Restart service
railway restart

# View environment variables
railway variables

# Add variable
railway variables:add KEY=VALUE
```

---

## Example Deployment Flow

```
1. Make changes to serve.py
   ↓
2. Commit: git commit -m "Update dashboard"
   ↓
3. Push: git push origin main
   ↓
4. GitHub webhook triggers Railway
   ↓
5. Railway pulls latest code
   ↓
6. Build: pip install -r requirements.txt
   ↓
7. Deploy: gunicorn serve:app
   ↓
8. Your app is live at: https://your-app.railway.app
```

---

**🚀 Your Finance Worklog is ready to deploy!**

Questions? Check Railway docs or GitHub issues.
