import os
from serv import HTTPError


def serve_static(address, root): 

    size = len(address)
    def pattern(request):
        return request.url.startswith(address)

    def handler(request): 
        try:
            fd = "%s/%s" % (root, request.url[size:])
            request.start_response(content_length=str(os.stat(fd).st_size))
            return open(fd)

        except IOError:

            if IOError.errno == 2:
                raise HTTPError(404) # No such file or directory

            if IOError.errno == 13:
                raise HTTPError(403) # Permission denied

            if IOError.errno == 21:
                raise HTTPError(403) # Is a directory

    return pattern, handler
