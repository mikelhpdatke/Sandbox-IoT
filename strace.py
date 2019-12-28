import sys
import subprocess
import json
from datetime import datetime
import time
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

class Strace:
    def __init__(self, target):
        self.target = target
        self.proc = None

    def start(self):
        print('strace start..')
        self.proc = subprocess.Popen(['/usr/bin/strace', '-tt', '/root/agent/0a6669f1bbbb687e1495d1d875eedcbe'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        # p.wait()
        print('after sub')
        err, data = self.proc.communicate('\n')
        print(err, data)
        data = data.decode('utf8').split('\n')
        res = []
        print(data)
        for line in data[:-1]:
            obj = {}
            now = datetime.now().strftime('%Y/%m/%d ') + str(line[:line.find(' ')])
            cur = datetime.strptime(now,'%Y/%m/%d %H:%M:%S.%f')

            obj['timestamp'] = int(time.mktime(cur.timetuple()))
            line = line[line.find(' ')+1:]
            obj['name'] = line[:line.find('(')]
            line = line[line.find('(')+1:]
            obj['return'] = line[line.rfind('=')+1:-1].strip()
            line = line[:line.rfind('=')-1]
            obj['arguments'] = line[:line.rfind(')')].strip()
            res.append(obj)
        with open(self.target+'_strace_log.json', 'w') as f:
            json.dump(res, f)

    def stop(self):
        """Stop.
        @return: operation status.
        """
        # The tcpdump process was never started in the first place.
        if not self.proc:
            return

        # The tcpdump process has already quit, generally speaking this
        # indicates an error such as "permission denied".
        if self.proc.poll():
            out, err = self.proc.communicate()
            raise Exception(
                "permission-denied-for-strace"
            )

        try:
            self.proc.terminate()
        except:
            try:
                if not self.proc.poll():
                    log.debug("Killing strace")
                    self.proc.kill()
            except OSError as e:
                log.debug("Error killing strace: %s. Continue", e)
            except Exception as e:
                log.exception("Unable to stop the strace with pid %d: %s",
                              self.proc.pid, e)

        # Ensure expected output was received from strace.
        out, err = self.proc.communicate()
        log.debug(out, err)