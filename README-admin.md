# SmartBrgy — Admin Dashboard
**Barangay Anabu I-G, Imus City, Cavite**

Sistema ng pamamahala ng barangay — para sa barangay staff.

## Mga Files

| File | Paggamit |
|---|---|
| `index.html` | Admin dashboard |
| `script.js` | Lahat ng logic ng admin |
| `style.css` | Estilo |
| `app.py` | Flask backend API |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render.com deployment config |

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

## Tandaan

- Ang `smartbrgy.db` ay nasa `.gitignore` — **huwag i-commit** (personal na datos ng mga residente)
- Ang Render.com free tier ay natutulog pagkatapos ng 15 minuto ng walang gumagamit
