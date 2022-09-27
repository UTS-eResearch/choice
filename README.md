# Discrete Choice Experiments

Author: Mike Lake     
Version of this Doc: 2015.03.23

<a href="#description"/>Description</a>    
<a href="#release"/>New Version Release at Nectar</a>    
<a href="#required"/>Software Required</a>    
<a href="#setup"/>System Setup at Nectar</a>    
<a href="#programs"/>Two Programs - choice.py and process_choices.py</a>    
<a href="#running"/>Running the Application</a>    
<a href="#tests"/>Running Regression Tests</a>    
<a href="#windows"/>Running under Microsoft Windows</a>    
<a href="#problems"/>Problems Encountered</a>     
<a href="#refs"/>Programming References</a>    

## Description

This describes the python scripts that run the web based 
&quot;Discrete Choice Experiments&quot;. 
This was written for for Deborah Street and Leonie Burgess. 
Mike Lake wrote the choice.py and Emily Bird (from Maths) wrote the main functions in 
process_choices.py.  

## New Version Release at Nectar

This is how to do a new release at the Nectar hosted site.

1. Update the version number for the main program: `choice.py`               
   e.g. version = '2013.10.23'

   The version numbers for the other programs remain as-is; 
   i.e. `choice_common.py` and `process_choices.py`

2. Checkin changes and push to github.

2. Run the script `./release_to_nectar.sh`      
   This will just make a tarball of the required files and scp the tarball to Nectar's 
   `/home/ec2-user/public_html/`. 
   It will then echo to the screen the command for logging into Nectar.

3. Login to Nectar (this is done automatically by the above script)     
   `$ ssh -i ~/.ssh/keys/mikes_nectar ec2-user@130.56.248.113`
  
   Your home directory will be `/home/ec2-user/`     
   The tarball will be in public_html/

       $ cd public_html 
       $ tar xvf choice_release_2014.01.07.tar  <== This will create directory choice_2014.01.07/
       $ rm choice_release_2014.01.07.tar
    
       $ sudo systemctl stop nginx.service

       $ rm choice                               <== This is a symlink to a release.
       $ ln -s choice_release_2014.01.07 choice  <== Create new symlink.

       $ sudo systemctl start nginx.service
       $ sudo systemctl restart uwsgi.service
 
4. Check <a href="http://XXX.XXX.XXX.XXX">http://XXX.XXX.XXX.XXX/choice</a> 
It should show the correct version number at the bottom left of the page. 

If you just want an archive of the current repo then:

    $ git archive HEAD --prefix=choice/ --output ../choice.tar

## Software Required for Choice Application

The following required software will be installed onto a "Fedora release 19" release.

### Fedora Packages

First &quot;<tt>sudo yum update</tt>&quot; then install the following Fedora packages:

    Fedora Package          Provides
    --------------          --------
    python                  Python 2.7.5 will already be installed.
    python-bottle           Provides micro web framework
    python-devel            Required for a pip install of subprocess32-3.2.6
    numpy                   Provides numerical array maths
    gcc                     Required for a pip install of subprocess32-3.2.6
    nginx                   Provides web server
    uwsgi                   Provides /usr/sbin/uwsgi and other files in /etc/ and /usr/share/doc/uwsgi
    uwsgi-plugin-python     Only provides /usr/lib64/uwsgi/python_plugin.so
    uwsgi-plugin-common     Pulled in as a dependeny of uwsgi-plugin-python 

Note: on my laptop I have installed:

    mod_wsgi &lt;-- this is for Apache
        /etc/httpd/conf.modules.d/10-wsgi.conf
        /usr/lib64/httpd/modules/mod_wsgi.so
        /usr/share/doc/mod_wsgi
        /usr/share/doc/mod_wsgi/LICENCE
        /usr/share/doc/mod_wsgi/README

### Python Packages

<b>sympy</b>: The python package called sympy is available from from http://sympy.org. 
This provides symbolic maths for python. From that site download and install sympy-0.7.2.tar.gz <br>
Note: Do not install sympy from the yum repos. That will install version 0.7.3
which has a problem. Download 0.7.2 and install using setup.py as below.

    sympy-sympy-0.7.2$ python setup.py build
    sympy-sympy-0.7.2$ sudo python setup.py install

