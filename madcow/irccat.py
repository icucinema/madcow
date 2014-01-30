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
        recipients_str, _, line = line.partition(' ')
        base_recipients = recipients_str.split(',')

        recipients = set()
        for recipient in base_recipients:
            if recipient == '#*':
                recipients = receipients | set(self.madcow.channels)
            elif recipient[0] == '@':
                recipients.add(recipient[1:])
            else:
                recipients.add(recipient)

        for recipient in recipients:
            request = Request(sendto=recipient)
            print "Sending", line, "to", recipient
            self.madcow.output(line, request)
        

class IRCCatServer(ThreadingMixIn, TCPServer):
    daemon_threads = True

    def __init__(self, madcow, *args, **kwargs):
        self.daemon_threads = True
        self.madcow = madcow

        TCPServer.__init__(self, *args, **kwargs)
