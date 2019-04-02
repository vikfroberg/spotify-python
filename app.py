import requests
import urllib.parse
import base64
import json
from flask import Flask, make_response, redirect, request, jsonify
from models import db, Search

# 422 return params and body so that one can render form

app = Flask(__name__)

CLIENT_ID = "ba714a6f875d4b329119327b37125d07"
CLIENT_SECRET = "0407c924f6684b10902887a85a4b54b8"

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

CLIENT_SIDE_URL = "http://localhost:5000"
REDIRECT_URI = "{}/callback".format(CLIENT_SIDE_URL)
SCOPE = "playlist-modify-public playlist-modify-private"

AUTH_QUERY_PARAMETERS = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

POSTGRES = {
    'user': 'vikfroberg',
    'pw': '7833',
    'db': 'spotify_dev',
    'host': 'localhost',
    'port': '5432',
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(app)


def _id(user):
    return user.id


def list_map(fn, list):
    return [fn(x) for x in list]


def to_query_string(options):
    return "&".join(["{}={}".format(key, urllib.parse.quote(val)) for key, val in options.items()])


@app.route("/")
def index():
    access_token = request.cookies.get('access_token')
    if access_token:
        authorization_header = {"Authorization":"Bearer {}".format(access_token)}
        endpoint = "{}/me".format(SPOTIFY_API_URL)
        response = requests.get(endpoint, headers=authorization_header)
        data = json.loads(response.text)

        if response.status_code == 200:
            return jsonify(data)
        else:
            return redirect("/login")

    else:
        return redirect("/login")


@app.route("/login")
def login():
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, to_query_string(AUTH_QUERY_PARAMETERS))
    return redirect(auth_url)


@app.route("/callback")
def callback():
    auth_token = request.args.get('code')

    code_payload = {
        "grant_type": "authorization_code",
        "code": auth_token,
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
    response_data = json.loads(post_request.text)

    if post_request.status_code == 200:
        access_token = response_data.get("access_token")
        refresh_token = response_data.get("refresh_token")
        expires_in = response_data.get("expires_in")

        response = make_response(redirect('/'))
        response.set_cookie('access_token', access_token)
        response.set_cookie('refresh_token', refresh_token)
        response.set_cookie('expires_in', str(expires_in))

        return response
    else:
        return jsonify(response_data)


# @app.route("/users/add")
# def users_add():
#     user = User()
#     db.session.add(user)
#     db.session.commit()
#     return jsonify(user.id)


@app.route("/labels/search")
def labels_search():
    q = request.args.get("q")
    access_token = request.cookies.get('access_token')
    if access_token:
        authorization_header = {"Authorization":"Bearer {}".format(access_token)}
        options = {
            "q": 'label:"{}" tag:new'.format(q),
            "type": "album",
            "limit": "50",
            "offset": "0",
        }
        endpoint = "{}/search?{}".format(SPOTIFY_API_URL, to_query_string(options))
        response = requests.get(endpoint, headers=authorization_header)
        data = json.loads(response.text)

        if response.status_code == 200:
            return jsonify(data)
        else:
            return redirect("/login")

    else:
        return redirect("/login")
    return jsonify(q)


@app.route("/artists/search")
def artists_search():
    q = request.args.get("q")
    access_token = request.cookies.get('access_token')
    if access_token:
        authorization_header = {"Authorization":"Bearer {}".format(access_token)}
        options = {
            "q": 'artist:"{}"'.format(q),
            "type": "track",
            "limit": "50",
            "offset": "0",
        }
        endpoint = "{}/search?{}".format(SPOTIFY_API_URL, to_query_string(options))
        response = requests.get(endpoint, headers=authorization_header)
        data = json.loads(response.text)

        if response.status_code == 200:
            return jsonify(data)
        else:
            return redirect("/login")

    else:
        return redirect("/login")
    return jsonify(q)


if __name__ == "__main__":
    app.run()
