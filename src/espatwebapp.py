import time
import os
import storage
import espatwifi
from espatwifi import send_cmd
from espatwebapp_html import payload_html, edit_html, new_html, response_html, newrow_html, cleanup_text
from duckyinpython import *

# === ROUTES ===
routes = {}

def route(method, path):
    def decorator(func):
        routes[(method, path)] = func
        return func
    return decorator


def match_route(method, request_path):
    """
    Match `request_path` against routes for `method`.
    Supports path variables in the form of <varname> in route paths.
    Returns (handler, [var_values]) or (None, None) if no match.
    """
    # Iterate over all registered routes for this method
    for (m, pattern), func in routes.items():
        if m != method:
            continue
        # Split pattern and request path into segments
        pat_segments = pattern.strip("/").split("/") if pattern != "/" else [""]
        req_segments = request_path.strip("/").split("/") if request_path != "/" else [""]
        if len(pat_segments) != len(req_segments):
            continue
        vars_values = []
        matched = True
        for pseg, rseg in zip(pat_segments, req_segments):
            if pseg.startswith("<") and pseg.endswith(">"):
                # Captured var; save value
                vars_values.append(rseg)
            elif pseg == rseg:
                continue
            else:
                matched = False
                break
        if matched:
            return func, vars_values
    return None, None


# === ENDPOINTS ===

def ducky_main():
    print("Ducky main")
    payloads = []
    rows = ""
    files = os.listdir()
    #print(files)
    for f in files:
        if ('.dd' in f) == True:
            payloads.append(f)
            newrow = newrow_html.format(f,f,f)
            #print(newrow)
            rows = rows + newrow

    response = payload_html.format(rows)
    return response

def setPayload(payload_number):
    if(payload_number == 1):
        payload = "payload.dd"
    else:
        payload = "payload"+str(payload_number)+".dd"

    return(payload)

@route("GET", "/ducky")
def duck_main():
    return ducky_main()

@route("GET", "/edit/<filename>")
def edit(filename):
    print("Editing ", filename)
    f = open(filename,"r",encoding='utf-8')
    textbuffer = ''
    for line in f:
        textbuffer = textbuffer + line
    f.close()
    response = edit_html.format(filename,textbuffer)

    return response

@route("POST", "/write/<filename>")
def write_script(request_body, filename):
    fields = request_body.split("&")
    form_data = {}
    for field in fields:
        key,value = field.split('=')
        form_data[key] = value

    #print(form_data)
    storage.remount("/",readonly=False)
    f = open(filename,"w",encoding='utf-8')
    textbuffer = form_data['scriptData']
    textbuffer = cleanup_text(textbuffer)
    #print(textbuffer)
    for line in textbuffer:
        f.write(line)
    f.close()
    storage.remount("/",readonly=True)
    response = response_html.format("Wrote script " + filename)
    return response

@route("GET", "/new")
def write_new_script_get():
    return new_html

@route("POST", "/new")
def write_new_script_post(request_body):
    fields = request_body.split("&")
    form_data = {}
    for field in fields:
        key,value = field.split('=')
        form_data[key] = value
    filename = form_data['scriptName']
    textbuffer = form_data['scriptData']
    textbuffer = cleanup_text(textbuffer)
    storage.remount("/",readonly=False)
    f = open(filename,"w",encoding='utf-8')
    for line in textbuffer:
        f.write(line)
    f.close()
    storage.remount("/",readonly=True)
    response = response_html.format("Wrote script " + filename)
    return response

@route("GET", "/run/<filename>")
def run_script(filename):
    print("run_script ", filename)
    response = response_html.format("Running script " + filename)
    runScript(filename)
    return response

@route("GET", "/")
def index():
    return ducky_main()

@route("GET", "/api/run/<filenumber>")
def api_run_script(filenumber):
    filename = setPayload(int(filenumber))
    print("run_script ", filenumber)
    response = response_html.format("Running script " + filename)
    runScript(filename)
    return response


# === SEND DATA (WAIT FOR >) ===
def send_data(link_id, data):
    cmd = f"AT+CIPSEND={link_id},{len(data)}"
    espatwifi.esp.at_response(cmd, timeout=5)
    
    start = time.monotonic()
    while time.monotonic() - start < 3:
        if espatwifi.esp._uart.in_waiting:
            resp = espatwifi.esp._uart.read()
            if b">" in resp:
                espatwifi.esp._uart.write(data)
                start2 = time.monotonic()
                while time.monotonic() - start2 < 3:
                    if espatwifi.esp._uart.in_waiting:
                        resp2 = espatwifi.esp._uart.read()
                        if b"SEND OK" in resp2:
                            return True
                return False
        time.sleep(0.01)
    return False

# === DRAIN UART ===
def drain_uart():
    while espatwifi.esp._uart.in_waiting:
        espatwifi.esp._uart.read()
        time.sleep(0.01)

# === HTTP RESPONSE ===
def make_response(body):
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{body}".encode()

# === MAIN LOOP ===
async def startWebService():
    try:
        # Ensure the esp module is initialized by startWiFi() before proceeding
        start = time.monotonic()
        while espatwifi.esp is None and time.monotonic() - start < 5:
            time.sleep(0.01)
        if espatwifi.esp is None:
            raise RuntimeError("espatwifi.esp not initialized; call startWiFi() first")
        while True:
            if espatwifi.esp._uart.in_waiting:
                data = espatwifi.esp._uart.read()
                if b"+IPD," in data:
                    try:
                        parts = data.split(b"+IPD,")[1]
                        link_id = int(parts.split(b",")[0])
                        length = int(parts.split(b",")[1].split(b":")[0])
                        raw_request = parts.split(b":", 1)[1][:length]

                        if b"\r\n\r\n" in raw_request:
                            headers, body = raw_request.split(b"\r\n\r\n", 1)
                            body = body.decode()
                        else:
                            headers = raw_request
                            body = ""

                        request_line = headers.split(b"\r\n")[0].decode()
                        method, path, _ = request_line.split()
                        # strip querystring if present
                        if "?" in path:
                            path = path.split("?", 1)[0]

                        print(f"{method} {path}")

                        handler, path_vars = match_route(method, path)
                        if handler:
                            if method == "POST":
                                # POST handlers expect request body as first arg, followed by path variables
                                response_body = handler(body, *path_vars)
                            else:
                                # GET handlers expect only path variables (if any)
                                response_body = handler(*path_vars)
                        else:
                            response_body = f"<h1>404: {path}</h1>"

                        response = make_response(response_body)
                        if send_data(link_id, response):
                            print("Sent")
                        else:
                            print("Send failed")

                        send_cmd(f"AT+CIPCLOSE={link_id}", timeout=3)
                        drain_uart()

                    except Exception as e:
                        print("Error:", e)
                        drain_uart()
                        raise e

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopped.")
        send_cmd("AT+CIPSERVER=0", timeout=3)

