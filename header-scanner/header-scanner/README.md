# HeaderCheck

A small tool that checks whether a site is sending the security headers it
should be (CSP, HSTS, X-Frame-Options, etc), grades it A-F, and tells you
what to fix. Built with a deliberately retro Web 1.0 look just for fun.

## Run it locally

```
git clone https://github.com/<your-username>/headercheck.git
cd headercheck
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 and type in a URL.

That's it — one file (`app.py`), one template, two real dependencies
(Flask + requests).

## Deploy it (so you can link a live demo, not just code)

Easiest option is **Render** (free tier, no credit card):

1. Push this repo to GitHub (see below if you haven't yet)
2. Go to https://render.com → New → Web Service → connect your GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Deploy — Render gives you a public URL in a couple minutes

Railway and PythonAnywhere work the same way if you'd rather use those.
The `Procfile` in this repo is already set up for any of them.

## How it works

`app.py` does three things: makes one request to the target URL, checks the
response headers against a list of headers that matter for security, and
checks cookies for missing `Secure`/`HttpOnly` flags. No crawling, no
external services, no API keys needed.

## Disclaimer

Only checks the same response headers your browser already receives when
visiting a page — it doesn't probe or attack anything. Still, use it on
sites you own or have permission to test.

## License

MIT