<b>subprocess32-3.2.6</b>: &quot;subprocess&quot; is the native one for Python 2.7 but I have 
installed &quot;subprocess32&quot; (via &quot;pip install&quot;) which is a
backport from Python 3.0 which supports a timeout arg. 

Added via pip install: subprocess32-3.2.6

    $ python setup.py build
    $ sudo python setup.py install
    OK  

Note: if you have not installed python-devel via yum then when you do the
"python setup.py build" step you will get an error "Python.h: No such file or directory".
This package also needs gcc so ensure gcc yum package is installed.

## System Setup at Nectar

### Nginx Setup at Nectar

Mike made some global changes to nginx configuration files. 
The changes are documented in these files. Search for MRL strings for changes. 

    /etc/nginx/nginx.conf                   Changed document root, changed log format to a simpler string.
    /etc/nginx/conf.d/default.conf          Contains hello and choice apps. 
    /usr/share/nginx/html/index.html        Changed to just say "Nothing here." 
    /home/ec2-user/public_html              Created public_html directory. 

Changed permissions of /home/ec2-user/ so nginx can see the public_html dir. 

    from: drwx------ 
    to:   drwxr-xr-x                      

Check nginx configuration:

    $ sudo /usr/sbin/nginx -t
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    $ 

Change ownership and mode of choice python files:

    choice$ chown ec2-user:nginx *.py
    choice$ chmod ug+x *.py

Make sure that nginx starts at boot time:

    $ sudo systemctl enable nginx.service
    ln -s '/usr/lib/systemd/system/nginx.service' '/etc/systemd/system/multi-user.target.wants/nginx.service'
    $ 

    TODO deployment: nginx+uwsgi
    
    TODO nohup python app.py &amp; - run in background with ability to logout from console.
    
    In /etc/nginx/nginx.conf
    # TODO logs outside of http or server do ???
    #access_log  /var/log/nginx/access.log  main;
    #error_log  /var/log/nginx/error.log;
    #error_log  /var/log/nginx/error.log  notice;
    #error_log  /var/log/nginx/error.log  info;

### uWSGI Setup at Nectar

<p>Package uwsgi will contain /usr/sbin/uwsgi and some doc files. <br>
<tt>$ rpmquery -ql uwsgi | grep -v doc</tt>
</p>

<pre>
/etc/uwsgi.d     &lt;-- was empty, added choice.ini &amp; hello.ini
/etc/uwsgi.ini
/run/uwsgi
/usr/lib/systemd/system/uwsgi.service
/usr/sbin/uwsgi
</pre>

File: /etc/uwsgi.ini 
<blockquote>
<pre>
[uwsgi]
uid = uwsgi  &lt;-- drops privs from root to these after starting. TODO uwsgi or nginx
gid = uwsgi
pidfile = /run/uwsgi/uwsgi.pid
emperor = /etc/uwsgi.d
stats = /run/uwsgi/stats.sock
emperor-tyrant = false
cap = setgid,setuid
</pre>
</blockquote>


File: /etc/uwsgi.d/choice.ini
<blockquote>
<pre>
[uwsgi]
uid = nginx
gid = nginx
socket = 127.0.0.1:9000
plugin = python
wsgi-file = /home/ec2-user/public_html/choice/choice.py 
chdir = /home/ec2-user/public_html/choice/
process = 3
</pre>
</blockquote>
 
File: /etc/uwsgi.d/hello.ini 
<blockquote>
<pre>
[uwsgi]
uid = nginx
gid = nginx
socket = 127.0.0.1:9090
plugin = python
wsgi-file = /home/ec2-user/public_html/hello/hello.py
process = 1
</pre>
</blockquote>

This is what we should see:

uwsgi is running:

