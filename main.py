from dotenv import load_dotenv
from flask import Flask, abort, request, redirect
from google.appengine.api import urlfetch
import json
import os
from os.path import join, dirname
import urllib
from uuid import uuid4
from gaesessions import get_current_session

app = Flask(__name__)

load_dotenv(join(dirname(__file__), '.env'))
CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("OAUTH_REDIRECT_URI", '')
AUTHORIZATION_BASE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_HOST = os.environ.get('GIT_HOSTNAME', 'https://github.com')
TOKEN_PATH = os.environ.get('OAUTH_TOKEN_PATH', '/login/oauth/access_token')
AUTHORIZE_PATH = os.environ.get(
    'OAUTH_AUTHORIZE_PATH', '/login/oauth/authorize')
TOKEN_URL = '%s%s' % (TOKEN_HOST, TOKEN_PATH)
SCOPE = os.environ.get('SCOPES', 'repo user')
SSL_ENABLED = os.environ.get('SSL_ENABLED', '0') == '1'


@app.route("/")
def index():
    """ Show a log in with github link """
    return 'Hello<br><a href="/auth">Log in with Github</a>'


@app.route("/auth")
def auth():
    """ We clicked login now redirect to github auth """
    return redirect(make_authorization_url())


@app.route("/callback", methods=["GET"])
def callback():
    """ retrieve access token """
    error = request.args.get('error', '')
    if error:
        print("Callback ERROR: %s" % error)
        abort(500)

    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)

    code = request.args.get('code')
    token = get_token(code, state)
    content = json.dumps(
        {'token': token, 'provider': 'github'})
    message = 'success'
    post_message = json.dumps(
        'authorization:github:{0}:{1}'.format(message, content))
    # print(post_message)
    return """<html><body><script>
    (function() {
      function recieveMessage(e) {
        console.log("recieveMessage %o", e)
        // send message to main window with da app
        window.opener.postMessage(
          """+post_message+""",
          e.origin
        )
      }
      window.addEventListener("message", recieveMessage, false)
      // Start handshare with parent
      console.log("Sending message: %o", "github")
      window.opener.postMessage("authorizing:github", "*")
      })()
    </script></body></html>"""


@app.route("/success", methods=["GET"])
def success():
    return '', 204


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "redirect_uri": REDIRECT_URI,
              "scope": SCOPE,
              "state": state, }
    url = "%s?%s" % (AUTHORIZATION_BASE_URL, urllib.urlencode(params))
    return url


# @TODO implement state storage and verification to protect against XSRF
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.


def save_created_state(state):
    pass


def is_valid_state(state):
    return True


def get_token(code, state):
    """Exchange the step 1 code for an access token"""
    headers = {
        # 'Accept': 'application/vnd.github.v3+json',
        'Accept': 'application/json',
        'Content-Type': 'application/json'}
    post_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        # "redirect_uri": REDIRECT_URI,
        # "state": state
    }
    print(json.dumps(post_data))
    result = urlfetch.fetch(TOKEN_URL,
                            payload=json.dumps(post_data),
                            method=urlfetch.POST,
                            headers=headers,
                            validate_certificate=True)

    if result.status_code != 200:
        print("API call error (%i): %s" % (result.status_code, result.content))
        abort(500)

    result_json = json.loads(result.content)

    return result_json["access_token"]


if __name__ == "__main__":
    run_config = {}
    if not SSL_ENABLED:
        # allows us to use a plain HTTP callback
        os.environ['DEBUG'] = "1"
        # If your server is not parametrized to allow HTTPS set this
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    else:
        run_config = {'ssl_context': 'adhoc'}
    app.secret_key = os.urandom(24)
    app.run(port=5000, debug=True, **run_config)
