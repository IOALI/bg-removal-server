# Background Removal Server — Railway Deployment

## Deploy in 5 minutes (FREE)

### Step 1 — Create a GitHub account
Go to https://github.com and sign up (free)

### Step 2 — Create a new GitHub repository
1. Click the "+" icon → "New repository"
2. Name it: `bg-removal-server`
3. Set it to **Public**
4. Click "Create repository"

### Step 3 — Upload these files to GitHub
1. Click "uploading an existing file" link on the repo page
2. Drag and drop ALL files from this folder:
   - server.py
   - requirements.txt
   - Procfile
   - railway.toml
   - runtime.txt
3. Click "Commit changes"

### Step 4 — Deploy on Railway
1. Go to https://railway.app
2. Click "Start a New Project"
3. Click "Deploy from GitHub repo"
4. Sign in with your GitHub account
5. Select your `bg-removal-server` repository
6. Railway will automatically build and deploy!

### Step 5 — Get your server URL
1. In Railway dashboard, click your project
2. Click "Settings" → "Domains"
3. Click "Generate Domain"
4. Copy the URL — it looks like: `https://bg-removal-server-production-xxxx.up.railway.app`

### Step 6 — Configure WordPress plugin
1. Go to WordPress Admin → BG Remover → Settings
2. Paste your Railway URL in the "Python Server URL" field
3. Click "Test Connection" — should show ✓ green
4. Save settings
5. Done! Go process your products 🎉

## Notes
- Railway free tier gives 500 hours/month (more than enough)
- First request after idle may take 30-60 seconds (cold start)
- The AI model downloads automatically on first deploy (~170MB)