<pre>
$ ps ax | grep uwsgi
  325 ?        Ss     1:11 /usr/sbin/uwsgi --ini /etc/uwsgi.ini
  341 ?        S      0:43 /usr/sbin/uwsgi --ini choice.ini
  343 ?        S      0:43 /usr/sbin/uwsgi --ini hello.ini
  381 ?        S      0:00 /usr/sbin/uwsgi --ini hello.ini
  407 ?        S      0:01 /usr/sbin/uwsgi --ini choice.ini
$ 

~/$ ps axjf | grep wsgi
    1   325   325   325 ?           -1 Ss     996   1:11 /usr/sbin/uwsgi --ini /etc/uwsgi.ini
  325   341   325   325 ?           -1 S      996   0:43  \_ /usr/sbin/uwsgi --ini choice.ini
  341   407   325   325 ?           -1 S      996   0:01  |   \_ /usr/sbin/uwsgi --ini choice.ini
  325   343   325   325 ?           -1 S      996   0:43  \_ /usr/sbin/uwsgi --ini hello.ini
  343   381   325   325 ?           -1 S      996   0:00      \_ /usr/sbin/uwsgi --ini hello.ini
~/$ 
</pre>

<pre>
$ sudo netstat -tlpn | grep uwsgi
tcp   0    0 127.0.0.1:9090   0.0.0.0:*   LISTEN   343/uwsgi           
tcp   0    0 127.0.0.1:9000   0.0.0.0:*   LISTEN   341/uwsgi           
<strike>tcp   0    0 127.0.0.1:9000   0.0.0.0:*   LISTEN   8509/uwsgi</strike>
<strike>tcp   0    0 127.0.0.1:9001   0.0.0.0:*   LISTEN   8507/uwsgi</strike> 
$ 

</pre>

Here is how to start the uwsgi service:
<pre>
$ sudo systemctl start uwsgi.service
</pre>

<pre>
$ ps axjf | grep wsgi
   0:00 /usr/sbin/uwsgi --ini /etc/uwsgi.ini
   0:00  \_ /usr/sbin/uwsgi --ini /etc/uwsgi.ini
</pre>


Make sure uWSGI starts at boot time:
<pre>
$ sudo systemctl enable uwsgi.service
ln -s '/usr/lib/systemd/system/uwsgi.service' '/etc/systemd/system/multi-user.target.wants/uwsgi.service'
$ 
</pre>

<p>
<b>Note</b>: /etc/uwsgi/ directory containing emperor.ini and vassals/ is not part of the uwsgi package.
</p>


<h3>systemd Setup at Nectar</h3>

<p>At Nectar we are running a systemd based init system which replaces the
older SysV init system. See <tt>/etc/init.d/README</tt>. 
Files are in: <tt>/etc/systemd/system</tt> and some of these are symlinks to files in 
<tt>/usr/lib/systemd/system</tt> 
</p>

<p>Basic usage: </p>

<pre>
systemctl start nginx.service
systemctl stop nginx.service
systemctl status nginx.service    
systemctl list-unit-files
</pre>

<p>If you use the older SysV system command: <tt>$ service uwsgi status</tt> it will 
redirect it with a message 
&quot;<tt>Redirecting to /bin/systemctl status uwsgi.service</tt>&quot;
</p>


<p>The Choice application page should now be visible at: 
<a href="http://130.56.248.113/choice/">http://130.56.248.113/choice/</a>
</p>

<a name="programs"/><h2>Two Programs - choice.py and process_choices.py</h2>

<p>This is the web form submission process.</p>

<pre>
Start here

+--- Users Web Browser ---+
|                         |
|  Javascript validation  | <-- Note 1 
|  for basic checking     |
+-------------------------+
              |
User submits form  
              |
+--- choice.py: web application ---+
|                                  | 
| gets inputs from web browser     |      +--- process_choices.py ----+ 
| inputs_validation()              |      |                           |
|                                  |      | get_expected_io()         |
| write_input_files() ------------------> | read_input_files()        |  
|                                  |      |   ... processing ...      |
|                                  |      |   ... processing ...      |
| read_output_files() <------------------ | write_output_files()      |
|                                  |      +---------------------------+
| creates HTML pages with data     | 
+----------------------------------+
              |
Results sent back to user
              |
+--- Users Web Browser ---+
|                         |
|         results         |
+-------------------------+
</pre>

