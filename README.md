These steps use Windows cmd, but the commands are nearly identical on Mac/Linux (just swap venv\Scripts\activate for source venv/bin/activate).
1. Clone or download the repo, then go into the folder

git clone https://github.com/<your-username>/headercheck.git

cd headercheck

If you downloaded it as a zip instead, extract it first, then cd into the extracted folder — make sure you're in the folder that actually contains app.py (running dir should show it in the list).

2. (Optional but recommended) Create a virtual environment

python -m venv venv

venv\Scripts\activate

You'll know it worked if your prompt now starts with (venv).

3. Install dependencies
python -m pip install -r requirements.txt

4. Run the app

python app.py

You should see something like:

* Running on http://127.0.0.1:5000

5. Open it in your browser

Go to http://localhost:5000. Type in a URL (e.g. example.com or https://example.com) and click Check. Leave the cmd window open while you're using it — closing it stops the server. Press Ctrl+C in the cmd window to stop it manually.

That's the whole thing — one file (app.py), one template, two real dependencies (Flask + requests).
