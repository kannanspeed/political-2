# Deployment Guide for Political Events App

## Deploy to Render

### Prerequisites
- GitHub account with your repository: `https://github.com/kannanspeed/political-2.git`
- Render account (free tier available)

### Step 1: Connect Repository to Render

1. **Go to Render Dashboard**
   - Visit [https://dashboard.render.com](https://dashboard.render.com)
   - Sign in or create an account

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"

3. **Connect GitHub Repository**
   - Click "Connect a repository"
   - Select `kannanspeed/political-2`
   - Click "Connect"

### Step 2: Configure Web Service

**Basic Settings:**
- **Name**: `political-events-app`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty (root of repository)

**Build & Deploy Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --worker-class eventlet -w 1 wsgi:app`

**Plan:**
- Select "Free" plan (or upgrade if needed)

### Step 3: Set Environment Variables

Click on "Environment" tab and add these variables:

**Required Variables:**
```
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///political_events.db
GOOGLE_MAPS_API_KEY=AIzaSyC4VX_V-P58o0lS1OTAkpfqqRPeNoc61z0
```

**Optional Variables:**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build the application
   - Deploy to a live URL

3. **Wait for Build to Complete**
   - Monitor the build logs for any errors
   - First build may take 5-10 minutes

### Step 5: Access Your App

Once deployment is successful:
- Your app will be available at: `https://your-app-name.onrender.com`
- The URL will be displayed in your service dashboard

## Post-Deployment Setup

### 1. Initialize Database
- Visit your app URL
- The database will be automatically created on first access
- Default admin account: `admin@political.com` / `admin123`

### 2. Test Functionality
- Test user registration
- Test event creation
- Test QR code generation
- Test real-time features

### 3. Monitor Performance
- Check Render dashboard for:
  - Build status
  - Service health
  - Logs
  - Performance metrics

## Troubleshooting

### Common Issues

**1. Build Failures**
- Check build logs in Render dashboard
- Verify all dependencies in `requirements.txt`
- Ensure Python version compatibility

**2. Runtime Errors**
- Check service logs in Render dashboard
- Verify environment variables are set correctly
- Test locally before deploying

**3. Database Issues**
- Ensure `DATABASE_URL` is set correctly
- Check if database file is writable
- Verify SQLite permissions

**4. Socket.IO Issues**
- Ensure `eventlet` is installed
- Check WebSocket configuration
- Verify CORS settings if needed

### Debug Commands

**Local Testing:**
```bash
# Test the app locally
python wsgi.py

# Check dependencies
pip list

# Test database
python init_db.py
```

**Render Logs:**
- Go to your service dashboard
- Click "Logs" tab
- Check for error messages

## Performance Optimization

### Free Tier Limitations
- **Sleep Mode**: Free services sleep after 15 minutes of inactivity
- **Cold Start**: First request after sleep may take 10-30 seconds
- **Bandwidth**: Limited bandwidth on free tier

### Upgrade Considerations
- **Paid Plans**: Better performance and no sleep mode
- **Custom Domains**: Add your own domain name
- **SSL Certificates**: Automatic HTTPS included
- **CDN**: Better global performance

## Security Considerations

### Environment Variables
- Never commit sensitive data to Git
- Use Render's environment variable system
- Rotate secrets regularly

### Database Security
- Use strong, unique `SECRET_KEY`
- Consider PostgreSQL for production
- Regular database backups

### API Keys
- Secure your Google Maps API key
- Set appropriate API restrictions
- Monitor API usage

## Monitoring & Maintenance

### Regular Checks
- Monitor service health
- Check build logs after updates
- Review error logs
- Monitor resource usage

### Updates
- Push changes to GitHub
- Render automatically redeploys
- Test changes locally first
- Monitor deployment logs

### Backup Strategy
- Regular database backups
- Version control for code
- Environment variable documentation
- Deployment configuration backup

## Support Resources

- **Render Documentation**: [https://render.com/docs](https://render.com/docs)
- **Flask Documentation**: [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
- **GitHub Issues**: Report bugs in your repository
- **Community Forums**: Stack Overflow, Reddit, etc.

---

**Happy Deploying! 🚀**

Your Political Events app should now be live on Render and accessible to users worldwide.
