from http.server import SimpleHTTPRequestHandler
from typing import Dict, List, Optional, Tuple, Union
from db_manager import DBManager
from url_manager import URLManager
from url_pair import URLPair
from settings import DOMAIN, PORT, PAGES_HOME, LOCAL_PAGES_HOME
import urllib.parse, os, json

public_dir: str = os.path.dirname(os.path.realpath(__file__))

routes: List[Tuple[str, str]] = [
    ('/test', os.path.join(LOCAL_PAGES_HOME, 'foo.html')),
    ('/compress', os.path.join(LOCAL_PAGES_HOME, 'url_test.html')),
    ('/login', os.path.join(LOCAL_PAGES_HOME, 'login', 'index.html')),
    ('/admin', os.path.join(LOCAL_PAGES_HOME,'admin', 'index.html'))
]

class RequestHandler(SimpleHTTPRequestHandler):
    db_manager: DBManager = DBManager(requests_query='server/db/query_requests.sql')
    url_manager: URLManager = URLManager(db_manager)

    def _set_success_headers(self) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def _set_success_css_headers(self) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()
    
    def _set_redirect_headers(self, url:str) -> None:
        self.send_response(301)
        self.send_header('Location', url)
        self.end_headers()
    
    def _send_error_response(self) -> None:
        self.send_response(500)
    
    def handle_args(self, path:str) -> str:
        if not '?' in path: return ''
        try:
            root, args = tuple(path.split('?'))
            arg_dict: dict[str, str] = {key: value for key, value in [tuple(kv_pair.split('=')) for kv_pair in args.split("&")] }
            if root == '/login':
                if 'username' in arg_dict and arg_dict['username'] == 'admin' and 'pass' in arg_dict and arg_dict['pass'] == 'admin':
                    return '/admin'
        except Exception as e:
            print("------------ERROR:", e)
        return ''

    def handle_action(self, path:str) -> bool:
        if path == "/clear":
            self.url_manager.clear()
            # return True
        return False
    
    def check_pages_path(self, path:str) -> str:
        roots: List[str] = [
            PAGES_HOME,
            os.path.join(PAGES_HOME, "login")
        ]
        for root in roots:
            file_path: str = os.path.join(root, "." + path)
            if(os.path.isfile(file_path)): return file_path
        return ""

    def handle_path(self, path:str) -> Optional[str]:
        file_path: str = self.check_pages_path(path)
        if file_path: return file_path

        arg_path: str = self.handle_args(path)
        if arg_path:
            self._set_redirect_headers(arg_path)
            return 

        handle_action_resp: bool = self.handle_action(path)
        if handle_action_resp:
            return
        
        # default route
        new_path: str = os.path.join(LOCAL_PAGES_HOME, "login", "index.html")

        orig_url: str = self.url_manager.get(path, status='accepted')
        if orig_url:
            print("Redirecting to:", orig_url)
            self._set_redirect_headers(orig_url)
            return
        # look up routes and get root directory
        for pattern, route in routes:
            if path.startswith(pattern):
                new_path = route
                break

        # new path
        result: str = os.path.join(public_dir, new_path)
        return result
    
    def handle_GET(self) -> None:
        path: Optional[str] = self.handle_path(self.path)
        if path is None: return

        # get html file path

        if not os.path.isfile(path):
            print("Invalid file:", path)
            path = self.handle_path("/")
            if path is None: return
        
        # send html header
        self._set_success_headers() if not path.endswith(".css") else self._set_success_css_headers()
        # Send the content of the html
        with open(path, "rb") as f:
            self.wfile.write(f.read())

    def do_GET(self) -> None:
        try:
            self.handle_GET()
        except:
            self._send_error_response()
        
    
    def handle_POST(self) -> None:
        self._set_success_headers()
        # print("Content:", self.headers)
        content_len: int = int(self.headers.get('Content-Length', '0'))
        post_body: bytes = self.rfile.read(content_len)
        # print("Body:", post_body)
        contents: List[str] = post_body.decode("utf-8").split("&")
        post_dict: Dict[str,str] = { key:value for item in contents for key, value in [item.split("=")]}
        
        request_type: str = post_dict.get('request_type', '')
        if not request_type:
            print("No request type!")
            return

        response: str = "{}"

        if request_type == "url_requests":
            response = json.dumps(self.db_manager.exec_w_headers('requests_query'))
            
        elif request_type == "update_status":
            url_id: int = int(post_dict.get('url_id', '-1'))
            status: str = post_dict.get('status', '')
            if url_id < 0 or not status:
                print("Invalid url_id: '{}' or status: '{}'".format(url_id, status))
                return
            
            self.url_manager.update_status(url_id, status)
        else:
            url_data: str = post_dict.get('url_data', '')
            parsed_url: str = urllib.parse.unquote(url_data)
            # print("URL request:", url_data, "->", parsed_url)
            if not parsed_url:
                print("No URL!")
                return
            
            if request_type == 'compress':
                short_url: Optional[str] = self.url_manager.append(parsed_url)
                if short_url is None:
                    print("Failed to compress URL")
                    return

                response = "{}:{}{}".format(DOMAIN, PORT, short_url)
            elif request_type == "verify":
                url_pair: Union[URLPair, None] = self.url_manager.find_pair(parsed_url, status='accepted')
                response = json.dumps({
                    "verified": True,
                    "short_url": url_pair.short_url,
                    "orig_url": url_pair.orig_url
                } if url_pair else {
                    "verified": False
                })

        self.wfile.write(response.encode('utf-8'))
        
    def do_POST(self) -> None:
        try:
            self.handle_POST()
        except:
            self._send_error_response()
    
    def end_headers (self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)
