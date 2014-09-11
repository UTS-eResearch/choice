'''
Hello Application to Test WSGI 
Following: http://note.kjuly.com/note/nginx-uwsgi-bottle/

Files needed: hello.py          <-- this file
              hello-uwsgi.ini   <-- configuration

Run like this: 
    uwsgi --http :9090 --plugin python --wsgi-file path/to/project/hello.py
    View with: lynx localhost:9090
or
    uwsgi --ini hello-uwsgi.ini

'''

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    
    html = "<h1>Hello World From Python</h1>\n"
    html += "<table>\n"
    for k in env:
        html += "<tr><td>{}</td><td>{}</td></tr>\n".format(k, env[k])
    html += "</table>\n"

    return html

