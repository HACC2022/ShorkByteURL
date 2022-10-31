from http.server import HTTPServer
from request_handler import RequestHandler
from settings import DOMAIN, PORT

def main() -> None:
    httpd: HTTPServer = HTTPServer((DOMAIN, PORT), RequestHandler)
    print("Running Server...")
    httpd.serve_forever()

if __name__ == '__main__':
    main()