<p>This is roughly what each program does.</p>

<table>
<tr><td><p><b>choice.py:</b><br>
1. reads form input values (as dict)<br>  
2. writes input values to files in a temp dir<br>
3. runs process_choices.py<br>
4. reads output values from these files<br>
5. writes values to web page
</p></td>
<td><p>
<b>process_choices.py:</b><br>
1. reads input values from files in temp dir<br>
2. processes them<br>
3. writes output values to files in temp dir<br>
&nbsp;<br>
&nbsp;<br>
</p></td>
</tr>
</table>


<p>
Note 1: To turn off the javascript validation edit <tt>views/head.tpl</tt> and rename the 
<tt>src="/static/validate.js"</tt> to something &quot;wrong&quot; so it won't load.
</p>

<a name="running"/><h2>Running the Application</h2>

<h3>Running under Bottle's inbuilt web server</h3>

<p><i>This is just for testing - not production!</i></p>

<p>The script choice.py needs to have this at the end:</p>
<pre>
  run(host='localhost', port=8080, reloader=True)
</pre>

<p>Start the script:</p>
<pre>
  choice/$ ./choice.py 
  Bottle server starting up (using WSGIRefServer())...
  Listening on http://localhost:8080/
  Hit Ctrl-C to quit.
</pre>

Go to: <a href="http://localhost/choice">http://localhost/choice</a>

<p>Note: The port=8080 is superfluous as the default port is actually 8080. 
If you try to run  on port 80 you will get a 
"socket.error: [Errno 13] Permission denied error" as you don't have permission 
to bind that that port - even if apache or nginx are not running. 
</p>

<h3>Running under Nginx and Fast CGI</h3>

<p><i>This is how to run for production.</i></p>

<p>The script choice.py needs to have this:</p>
<pre>
  run(server=FlupFCGIServer, port=9000, host='localhost', reloader=True)
</pre>

<p>Start the script:</p>
<pre>
  choice/$ ./choice.py 
  Bottle server starting up (using FlupFCGIServer())...
  Listening on http://127.0.0.1:9000/
  Hit Ctrl-C to quit.
</pre>

or

<pre>
$ nohup python ./choice.py &   &lt;-- Runs COMMAND, ignoring hangup signals.
  nohup: ignoring input and appending output to "nohup.out"
</pre>

<p>Go to: <a href="http://localhost/choice/">http://localhost/choice/</a>
</p>

<pre>
[ec2-user@choice2 ~]$ ps ax | grep choice
     2:11 avahi-daemon: running [choice2.local]
     1:31 python ./choice.py
     3:14 /usr/bin/python ./choice.py
[ec2-user@choice2 ~]$ 
</pre>

<p>If you get this web page below then you forgot to start ./choice.py</p>
<pre>
  Possibly Busy
  The page you are looking for is temporarily unavailable. Please try again later. 
</pre>

Note: For Mikes laptop only make sure nginx is running and not apache: 
<pre>
  $ sudo service httpd stop
  Redirecting to /bin/systemctl stop  httpd.service
  choice/$ sudo service nginx start
  Redirecting to /bin/systemctl start  nginx.service
  $ 
</pre>

<a name="tests"/><h2>Running Regression Tests</h2>

<p>Run the script to show usage. For each test there should be no output if the test passes. </p>

<pre>
$ ./regression_test.sh
$
</pre>

<a name="windows"/><h2>Running 'process_choices.py' under Microsoft Windows </h2>

<p>The web server and its app (i.e. <tt>choice.py</tt>) can't be run under Windows but the 
program <tt>process_choices.py</tt> can be run under Windows. This means that Emily Bird 
can run and debug her code on Windows. For details on this see below.</p>

<p>1. Copy the following files over to the Windows box: 
<tt>process_choices.py</tt> and <tt>choice_common.py</tt><br>
2. Copy the directory <tt>test</tt>  with its test files to the Windows box.<br>
</p>

<p>Then run it like this: </p>

<pre>
C:\choice_emily&gt; C:\Python27\python.exe process_choices.py test\check_main_1 check main
C:\choice_emily&gt; 
</pre>

