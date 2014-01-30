from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler

from .util import Request

class IRCCatRequestHandler(StreamRequestHandler):
    def __init__(self, *args, **kwargs):
        StreamRequestHandler.__init__(self, *args, **kwargs)

        self.madcow = self.server.madcow
  
    def handle(self):
        self.madcow = self.server.madcow
        while True:
            ln = self.rfile.readline().strip()
            self.handle_line(ln)

    def handle_line(self, line):
        if len(line) < 4 or ' ' not in line:
            self.wfile.write('ERROR line empty or invalid\n')
            return
        
        recipients_str, _, line = line.partition(' ')
        base_recipients = recipients_str.split(',')

        recipients = set()
        for recipient in base_recipients:
            if recipient == '#*':
                recipients = recipients | set(self.madcow.channels)
            elif recipient[0] == '@':
                recipients.add(recipient[1:])
            elif recipient[0] == '#':
                recipients.add(recipient[1:])
            else:
                # nope
                self.wfile.write('ERROR recipient {} invalid\n'.format(recipient))
                continue

        for recipient in recipients:
            request = Request(sendto=recipient)
            print "Sending", line, "to", recipient
            self.madcow.output(line, request)
            
        self.wfile.write('OK\n')
        

class IRCCatServer(ThreadingMixIn, TCPServer):
    daemon_threads = True

    def __init__(self, madcow, *args, **kwargs):
        self.daemon_threads = True
        self.madcow = madcow

        TCPServer.__init__(self, *args, **kwargs)
