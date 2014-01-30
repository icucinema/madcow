from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler

from .util import Request

class IRCColours(object):
    COLOUR_PREFIX = "\x03"

    NORMAL    = "\x0f"
    BOLD      = "\x02"
    UNDERLINE = "\x1f"
    REVERSE   = "\x16"

    WHITE      = COLOUR_PREFIX + "00"
    BLACK      = COLOUR_PREFIX + "01"
    DARK_BLUE  = COLOUR_PREFIX + "02"
    DARK_GREEN = COLOUR_PREFIX + "03"
    RED        = COLOUR_PREFIX + "04"
    BROWN      = COLOUR_PREFIX + "05"
    PURPLE     = COLOUR_PREFIX + "06"
    OLIVE      = COLOUR_PREFIX + "07"
    YELLOW     = COLOUR_PREFIX + "08"
    GREEN      = COLOUR_PREFIX + "09"
    TEAL       = COLOUR_PREFIX + "10"
    CYAN       = COLOUR_PREFIX + "11"
    BLUE       = COLOUR_PREFIX + "12"
    MAGENTA    = COLOUR_PREFIX + "13"
    DARK_GRAY  = COLOUR_PREFIX + "14"
    LIGHT_GRAY = COLOUR_PREFIX + "15"

    export = [
        'NORMAL', 'BOLD', 'UNDERLINE', 'REVERSE',
        'WHITE', 'BLACK', 'DARK_BLUE', 'DARK_GREEN',
        'RED', 'BROWN', 'PURPLE', 'OLIVE', 'YELLOW',
        'GREEN', 'TEAL', 'CYAN', 'BLUE', 'MAGENTA',
        'DARK_GRAY', 'LIGHT_GRAY'
    ]
    prefix_chars = '%#'

    @classmethod
    def colourise(cls, line):
        for prefix_char in cls.prefix_chars:
            for colour in cls.export:
                line = line.replace(prefix_char + colour, getattr(cls, colour))
        return line

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

        line = IRCColours.colourise(line)

        recipients = set()
        for recipient in base_recipients:
            if recipient == '#*':
                recipients = recipients | set(self.madcow.channels)
            elif recipient[0] == '@':
                recipients.add(recipient[1:])
            elif recipient[0] == '#':
                recipients.add(recipient)
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
