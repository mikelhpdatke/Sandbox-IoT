import sys
import subprocess
import json
from datetime import datetime
import time
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

class Top:
    def __init__(self):
        self.proc = None

    def start(self):
        res = []
        self.proc = subprocess.Popen(['top', '-bn 1'], stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        data = self.proc.communicate()[0].decode('utf8').split('\n')
        obj = {}
        now = time.mktime(datetime.now().timetuple())
        obj['timestamp'] = int(now)

        data0 = data[0].split(',')
        temp = data0[1].strip()
        obj['num_user_login'] = temp[:temp.find(' ')]
        obj['load_avg'] = []
        temp = data0[2].strip()
        obj['load_avg'].append(temp[temp.rfind(' ')+1:])
        obj['load_avg'].extend([data0[3].strip(), data0[4].strip()])

        data1 = data[1].split(',')
        temp = data1[0].strip()
        obj['num_total_tasks'] = temp[temp.find(' ')+1:temp.rfind(' ')]
        obj['num_total_running'] = data1[1].strip()[:data1[1].strip().find(' ')]
        obj['num_total_sleeping'] = data1[2].strip()[:data1[2].strip().find(' ')]
        obj['num_total_stopped'] = data1[3].strip()[:data1[3].strip().find(' ')]
        obj['num_total_zombie'] = data1[4].strip()[:data1[4].strip().find(' ')]

        data2 = data[2].split(',')
        temp = data2[0].strip()
        obj['cpu_%_us'] = temp[temp.find(' ')+1:temp.rfind(' ')]
        obj['cpu_%_sy'] = data2[1].strip()[:data2[1].strip().find(' ')]
        obj['cpu_%_ni'] = data2[2].strip()[:data2[2].strip().find(' ')]
        obj['cpu_%_id'] = data2[3].strip()[:data2[3].strip().find(' ')]
        obj['cpu_%_wa'] = data2[4].strip()[:data2[4].strip().find(' ')]
        obj['cpu_%_hi'] = data2[5].strip()[:data2[5].strip().find(' ')]
        obj['cpu_%_si'] = data2[6].strip()[:data2[6].strip().find(' ')]
        obj['cpu_%_st'] = data2[7].strip()[:data2[7].strip().find(' ')]

        data3 = data[3].split(',')
        temp = data3[0].strip()
        obj['mem_total'] = temp[temp.find(':')+3:temp.rfind(' ')].strip()
        obj['mem_free'] = data3[1][:data3[1].rfind(' ')].strip()
        obj['mem_used'] = data3[2][:data3[2].rfind(' ')].strip()
        obj['mem_buffers'] = data3[3][:data3[3].rfind(' ')].strip()

        data4 = data[4].split(',')
        temp = data4[0].strip()
        obj['swap_total'] = temp[temp.find(':')+3:temp.rfind(' ')].strip()
        obj['swap_free'] = data4[1][:data4[1].rfind(' ')].strip()
        try:
            obj['swap_used'] = data4[2][:data4[2].rfind(' ')].strip()
            obj['swap_cache'] = data4[3][:data4[3].rfind(' ')].strip()
        except:
            print('\33[91m{}\33[00m'.format('tesing... Ubuntu'))
            temp = data4[2].split('.')
            obj['swap_used'] = temp[0][:temp[0].rfind(' ')].strip()
            obj['avail_mem'] = temp[1].strip()[:temp[1].strip().find(' ')]

        obj['process'] = []
        for line in data[7:-1]:
            temp = line.split(' ')
            while '' in temp:
                temp.remove('')
            dat = {}
            dat['PID'] = temp[0].strip()
            dat['USER'] = temp[1].strip()
            dat['PR'] = temp[2].strip()
            dat['NI'] = temp[3].strip()
            dat['VIRT'] = temp[4].strip()
            dat['RES'] = temp[5].strip()
            dat['SHR'] = temp[6].strip()
            dat['S'] = temp[7].strip()
            dat['%CPU'] = temp[8].strip()
            dat['%MEM'] = temp[9].strip()
            dat['TIME+'] = temp[10].strip()
            dat['COMMAND'] = temp[11].strip()
            obj['process'].append(dat)

        res.append(obj)

        with open('_top_log.json' + '.' + str(int(time.time())), 'w') as f:
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
                   "permission-denied-for-strace")


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
