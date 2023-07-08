from flask import *
from methods import *
import os
from dotenv import load_dotenv

app = Flask(__name__)
generator=Generator()


@app.route("/")
def RootRequest():
    return generator.getPage("index.json", {})
@app.route("/test")
def Test():
    config=generator.read_file("json/murakatasssystem/config.json","json","//")
    if config.split()[0] == "FileNotFoundError:":
        return ("Config File not found")
    #return config
#I used two functions because flask needs a trailing slash
"""
@app.route("/<path:uri_request>")
def GeneralRequest(uri_request):
    #split the request
    uri_request=uri_request.split("/")
    #look on pages definition file for a match
    config=generator.read_file("json/system/config.json","json","//")
    if config == "FileNotFoundError":
        return ("Config File not found")
    uri_definition=generator.read_file(config["URIS_FILE"],"json","//")
    #no matches? return 404
    if uri_request[0] not in uri_definition:
        abort(404)
    else:
        return generator.getPage(uri_definition[uri_request[0]]['instructor'],uri_definition[uri_request[0]]['arguments'])
"""
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