<p>Note: Regression tests also can't be run under Windows.</p>

<a name="problems"/><h2>Problems Encountered</h2> 

<h3>Problem: Connection refused while connecting to upstream.</h3>

<p>Error is:</p>

<pre>
2014/04/29 13:10:04 [error] 10640#0: *9 connect() failed (111: Connection refused) while connecting to upstream, 
client: 113.197.9.114, server: , request: "GET /hello/ HTTP/1.1", upstream: "uwsgi://127.0.0.1:9090", host: "130.56.248.113"
</pre>

<p>This error Means nginx is trying to pass along the app to port 9090 but nothing seems to be listening there. 
But we do seem to have uwsgi listening OK - see below: <br>
<tt>10848 ?        Ss     0:00 /usr/sbin/uwsgi --ini /etc/uwsgi.ini </tt><br>
<tt>10850 ?        S      0:00 /usr/sbin/uwsgi --ini /etc/uwsgi.ini </tt>
</p>

<h3>Problem: Starting uwsgi </h3>

<pre>
$ sudo /usr/sbin/uwsgi --ini /etc/uwsgi.ini 
[uWSGI] getting INI configuration from /etc/uwsgi.ini
setting capability setgid [6]
setting capability setuid [7]
*** Starting uWSGI 1.9.19 (64bit) on [Thu May  1 14:19:04 2014] ***
compiled with version: 4.8.2 20131017 (Red Hat 4.8.2-1) on 12 November 2013 18:02:19
os: Linux-3.13.9-100.fc19.x86_64 #1 SMP Fri Apr 4 00:51:59 UTC 2014
nodename: uts-choice.novalocal
machine: x86_64
detected number of CPU cores: 1
current working directory: /home/ec2-user
writing pidfile to /run/uwsgi/uwsgi.pid
detected binary path: /usr/sbin/uwsgi
setgid() to 996
setuid() to 996
*** WARNING: you are running uWSGI without its master process manager ***
your processes number limit is 1024
*** starting uWSGI Emperor ***
[emperor-tyrant] invalid permissions for vassal choice.ini
[emperor-tyrant] invalid permissions for vassal hello.ini
[emperor-tyrant] invalid permissions for vassal choice.ini
[emperor-tyrant] invalid permissions for vassal hello.ini
^C[emperor] *** RAGNAROK EVOKED ***
$ 
</pre>


<h3>Problem: 504 Gateway Time-out - April 2015</h3>

<pre>
2015.03.20  Estimating main effects only.
This shows an nginx error (see screenshot) which says:
"The page you are looking for is temporarily unavailable".

1. Test via command line: 

choice/$ ./process_choices.py $dir $operation $effects
         time ./process_choices.py test/2015.03.20 check main 

Time taken: 2.5 minutes
Creates: out_bmat.dat   OK
         out_cinv.dat   OK
         out_cmat.dat   OK
         out_correln.dat    OK
         out_lmat.dat   OK
         out_msg.dat    OK

2. Test via http://localhost:8080/:
   Make sure TEST exists.

Enter matrices then...
[submit]
 
temp/$ ps ax | grep python
 1010 ?        S      0:00 /usr/bin/python /usr/bin/denyhosts.py --daemon --config=/etc/denyhosts.conf
29614 pts/0    S+     0:00 python ./choice.py
29615 pts/0    Sl+    0:01 /bin/python ./choice.py
30337 pts/0    R+     0:18 python ./process_choices.py temp check main
30394 ?        Sl     0:01 /usr/bin/python -Es /usr/sbin/setroubleshootd -f
30856 pts/1    S+     0:00 grep --color=auto python
temp/$ 

All works fine. It just times out with nginx.

PS. Saved the output files to the test directory test/2015.03.20

3. Test via nginx:
   Make sure TEST does NOT exist.

$ uwsgi -- /etc/uwsgi/vassals/choice.ini

User sees this: 
    504 Gateway Time-out

