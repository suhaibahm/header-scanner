from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# these are the headers we care about. each one has a short note on why
# it matters and what to do if it's missing. severity is just a rough
# guess at how bad it is to not have it, not some official scoring system
HEADERS_TO_CHECK = {
    "Content-Security-Policy": {
        "why": "Stops a bunch of XSS and data injection attacks by controlling what scripts/styles/etc are allowed to load.",
        "fix": "Add a CSP header, even a basic one is better than nothing.",
        "severity": "high",
    },
    "Strict-Transport-Security": {
        "why": "Forces browsers to only talk to the site over HTTPS, even if someone tries to downgrade the connection.",
        "fix": "Add 'Strict-Transport-Security: max-age=63072000; includeSubDomains'",
        "severity": "medium",
    },
    "X-Frame-Options": {
        "why": "Without this your site can be put inside an iframe on someone else's page (clickjacking).",
        "fix": "Add 'X-Frame-Options: DENY' or use frame-ancestors in your CSP.",
        "severity": "medium",
    },
    "X-Content-Type-Options": {
        "why": "Stops browsers guessing the content type which can be abused in some attacks.",
        "fix": "Add 'X-Content-Type-Options: nosniff'",
        "severity": "low",
    },
    "Referrer-Policy": {
        "why": "Controls how much of your URL gets leaked to other sites when people click links away from your page.",
        "fix": "Add something like 'Referrer-Policy: strict-origin-when-cross-origin'",
        "severity": "low",
    },
    "Permissions-Policy": {
        "why": "Lets you turn off browser features (camera, mic, geolocation etc) that the page doesn't need.",
        "fix": "Add a Permissions-Policy header restricting features you're not using.",
        "severity": "info",
    },
}

# headers that are fine to have but shouldn't really be telling the world
# what software/version you're running
LEAKY_HEADERS = ["Server", "X-Powered-By", "X-AspNet-Version", "X-Generator"]


def scan_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "HeaderScanner/1.0"})
    except requests.exceptions.SSLError:
        return {"error": "SSL error - couldn't verify the certificate. Site might have a bad/expired cert."}
    except requests.exceptions.ConnectionError:
        return {"error": "Couldn't connect. Check the URL is right and the site is up."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out after 8 seconds."}
    except Exception as e:
        return {"error": f"Something went wrong: {e}"}

    found = []
    missing = []

    for header_name, info in HEADERS_TO_CHECK.items():
        if header_name in r.headers:
            found.append({
                "name": header_name,
                "value": r.headers[header_name],
            })
        else:
            missing.append({
                "name": header_name,
                "why": info["why"],
                "fix": info["fix"],
                "severity": info["severity"],
            })

    leaks = []
    for h in LEAKY_HEADERS:
        if h in r.headers:
            leaks.append({"name": h, "value": r.headers[h]})

    # quick cookie check while we're at it, not just headers but related enough
    cookie_issues = []
    for c in r.cookies:
        problems = []
        if not c.secure:
            problems.append("no Secure flag")
        if not c.has_nonstandard_attr("HttpOnly"):
            problems.append("no HttpOnly flag")
        if problems:
            cookie_issues.append({"name": c.name, "problems": problems})

    score = len(found) - len(missing) * 0  # not really using this for now, placeholder
    grade = calc_grade(found, missing)

    return {
        "url": url,
        "status_code": r.status_code,
        "found": found,
        "missing": missing,
        "leaky_headers": leaks,
        "cookie_issues": cookie_issues,
        "grade": grade,
    }


def calc_grade(found, missing):
    # super rough grading, weight by severity of what's missing
    weights = {"high": 3, "medium": 2, "low": 1, "info": 0.5}
    penalty = 0
    for m in missing:
        penalty += weights.get(m["severity"], 1)

    if penalty == 0:
        return "A"
    elif penalty <= 2:
        return "B"
    elif penalty <= 4:
        return "C"
    elif penalty <= 6:
        return "D"
    else:
        return "F"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    url = data.get("url", "").strip() if data else ""

    if not url:
        return jsonify({"error": "need a url"}), 400

    result = scan_url(url)
    return jsonify(result)


if __name__ == "__main__":
    # debug=True is fine for local testing, just don't deploy this to
    # the public internet with debug on
    app.run(debug=True, port=5000)
