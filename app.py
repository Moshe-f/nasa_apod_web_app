import os

from flask import Flask, redirect, url_for, render_template, request, abort
import requests


NASA_API_KEY: str | None = os.getenv("NASA_API_KEY")  # NASA API key


app = Flask(__name__)


def parse_resp(resp):
    """Parse Nasa api respond.

    Args:
        resp (json): Nasa respond.

    Returns:
        dict: [str: str]
    """
    placeholder: str = r"\static\bryan-goff-f7YQo-eYHdM-unsplash.jpg"
    title: list = resp.get("title", "")
    src: str = resp.get("url", placeholder)
    explanation: str = resp.get("explanation", ".").replace(".", ".{&").split("{&")
    copyright: str = resp.get("copyright", "NASA")
    date: str = ("-").join(resp.get("date", "-").split("-")[::-1])
    media_type: str = resp.get("media_type", "")

    # Dealing with source missing.
    if src == placeholder:
        copyright = "Bryan Goff - Unsplash - (place holder - source missing)"
        date = "place holder - source missing"
        media_type: str  = "image"

    return {"title": title, "src": src, "explanation": explanation, "copyright": copyright, "date": date, "media_type": media_type}


def get_apod(get_url):
    """Return json respond from nasa api.

    Args:
        get_url (str): Url for api request.

    Returns:
        json: Nasa respond.
    """
    if NASA_API_KEY == None:
        print("api key not found")
        abort(500)

    resp = requests.get(get_url)
    
    if not resp.ok:
        print("api don't respond")

    return resp.json()


@app.route("/")
def home():
    """Render apod home page, with img and title from nasa api.

    Returns:
        func: render_template(apod.html)
    """
    resp = get_apod(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}")

    parse_respond = parse_resp(resp)

    return render_template("apod.html", **parse_respond)


@app.route("/apod/<string:date>")
def apod_by_date(date):
    """Render apod page, with img and title from nasa api with date param.

    Returns:
        func: render_template(apod.html)
    """
    date: str = ("-").join(date.split("-")[::-1])
    resp = get_apod(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date}")

    parse_respond = parse_resp(resp)

    return render_template("apod.html", **parse_respond)


@app.route("/search-apod", methods=["GET", "POST"])
def search_apod_by_date():
    """Render search apod page, with images and titles from nasa api.

    Returns:
        func: render_template(search-apod.html)
    """
    if request.method == "POST":
        date = ("-").join(request.form["date"].split("-")[::-1])
        return redirect(url_for("apod_by_date", date=date))

    resp = get_apod(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&count=6")

    parse_responds = []

    for img in resp:
        parse_responds.append(parse_resp(img))

    return render_template("search-apod.html", respond=parse_responds)


# Error handlers
@app.errorhandler(404)
def page_not_found(error: int):
    """Error handler 404 Respond.

    Args:
        error (int): Response number.

    Returns:
        str: Render template of 404 error page.
    """
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(threaded=True, port=5000, debug=True)
