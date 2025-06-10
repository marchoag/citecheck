# citecheck
A case law citation checker using the CourtListener API

## Setup

1. **Get a CourtListener API key:**
   - Sign up at https://www.courtlistener.com/
   - Go to your profile and generate an API token

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key:**
   Create a `.env` file in the project root:
   ```
   COURTLISTENER_API_KEY=your_actual_api_key_here
   ```

## Usage

The tool accepts various citation formats:

```bash
# Full citation with case name
python citecheck.py "Roe v. Wade, 410 US 113"

# Just the publication citation
python citecheck.py "410 US 113"

# Just the case name
python citecheck.py "Roe v. Wade"
```

## Features

- Flexible citation parsing (handles multiple formats)
- Search by case name, publication citation, or both
- Returns case details including court, date, and official citations
- Direct links to full text on CourtListener

## API Key Security

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Use placeholder values when sharing code
