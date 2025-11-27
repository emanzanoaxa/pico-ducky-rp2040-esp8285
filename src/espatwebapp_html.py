payload_html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W Ducky</title> </head>
    <body> <h1>Pico W Ducky</h1>
        <table border="1"> <tr><th>Payload</th><th>Actions</th></tr> {} </table>
        <br>
        <a href="/new">New Script</a>
    </body>
</html>
"""

edit_html = """<!DOCTYPE html>
<html>
  <head>
    <title>Script Editor</title>
  </head>
  <body>
    <form action="/write/{}" method="POST">
      <textarea rows="5" cols="60" name="scriptData">{}</textarea>
      <br/>
      <input type="submit" value="submit"/>
    </form>
    <br>
    <a href="/ducky">Home</a>
  </body>
</html>
"""

new_html = """<!DOCTYPE html>
<html>
  <head>
    <title>New Script</title>
  </head>
  <body>
    <form action="/new" method="POST">
      Script Name<br>
      <textarea rows="1" cols="60" name="scriptName"></textarea>
      Script<br>
      <textarea rows="5" cols="60" name="scriptData"></textarea>
      <br/>
      <input type="submit" value="submit"/>
    </form>
    <br>
    <a href="/ducky">Home</a>
  </body>
</html>
"""

response_html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W Ducky</title> </head>
    <body> <h1>Pico W Ducky</h1>
        {}
        <br>
        <a href="/ducky">Home</a>
    </body>
</html>
"""

newrow_html = "<tr><td>{}</td><td><a href='/edit/{}'>Edit</a> / <a href='/run/{}'>Run</a></tr>"

_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None

def cleanup_text(string):
    """unquote('abc%20def') -> b'abc def'."""
    global _hextobyte

    if not string:
        return b''

    if isinstance(string, str):
        string = string.encode('utf-8')

    bits = string.split(b'%')
    if len(bits) == 1:
        return string

    res = [bits[0]]
    append = res.append

    if _hextobyte is None:
        _hextobyte = {(a + b).encode(): bytes([int(a + b, 16)])
                      for a in _hexdig for b in _hexdig}

    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)

    return b''.join(res).decode().replace('+',' ')