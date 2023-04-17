from http.server import HTTPServer, BaseHTTPRequestHandler;
import json;
import sqlite3
import sys;     # to get command line argument for port
import urllib;  # code to parse for data
from urllib.parse import parse_qs
import molsql;
import io
import molecule


# list of files that we allow the web-server to serve to clients
# (we don't want to serve any file that the client requests)


home = 'localhost:' + sys.argv[1] + '/'
loaded_mol = None

class MyHandler( BaseHTTPRequestHandler ):
    # create a molecule
    
    #create a sql database
    
    
    # database['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
    # database['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
    # database['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
    # database['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );
    
    def do_GET(self):

        # used to GET a file from the list ov public_files, above
        if self.path == '/':   # make sure it's a valid file
            self.send_response( 200 );  # OK
            self.send_header( "Content-type", "text/html" )

            fp = open( 'public/index.html', 'r')

            # load the specified file
            page = fp.read()
            fp.close()

            # create and send headers
            self.send_header( "Content-length", len(page) );

            self.end_headers();
            # send the contents
            self.wfile.write( bytes( page, "utf-8" ) )
            

        elif self.path == '/static/style.css':   # make sure it's a valid file
            self.send_response( 200 );
            self.send_header( "Content-type", "text/css" )
            fp = open( 'public/static/style.css', 'r')
            css = fp.read()
            fp.close()
            self.send_header( "Content-length", len(css) )
            
            self.end_headers();
            self.wfile.write( bytes( css, "utf-8" ) )
        
        elif self.path == '/static/script.js':   # make sure it's a valid file
            self.send_response( 200 );
            self.send_header( "Content-type", "text/js" )
            fp = open( 'public/static/script.js', 'r')
            js = fp.read()
            fp.close()
            self.send_header( "Content-length", len(js) )
            
            self.end_headers();
            self.wfile.write( bytes( js, "utf-8" ) )
        
        elif self.path == '/static/favicon_io/favicon.ico':   # make sure it's a valid file
            self.send_response( 200 );
            self.send_header( "Content-type", "image/x-icon" )
            fp = open( 'public/static/favicon_io/favicon.ico', 'rb')
            favicon = fp.read()
            fp.close()
            self.send_header( "Content-length", len(favicon) )
            self.end_headers();
            self.wfile.write( favicon )
            
        # view get request 
        elif self.path == '/view':
            # print("in view")
            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Molecules')
            rows = cursor.fetchall()
            data = []
            # print(rows)
            
            for row in rows:
                d = {}
                d['id'] = row[0]
                d['name'] = row[1]
                data.append(d)
            
            json_data = json.dumps(data)
            conn.close()
            # print(json_data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write( bytes( json_data, "utf-8" ) )
            # print('\n')
            # print("end of view")
            
        elif self.path == '/viewElement':
            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Elements')
            rows = cursor.fetchall()
            data = []
            for row in rows:
                d = {}
                d['elno'] = row[0]
                d['elcode'] = row[1]
                d['elname'] = row[2]
                d['col1'] = row[3]
                d['col2'] = row[4]
                d['col3'] = row[5]
                d['rad'] = row[6]
                data.append(d)
            json_data = json.dumps(data)
            conn.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write( bytes( json_data, "utf-8" ) )
            
        else:
            # if the requested URL is not one of the public_files
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );



    def do_POST(self):
        # print( "POST request received")
        # print(self.path)
        global loaded_mol
        database = molsql.Database()
        
        
        if self.path == "/upload":
        
            print("in upload")
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            self.rfile.close()
            data = data.decode('utf-8').strip()
            print('data', data)
            
            fp = io.StringIO(data)
            
            for i in range(0,3):    # skip 3 lines
                # print(self.rfile.readline())
                fp.readline()
            
            name = fp.readline().strip()
            print(name)
            # print("testingname")
            for i in range(0,4):    # skip 4 lines
                # print(self.rfile.readline())
                fp.readline()
            database.add_molecule( name, fp);
            # self.path = "/"
            self.send_response(200)
            # self.send_header('Location', '/')
            self.end_headers()
        
        elif self.path == "/remove_element":
            print("in remove")
            length = int(self.headers['Content-length'])
            post_data = self.rfile.read(length)
            self.rfile.close()
            print(post_data)
            data = post_data.decode('utf-8')
            print(data)
            database.delete_element(data)
            self.send_response(200)
            self.end_headers()
                
                              
        elif self.path == "/rotation_values":
            # print("in rotate")
            # print(loaded_mol.svg())
            
            
            length = int(self.headers['Content-length'])
            post_data = self.rfile.read(length)
            self.rfile.close()

            data = json.loads(post_data.decode('utf-8'))
            print("data", data)

            direction = data['direction']
            rotation = int(data['rotation'])
            mx = None
            
            if(direction == 'x'):
                mx = molecule.mx_wrapper(rotation,0,0)
            elif(direction == 'y'):
                mx = molecule.mx_wrapper(0,rotation,0)
            elif(direction == 'z'):
                mx = molecule.mx_wrapper(0,0,rotation)
            else:
                print('failed')
            
            loaded_mol.xform(mx.xform_matrix)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            self.wfile.write( bytes( loaded_mol.svg(), "utf-8" ) )
            

            
        #     self.send_response(302)
        #     self.send_header('Location', '/')       
        #     self.end_headers()   
            
            
            
        elif self.path == "/add_element":
            print("in addElement")
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.rfile.close()
            data = json.loads(post_data.decode('utf-8'))
            
            print(data)
            
            
            elno = int(data['elno'])
            elcode = data['elcode']
            elname = data['elname']
            col1 = data['col1']
            print(col1)
            col1 = col1[1:] if col1 else col1
            print(col1)
            col2 = data['col2']
            col2 = col2[1:] if col2 else col2
            col3 = data['col3']
            col3 = col3[1:] if col3 else col3
            rad = float(data['rad'])
            
            # print(elno, elcode, elname, col1, col2, col3, rad)
            
            database['Elements'] = ( elno, elcode, elname, col1, col2, col3, rad )
            
            # print(self.path)
            self.send_response(200)
            # self.send_header('Location', '/')
            self.end_headers()
            # self.wfile.write(bytes())
            
            
            
        elif self.path == "/viewSVG":
            self.send_response( 200 );  # OK
            print("in viewSVG")
            length = int(self.headers['Content-Length'])
            name = self.rfile.read(length).decode('utf-8').strip()
            
            load_mol = database.load_mol(name)
            loaded_mol = load_mol
            self.end_headers()
            self.wfile.write(bytes(load_mol.svg(), "utf-8"))
            
            print("end of viewSVG")
            
            # molecule = database.load_mol(name)
            # return molecule
            
        elif self.path == "/form_handler":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            print( postvars );

            message = "data received";

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );
            redirect_handler_factory("localhost:59803/")
            
            

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );

def redirect_handler_factory(url):
    """
    Returns a request handler class that redirects to supplied url
    """
    class RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(301)
            self.send_header('Location', url)
            self.end_headers()

            return RedirectHandler



httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
httpd.serve_forever();
