import os, time
from serv import HTTPError



def serve_static(address, root, **options): 

    size = len(address)
    def pattern(request):
        return request.url.startswith(address)

    def handler(request): 
        path = "%s/%s" % (root, request.url[size:])
        if os.path.isdir(path) and options['autoindex']:
            request.start_response()
            files_list = os.listdir(path)
            return ["%s\t%s\t%s\n"%(file, str(os.stat(file).st_size), time.strftime('%a, %d %b %Y %H:%I:%S GMT', time.gmtime(os.stat(file).st_mtime))) for file in files_list]

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
