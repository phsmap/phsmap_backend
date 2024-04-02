from flask import Flask, request, Response, abort, send_file
import requests as http
import resource_server_configuration as cfg
import json
from datetime import datetime
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def fileRead(name, mode = 'r'):
    f = open(name, mode)
    c = f.read()
    f.close()
    return c

def closeOffLog(log):
    if cfg.doLog:
        f = open("access_log.txt", "a")
        f.write(str(log) + "\n")
        f.close()
    else:
        pass
        # during prod we're not actually going to log anything

@app.route('/resource', methods=["GET", "OPTIONS"])
@cross_origin()
def resource():
    if request.method == "OPTIONS": # CORS preflight
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET")
        return response

    toLog = f"{request.remote_addr}@{str(datetime.now())} "
    
    # First, we are going to check if the Auth. header is right
    token = request.headers.get('Authorization')
    if token == None or len(token.split(" ")) != 2 or token.split(" ")[0] != "Bearer":
        toLog = toLog + " -> 401:Bad Auth Header"
        closeOffLog(toLog)
        return Response("401 UNAUTHORIZED: Missing or malformed Authorization header (must be a Bearer token).", status=401, mimetype='text/plain')

    # Second, we are going to check if the user that called for the issuance of this token is a member of MCPSMD
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {
        'Authorization': 'Bearer ' + token.split(" ")[1],
        'Content-Type': 'application/json'
    }
    
    response = http.get(url, headers=headers)
    
    if response.status_code == 401:
        toLog = toLog + " -> 401:Bad Token"
        closeOffLog(toLog)
        return Response("401 UNAUTHORIZED: Access token does not correspond to any user, was tampered with, has expired or is otherwise invalid.", status=401, mimetype='text/plain')

    userPrincipalName = json.loads(response.text)["userPrincipalName"]

    if userPrincipalName.lower().endswith("mcpsmd.org") == False:
        toLog = toLog + f": {userPrincipalName.lower()} -> 401:Non MCPSMD"
        closeOffLog(toLog)
        return Response("401 UNAUTHORIZED: The user behind this token is not an MCPSMD user.", status=401, mimetype='text/plain')
    else:
        toLog = toLog + f": {userPrincipalName.lower()} "

    # Third, we are going to check if the file that the user has called for exists, and that they are allowed to access it
    # (we aren't going to let users call for any file on the fs willy nilly - they can only pull from a premade list)
    if request.args.get("file") == None or "/" in request.args.get("file"):
        toLog = toLog + "? {request.args.get('file')} -> 400:Bad ?file="
        closeOffLog(toLog)
        return Response("400 BAD REQUEST: Missing or malformed file parameter (the / character is not allowed).", status=400, mimetype='text/plain')
    else:
        toLog = toLog + f"? {request.args.get('file')}"

    try:
        file_number = cfg.acceptable_files.index(request.args.get("file"))
        if (file_number < 0):
            raise ValueError("The requested file isn't in the approved list.")
    except ValueError:
        toLog = toLog + " -> 403:No General Read Perm"
        closeOffLog(toLog)
        return Response(f"""403 FORBIDDEN: This user does not have permission to read this file ({request.args.get('file')})""", status=403, mimetype='text/plain')
        # There is supposed to be a check here where a specific user who has been given special permission to read a certain file
        # But we aren't there yet 

    # We only get to this spot if all conditions were met
    toLog = toLog + f": -> 200:OK"
    closeOffLog(toLog)
    return send_file(cfg.acceptable_files[file_number], cfg.mime_types[file_number])
    
    

    

if __name__ == '__main__':
    closeOffLog(f"""==== STARTUP AT {datetime.now()} ====
GP Accessible Files: {str(cfg.acceptable_files)}
Port #: {cfg.port}
==== END STARTUP LOG ====""")
    app.run(port=cfg.port)
