#!/usr/bin/python3
__author__ = "Jean-Baptiste Trystram"

import sys, os, socket, cprofile
from timeit import Timer


def help(detail, argument):
    if (detail == "all"):
        print ("No crypto alogorithm specified. It should be genEC, genRSA or test\n\
Usage : gen_n_test.py RSA -calength 4096 \n\
    gen_n_test.py EC -name sect571r1 \n\
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
        -cipher : value : specify a cipher you want to use for the tests. ")
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
    if (mode == 'RSA'):
        param = "genrsa"

        caKeySize = getOption(argv, "-CAlength")
        if not caKeySize:
            caKeySize = 4096

        clientKeySize = getOption(argv, "-Clientlength")
        if not clientKeySize:
            clientKeySize = 2048

        serverKeySize = getOption(argv, "-Serverlength")
        if not serverKeySize:
            serverKeySize = 2048

    if (mode == 'EC'):
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

    entities = ["ca", "server", "client"]
    for i in entities:
        j = 1
        # create paths to the files
        KeyFile = os.path.join(directory, i + ".key")
        CsrFile = os.path.join(directory, i + ".csr")
        CertFile = os.path.join(directory, i + ".crt")

        # prepare the command for the private key:
        # openssl = os.system("which openssl")
        openssl = ("/usr/bin/openssl " + param + " -out " + KeyFile + " ")
        if (mode == "RSA"):
            if (i == "ca"):
                keysize = str(caKeySize)
            elif (i == "server"):
                keysize = str(serverKeySize)
            else:
                keysize = str(clientKeySize)
            openssl = openssl + keysize
        else:
            openssl = openssl + " -genkey"
        # generate Private key
        print(openssl)
        os.system(openssl)
        if (i != "ca"):
            # Certificate Signing Request
            print ("############################ THIS IS THE " + i + " CERTIFICATE")
            os.system("openssl req -new -key " + KeyFile + " -out " + CsrFile)
            # answer the openSSL questions (organisation, name,  etc)
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


def test(directory, port, resumption, cipher, clientBindAddress, serverMode, inputArgs):
    os.chdir(directory)

    if serverMode:
        # launch server in another window
        print ("Launching server..")
        serverCommand = 'gnome-terminal --profile hold -e "openssl s_server -accept {0} -key server.key -cert server.crt -CAfile ca.crt -Verify 2 {1} {2} "'\
            .format(str(port), (' -cipher {0}'.format(cipher)) if cipher else "", (' <<< {0}'.format(inputArgs)) if inputArgs else "")
        os.system(serverCommand)

    if clientBindAddress:
        print ("Launching client..")
        clientCommand = 'os.system(\"echo | openssl s_client -connect {0}:{1} -cert client.crt -key client.key -CAfile ca.crt {2} -quiet -no_ign_eof ")'\
        .format(clientBindAddress, str(port), ("-reconnect" if (resumption) else ""))
        time = Timer(clientCommand, 'import os')
        print ("%.2f msec " % (1000 * time.timeit(number=1)))

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # the first argument should define the mode : RSA, EC or test.
    if (len(argv) < 2):
        help("all")
    mode = argv[1]
    if (mode.upper() == "RSA"):
        mode = "RSA"
    elif (mode.upper() == "EC"):
        mode = "EC"
    elif (mode.upper() == "TEST"):
        mode = "test"
    else:
        help("all")

    # do we have a specific directory
    workDir = getOption(argv, "-dir")
    if not workDir :
        workDir = os.getcwd()

    # Now we can decide what to do
    if (mode == "RSA" or mode == "EC"):
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
        if not port :
                port = 4433

        if (server and clientAddress) or not(server and clientAddress):
            server = True
            clientAddress = "127.0.0.1"
        elif clientAddress:
            clientAddress = isValidIP(clientAddress)

        # Check for incompatible options
        if resumption and inputArgs:
            help("incompatibleOptionResumption")

        # Launch the tests
        test(workDir, port, resumption, cipher, clientAddress, server, inputArgs)


if __name__ == "__main__":
    main()

#-naccept count
#    The server will exit after receiving number connections, default unlimited.



    # launch server in another window

    # gnome-terminal -x sh -c "openssl s_server -accept 4433 -key server.key -cert server.crt -CAfile ca.crt -Verify 2"

    # echo "Server is launch, launching client :"
    # openssl s_client -connect localhost:4433 -cert client_ec.crt -key client_ec.key -CAfile ca.crt