Server nginx error logs shows this:
  2015/04/07 14:56:30 [error] 4818#0: *13 upstream timed out (110: Connection timed out) 
  while reading response header from upstream, client: 127.0.0.1,
  server: localhost, request: "POST /choice/process/ HTTP/1.1", upstream:
  "uwsgi://127.0.0.1:9001", host: "localhost", referrer: "http://localhost/choice/"

This occurs at 60 seconds, even if I have in /etc/nginx.conf 

    # These timeouts don't help in preventing "504 Gateway Time-out"
    #keepalive_timeout  65;
    #keepalive_timeout 200;
    #uwsgi_connect_timeout 200;
    #uwsgi_send_timeout 200; 

    # This timeout is the one required!
    uwsgi_read_timeout 200; 
    
Now ....
$ uwsgi -- /etc/uwsgi/vassals/choice.ini
...
spawned uWSGI worker 1 (and the only) (pid: 10925, cores: 1)
[pid: 10925|app: 0|req: 1/1] 127.0.0.1 () {44 vars in 747 bytes} [Tue Apr  7 15:28:00 2015] POST /choice/process/ => 
generated 6536801 bytes in 148932 msecs (HTTP/1.1 200) 2 headers in 84 bytes (2 switches on core 0)

and 

No nginx timeout !!!! Good

See the TODO.txt for timeout information.
</pre>

<h3>Problem: need uwsgi-plugin-python</h3>

<p>The problem was that the uwsgi process could not be started. </p>

<pre>
[ec2-user@choice2 hello]$ uwsgi --http-socket :9090 --plugin python --wsgi-file hello.py
open("/usr/lib64/uwsgi/python_plugin.so"): No such file or directory [core/utils.c line 3639]
!!! UNABLE to load uWSGI plugin: /usr/lib64/uwsgi/python_plugin.so: cannot open shared object file: No such file or directory !!!
uwsgi: unrecognized option '--wsgi-file'
getopt_long() error
[ec2-user@choice2 hello]$ 
</pre>

<p>Installed uwsgi-plugin-python </p>

<pre>
[ec2-user@choice2 hello]$ uwsgi --http-socket :9090 --plugin python --wsgi-file hello.py
*** Starting uWSGI 1.9.19 (64bit) on [Tue Jan  7 12:21:26 2014] ***
compiled with version: 4.8.2 20131017 (Red Hat 4.8.2-1) on 12 November 2013 18:02:19
os: Linux-3.10.10-200.fc19.x86_64 #1 SMP Thu Aug 29 19:05:45 UTC 2013

Now lynx http://localhost:9090 shows OK
</pre>


<h3>Problem: nginx/python run problems</h3> 

<p>This is what you should have:</p>

<pre>
[ec2-user@choice2 public_html]$ ps ax | grep choice
 7235 pts/0    S      0:00 python ./choice.py
 7236 pts/0    Sl     0:00 /usr/bin/python ./choice.py
[ec2-user@choice2 public_html]$ 
</pre>

<p>If you get this error on Nectar: <tt>Error: 502 Bad Gateway</tt> then 
chances are that nginx is runing but the <tt>choice.py</tt> app is not.
Try running it manually from the command line to see any errors. 
Don't background it so you can see what the problem is.
</p>
 
<pre>
$ python ./choice.py   &lt;-- no &amp; to see what the problem is.
</pre>


<h3>Problem: sympy error</h3>

<p>Note: Get the sympy version with "import sympy; sympy.__version__"</p>
<pre>            Python    Sympy    Numpy
Laptop      2.7.3     0.7.1    1.6.2    
Windows     2.7.3     0.7.2    1.7.1
Nectar      2.7.5     0.7.3    1.7.1 &lt;-- has a sympy problem 
Nectar      2.7.5     0.7.2    1.7.1 &lt;-- works OK
LiveShell   2.7.5     0.7.3    1.6.1
</pre>

<p>On laptop running sympy 0.7.1</p>
<pre>
mlake$ python
Python 2.7.3 (default, Jul 24 2012, 10:05:38) 
[GCC 4.7.0 20120507 (Red Hat 4.7.0-5)] on linux2
>>> import sympy
>>> m=[1,2]
>>> sympy.Matrix(m)
[1]
[2]
>>> 
</pre>

