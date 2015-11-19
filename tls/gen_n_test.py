#!/usr/bin/python3
__author__ = "Jean-Baptiste Trystram"

import sys, os, socket, time, subprocess
from scapy.all import *
from threading import Thread

exchange_size = 0
tls_exchange_over = False

# TODO : if you want to do network-level measure, you should be prompted for your root password

def help(detail, argument=""):
    if (detail == "all"):
        print ("No crypto algorithm specified ! It should be genEC, genRSA or test\n\
########################################### \n\
Usage : gen_n_test.py RSA -calength 4096 \n\
    gen_n_test.py EC -curve sect571r1 \n\
    gen_n_test.py test -resumption -port 443 -dir /var/rsa_certs\n\
    gen_n_test.py test -client  -port 443 -input \"my mqtt Message\" \n\
This script generate EC or RSA certificates, or run a test-handshake and do measurements. (CPU consuption, memory and time) \n\
Available options : \n\
    For RSA : \n\
        -CAlength size : let you specify a length for the CA's RSA key. Default is 4096.\n\
        -Clientlength size : let you specify a length for the client's RSA key. Default is 2048.\n\
        -Serverlength size : let you specify a length for the client's RSA key. Default is 2048.\n\
                \n\
    For EC : \n\
        -curve curve : use the specified openSSL curve. Run 'openssl ecparam -list_curves' and pick one. \n\
            This is mandatory in EC mode and ignored in RSA mode. \n\
    For both algorithms : \n\
        -dir /path/ : specify the absolute or relative path to store the generated certs. Default is ./ \n\
    To run tests : (time, cpu and memory usage) \n\
        -port port : specify the server should listen on (or wether the client should connect to). Default is 4433. \n\
        -client ip : launch only the client and connect to the given ip \n\
        -server : launch only the server \n\
        if you don't specify any client nor server, then both will be launched on localhost. \n\
        -input string : used with -client option. let you specify an input text that should be sent to the server when handshake is done. \n\
        This option CANNOT BE USED along -resumption \n\
        -resumption : test the resumption mechanisms (5 connections in a row). CANNOT BE USED with -input \n\
        -dir /path/ : absolute or relative path to the previously generated certs to use. Default is ./ \n\
        -cipher : value : specify a cipher you want to use for the tests.")
        sys.exit()

    elif detail == "nocurve":
        print ("An eliptic curve MUST be specified when using EC generation. \n\
            Run 'openssl ecparam -list_curves' for a list of the available curves.")
        sys.exit()
    elif detail == "noServerIp":
        print ("The given IP cannot be used to connect to the server. Please provide a valid IP.")
        sys.exit()
    elif detail == "incompatibleOptionResumption":
        print ("The -resumption option cannot be used along input. Please modify your arguments.")
        sys.exit()
    elif detail == "argvError":
        print ("You need to enter a value after the {0} argument".format(argument))
        sys.exit()


def isValidIP(addr):
    try:
        socket.inet_aton(addr)
        return addr
    except socket.error:
        help("noServerIp")


def getOption(argv, string, justCheck=False):
    if string in argv:
        if justCheck :
            return True
        else :
            arg = argv.index(string)
        try:
            arg = argv[arg + 1]
            return arg
        except:
            help("argvError", string)
    else:
        return False


def generate(mode, directory, argv):
    # Set arguments for the openSSL command
    if mode == "rsa":
        param = "genrsa"

        caKeySize = getOption(argv, "-calength")
        if not caKeySize:
            caKeySize = 4096

        clientKeySize = getOption(argv, "-clientlength")
        if not clientKeySize:
            clientKeySize = 2048

        serverKeySize = getOption(argv, "-serverlength")
        if not serverKeySize:
            serverKeySize = 2048

    else :
        param = "ecparam"

        curve = getOption(argv, "-curve")
        if curve:
            param = param + " -name " + curve
        else:
            help("nocurve")

    # cert generation
    # create paths to the ca files
    caKeyFile = os.path.join(directory, "ca.key")
    caCertFile = os.path.join(directory, "ca.crt")

    for i in ["ca", "server", "client"]:
        j = 1
        # create paths to the files
        KeyFile = os.path.join(directory, i + ".key")
        CsrFile = os.path.join(directory, i + ".csr")
        CertFile = os.path.join(directory, i + ".crt")

        # prepare the command for the private key:
        openssl = ("/usr/bin/openssl /{0} -out {1}").format(param, KeyFile)
        if (mode == "rsa"):
            if (i == "ca"):
                keysize = str(caKeySize)
            elif (i == "server"):
                keysize = str(serverKeySize)
            else:
                keysize = str(clientKeySize)
            openssl += ' {0}'.format(keysize)
        else:
            openssl += " -genkey"
        # generate Private key
        os.system(openssl)
        if (i != "ca"):
            # Certificate Signing Request
            print ("############################ THIS IS THE " + i + " CERTIFICATE")
            os.system("openssl req -new -key {0} -out {1}".format(KeyFile,CsrFile))
            # TODO : automated answers the openSSL questions (organisation, name,  etc)
            # sign it with the CA
            os.system("openssl x509 -req -days 365 -in " + CsrFile + " -CA "
                      + caCertFile + " -CAkey " + caKeyFile + " -set_serial "
                      + str(j) + " -out " + CertFile)
            # delete the request file
            os.system("rm " + CsrFile)
            j += 1
        # if it's CA, sign itself :
        else:
            print ("############################# THIS IS THE " + i + " CERTIFICATE")
            os.system("openssl req -new -x509 -days 365 -key "
                      + caKeyFile + " -out " + caCertFile)


