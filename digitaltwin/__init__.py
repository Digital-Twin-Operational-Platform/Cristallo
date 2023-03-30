from flask import Flask
from flask_bootstrap import Bootstrap5
 
def create_app(test_config = None):
    app = Flask(__name__)
    bootstrap = Bootstrap5(app)

    from . import digitaltwin 
    app.register_blueprint(digitaltwin.bp)

    return app
def get_date():
    import urllib.request, json 
    from dateutil import parser
    try:
        with urllib.request.urlopen("https://api.github.com/repos/Digital-Twin-Operational-Platform/Cristallo/commits") as url:
            data = json.load(url)
    except:
        return("Unable to Gather Date")
    date = data[0]["commit"]["author"]["date"]
    
    datestr = parser.isoparse(date).ctime()
    return datestr
date = get_date()