<p>On Nectar server running sympy 0.7.3</p>
<pre>
[ec2-user@choice2$ python
Python 2.7.5 (default, Aug 22 2013, 09:31:58) 
[GCC 4.8.1 20130603 (Red Hat 4.8.1-1)] on linux2
>>> import sympy
>>> m=[1,2]
>>> sympy.Matrix(m)
Matrix([
[1],
[2]])
>>> 
</pre>

<p>Solved: Removed the yum package sympy (0.7.3) and installed sympy 0.7.2 from 
the tarball source package sympy-sympy-0.7.2.tar. The problem has now gone. 
</p>

<a name="refs"/><h2>Programming References to Python, uWSGI and nginx</h2>

<pre>
<a href="http://eli.thegreenplace.net/2011/08/22/how-not-to-set-a-timeout-on-a-computation-in-python">How (not) to set a timeout on a computation in Python</a>
<a href="http://howto.pui.ch/post/37471155682/set-timeout-for-a-shell-command-in-python">Set timeout for a shell command in python</a>
<a href="http://monicalent.com/blog/2013/12/06/set-up-nginx-and-uwsgi/">Monica Lent: set-up-nginx-and-uwsgi</a> Good definitions here 
<a href="http://michael.lustfield.net/nginx/bottle-uwsgi-nginx-quickstart">Bottle + UWSGI + Nginx Quickstart</a>
<a href="http://community.webfaction.com/questions/3998/how-to-setup-a-python-bottle-application">How to serve WSGI using Apache</a>
<a href="http://uwsgi-docs.readthedocs.org/en/latest/SystemD.html">Adding the Emperor to systemd</a>
<a href="http://jawher.me/2012/03/16/multiple-python-apps-with-nginx-uwsgi-emperor-upstart/">Running multiple python apps with nginx and uwsgi in emperor mode - March 2012</a>
<a href="http://www.oelerich.org/using-uwsgi-emperor-systemd/">Using the uWSGI Emperor with systemd</a>
<a href="http://note.kjuly.com/note/nginx-uwsgi-bottle/">NginX + uWSGI + Bottle</a>
<a href="http://linuxgazette.net/115/orr.html">WSGI Explorations in Python</a> Good overview
<a href="http://wiki.nginx.org/PythonFlup">PythonFlup</a>
<a href="http://wiki.nginx.org/HttpUwsgiModule">HttpUwsgiModule</a>
<a href="http://fclef.wordpress.com/2013/01/12/bottle-virtualenv-uwsgi-nginx-installation-on-ubuntu-12-04-1-lts">bottle-virtualenv-uwsgi-nginx-installation-on-ubuntu-12-04-1-lts/</a>
<a href="http://stackoverflow.com/questions/361855/how-to-gracefully-restart-django-running-fcgi-behind-nginx">how-to-gracefully-restart-django-running-fcgi-behind-nginx</a>
<a href="http://helpful.knobs-dials.com/index.php/Mod_wsgi_notes">Mod_wsgi_notes</a>
<a href="http://michael.lustfield.net/nginx/bottle-uwsgi-nginx-quickstart">bottle-uwsgi-nginx-quickstart</a>
<a href="http://articles.slicehost.com/2010/8/27/customizing-nginx-web-logs">customizing-nginx-web-logs</a>
<a href="http://stackoverflow.com/questions/7048057/running-python-through-fastcgi-for-nginx">running-python-through-fastcgi-for-nginx</a>
<a href="http://scardig.com/articoli/2010/02/03/Webpy-deployment-through-Nginx-Fastcgi-Spawn-fcgi-and-Flup.html">Webpy-deployment-through-Nginx-Fastcgi-Spawn-fcgi-and-Flup</a>
<a href="http://blog.richard.do/index.php/2013/04/setting-up-nginx-django-uwsgi-a-tutorial-that-actually-works/">setting-up-nginx-django-uwsgi-a-tutorial-that-actually-works</a>
<a href="http://daeyunshin.com/2013/01/06/nginx-uwsgi-django-flask-deployment.html">nginx-uwsgi-django-flask-deployment</a>
</pre>

