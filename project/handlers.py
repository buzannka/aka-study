import os, time
from serv import HTTPError

def serve_static(address, root, **options): 

    size = len(address)
    def pattern(request):
        return request.url.startswith(address)

    def handler(request): 
        path = "%s/%s" % (root, request.url[size:])
        if os.path.isdir(path) and options['autoindex']:
            files_list = sorted((((not os.path.isdir('%s/%s' % (path, name))), name) for name in os.listdir(path) if not name.startswith('.')), key=lambda name: name[1].lower())
            files_list = sorted(files_list, key=lambda name: name[0])
            files_list.insert(0, (False, '..'))
            body = '<br/>\n'.join(('<a href="%s">%s</a>' if mode else '<a href="%s/"><b>%s/</b></a>')  % (name, name) for mode, name in files_list)
            request.reply(body, content_type='text/html; charset=utf-8')
            return
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
