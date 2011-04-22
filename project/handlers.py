import os, time
from serv import HTTPError



def serve_static(address, root, **options): 

    size = len(address)
    def pattern(request):
        return request.url.startswith(address)

    def handler(request): 
        path = "%s/%s" % (root, request.url[size:])
        if os.path.isdir(path) and options['autoindex']:
            request.start_response(content_type='text/html')
            request.headers_sent = True
            files_list = sorted((os.stat('%s%s' % (path, name)).st_mode, name) for name in os.listdir(path))
            return '<br/>'.join(('<a href="%s/"><b>%s</b></a>' if mode else '<a href="%s">%s</a>')  % (name, name) for mode, name in files_list)

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