def generateServerCommand(port, resumption, cipher):

    serverCommand = '/usr/bin/openssl s_server -accept {0} -key server.key -cert server.crt -CAfile ca.crt -Verify 2 {1} {2} '\
        .format(str(port), (' -cipher {0}'.format(cipher)) if cipher else "",\
        '-naccept 2' if (resumption) else "" )
    return serverCommand


def generateClientCommand(port, resumption, clientBindAddress, inputArgs, cipher):
    clientCommand = 'echo "{4}"| openssl s_client -connect {0}:{1} -cert client.crt -key client.key -CAfile ca.crt {2} {3} -quiet -no_ign_eof' \
        .format(clientBindAddress, str(port), ("-reconnect" if (resumption) else ""),
                (' -cipher {0}'.format(cipher)) if cipher else "", inputArgs if inputArgs else "")
    return clientCommand


def pkt_size(packet):
    global exchange_size
    exchange_size += len(packet[TCP])

def stopperCheck():
    #global tls_exchange_over
    if tls_exchange_over:
        return True
    else: return False


def sniff_network(host, port):
    filter  = "host {0} and tcp and port {1}".format(host, port)
    pakets = sniff(filter=filter, prn=pkt_size, stopperTimeout=1, stopper=stopperCheck, store=1)
    # TODO : this should be optionnal and the file should be specified. The file have to be chown
    wrpcap("./trace.cap", pakets)


def perfTest(command, host, port):
    global exchange_size
    global tls_exchange_over
    # captureing network packets to get the overall size of the TCP exchange
    capture = Thread(target=sniff_network, args=(host, port))
    # Making the thread a daemon force it to qui when all other threads are exited.
    capture.start()

    # Thread needs a bit of time
    time.sleep(1)
    # Start the timers
    sysstart = time.perf_counter()
    start = time.process_time()
    #Run the command !
    #client_process = subprocess.Popen(command.split(), shell=False)
    #client_process.wait()
    os.system(command)
    # stop the timers
    stop = time.process_time()
    sysstop = time.perf_counter()

    global tls_exchange_over
    tls_exchange_over = True

    stats = {'Time (ms)': (sysstop-sysstart)*1000, 'CPU time (ms)': (stop-start)*1000}
    # cpu usage = processTime / System-wide time
    stats['cpu usage (%)'] = (stats['CPU time (ms)']/stats['Time (ms)'])*100

    #if capturing on localhost, divide the size by 2 because each p acket is sniffed twice.
    if host == "127.0.0.1":
        exchange_size /= 2
    stats['TCP size (bytes)'] = exchange_size
    return stats

def main(argv=None):
    if argv is None:
        #lowercase all arguments
        argv = [x.lower() for x in sys.argv]

    # the first argument should define the mode : RSA, EC or test.
    if (len(argv) < 2):
        help("all")
    mode = argv[1]
    if mode not in ["rsa", "ec", "test"]:
        help("all")

    # do we have a specific directory
    workDir = getOption(sys.argv, "-dir")
    if workDir :
        if not (os.path.isdir(workDir)):
            try :
                os.makedirs("./{0}".format(workDir))
            except OSError as exception:
                wd = os.path.join(os.getcwd(), workDir)
                print ("can't create {0} . exit.".format(wd))
                sys.exit()
    else :
        workDir = os.getcwd()

    # Now we can decide what to do
    if mode in ['rsa', 'ec']:
        generate(mode, workDir, argv)
    else:
        # get special parameters from the arguments
        port = getOption(argv, "-port")
        cipher = getOption(argv, "-cipher")
        clientAddress = getOption(argv, "-client")
        inputArgs = getOption(argv, "-input")

        resumption = getOption(argv, "-resumption", justCheck=True)
        server = getOption(argv, "-server", justCheck=True)

        # Assigning default values
        if not port:
                port = 4433

        if cipher and ("PSK" in cipher):
            cipher = "{0} -psk c033f52671c61c8128f7f8a40be88038bcf2b07a6eb3095c36e3759f0cf40837".format(cipher)

        if (server and clientAddress) or (not server and not clientAddress):
            server = True
            clientAddress = "127.0.0.1"
        elif clientAddress:
            clientAddress = isValidIP(clientAddress)

        # Check for incompatible options
        if resumption and inputArgs:
            help("incompatibleOptionResumption")

        # cd in the appropriate directory
        os.chdir(workDir)
        # if needed generate the openssl command to run for the server then run it
        if server:
            srvCommand = generateServerCommand(port, resumption, cipher)
            # launch server in another window
            print("Launching server..")
            server_process = subprocess.Popen(srvCommand.split(), shell=False, stdout=subprocess.PIPE)
            print("SERVER PID IS {0}".format(server_process.pid))

        # Same for the client
        if clientAddress :
            cliCommand = generateClientCommand(port, resumption, clientAddress, inputArgs, cipher)
            print("Launching client & measurements")
            #do measurements
            perfs = perfTest(cliCommand, clientAddress, port)
            print("Results : {0}".format(str(perfs)))
            f = open('result.txt', 'a+', encoding="utf-8")
            for key, value in perfs.items() :
                f.write("{0} : {1}, ".format(key, ("%.3f" % value)))
            f.write("\n")
            #time.sleep(1)

        if server:
            # We can kill the server, since everything is done.
            server_process.kill()


if __name__ == "__main__":
    main()


#./gen_n_test.py test -client 127.0.0.1 -port 4433 -dir ec_certs/works/brainpoolP256r1/ -cipher NULL -input "$(< MQTT)"
