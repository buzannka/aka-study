import os
from serv import HTTPError

def iterable_files_list(files_list):
   for file in files_list:
      yield ("%s \t %s \n"%(file, str(os.stat(file).st_size)))


def serve_static(address, root): 

    size = len(address)
    def pattern(request):
        return request.url.startswith(address)

    def handler(request): 
        path = "%s/%s" % (root, request.url[size:])
        if os.path.isdir(path) and request.headers['AUTOINDEX']:
            request.start_response()
            files_list = os.listdir(path)
            return iterable_files_list(files_list)  
        try:
            request.start_response(content_length=str(os.stat(path).st_size))
            return open(path)

        except IOError:

            if IOError.errno == 2:
                raise HTTPError(404) # No such file or directory

            if IOError.errno == 13:
                raise HTTPError(403) # Permission denied

            if IOError.errno == 21:
                raise HTTPError(403) # Is a directory

    return pattern, handler
