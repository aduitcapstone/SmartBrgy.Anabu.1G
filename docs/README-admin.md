# SmartBrgy — Admin Dashboard
**Barangay Anabu I-G, Imus City, Cavite**

Sistema ng pamamahala ng barangay — para sa barangay staff.

## Mga Files

| File | Paggamit |
|---|---|
| `index.html` | Admin dashboard |
| `static/script.js` | Lahat ng logic ng admin |
| `static/style.css` | Estilo |
| `static/db-connector.js` | Koneksyon sa backend API |
| `app.py` | Flask backend API |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render.com deployment config |
| `database/` | SQL dumps (dev/seed data) |

## Pag-setup (Local)

```bash
pip install flask werkzeug
python app.py
```

Buksan ang `index.html` sa browser.

## Deployment

- **Backend (app.py):** Naka-deploy sa [Render.com](https://render.com) — awtomatiko mula sa GitHub push
- **Frontend (index.html):** Naka-host sa GitHub Pages

## API URL

Ang `script.js` ay awtomatikong gagamit ng:
- `http://localhost:5000` — kapag lokal na nag-te-test
- `https://smartbrgy-api.onrender.com` — kapag live na

## Environment Variables

Kailangan i-set ang mga ito sa hosting provider (huwag i-hardcode sa `app.py`):

| Variable | Paggamit |
|---|---|
| `GMAIL_USER` | Gmail address na magpapadala ng notification emails |
| `GMAIL_APP_PASSWORD` | Gmail App Password (Google Account → Security → App Passwords) |

Para sa lokal na testing, i-export muna bago patakbuhin ang `python app.py`:

```bash
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
```

## Tandaan

- Ang `smartbrgy.db` ay nasa `.gitignore` — **huwag i-commit** (personal na datos ng mga residente)
- Ang Render.com free tier ay natutulog pagkatapos ng 15 minuto ng walang gumagamit
