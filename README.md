# Citation Checker
A beautiful web application for verifying case law citations using the CourtListener API.

## 🚀 Try It Live
[Deploy your own instance](#deployment) or run locally with the instructions below.

## ✨ Features
- **Easy-to-use web interface** - Just paste your citation and get results
- **Flexible citation formats** - Works with case names, citations, or both:
  - `"Roe v. Wade, 410 US 113"`
  - `"410 US 113"`
  - `"Roe v. Wade"`
- **Instant verification** - Get case details, court info, dates, and links
- **Beautiful modern UI** - Clean, professional design
- **No setup required** - Enter your API key right in the app

## 🔑 Getting an API Key
1. Sign up at [CourtListener.com](https://www.courtlistener.com/)
2. Go to your profile and generate an API token
3. Paste it into the web app - that's it!

## 🛠 Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open `http://localhost:5000` in your browser.

## 📦 Deployment
This app is ready to deploy on Railway, Heroku, Render, or any Python hosting service.

## 🔒 Security Note
Your API key is only used for your session and is never stored or logged.
