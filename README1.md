## 🌩 One-Click Deployment

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/YOUR_USERNAME/muller-suspender-x1)

### Post-Deployment Steps:
1. Go to **Resources** tab in Heroku
2. Enable the `worker` dyno
3. Set environment variables:
   - `WHATSAPP_TOKEN` - From Facebook Developer Portal
   - `LICENSE_KEY` - Your master license key
4. Check logs: `heroku logs --tail --app your-app-name`
