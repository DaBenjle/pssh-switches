from pssh.clients import ParallelSSHClient
from pssh.utils import enable_host_logger
from pssh.exceptions import Timeout
import sys
import os
import json
import argparse

#Returns an args object
def parse_command_line():
    parser = argparse.ArgumentParser(description="Used to ssh into several servers at once and perform a command while gathering the output here.")
    
    subparsers = parser.add_subparsers(help="Choose one of these sub commands. Run addCredential before attempting to run anything.")
    parser_addCredential = subparsers.add_parser('addCredential', help=f'Adds credential to credential file at {relativeCredentialPath}')
    parser_runInstruction = subparsers.add_parser('runInstruction', help='Runs a given instruction. (Use psshServers runInstruction -h for more details)')
    
    parser_addCredential.add_argument("--credentials", help="Despite its name, this is a non-optional argument.", nargs=2, metavar=('Username', 'Password'))

    parser_runInstruction.add_argument("hostFile", help="Host File path. Host files should contain ip addresses delimmited by a new line. (Should not contain any empty lines.)") #don't use the filetype feature as it leaves a dangling file open
    parser_runInstruction.add_argument('-p', '--proxy', nargs=3, help="Allows you to ssh into a proxy server (like an edge router) before running commands on all of the internal hosts (should be listed in given host file).", metavar=('ProxyHostIP', 'ProxyUserName', 'ProxyPrivateKeyFile'))

    named_me_group = parser_runInstruction.add_argument_group('Instructions', 'Select only one of these instructions to run.')
    me_group = named_me_group.add_mutually_exclusive_group(required=True)
    me_group.add_argument('-u', '--searchUnits', help="Runs: show configuration | match {Unit} | display set   on all hosts", metavar='Unit')
    me_group.add_argument('-m', '--searchMacs', help="Runs: show ethernet-switching table | match {MacAddress}   on all hosts", metavar='MacAddress')
    me_group.add_argument('-c', '--custom', help="Runs one or more custom commands (each command is run series per host) on all hosts (in parallel). Wrap commands in quotes \" and seperate commands with a space. You will have to use this command at the end. Specify your host file first before selecting this instruction. (You can do that for all instructions)", nargs='+', metavar='CustomCommand(s)')

    return parser.parse_args()

def runInstruction(args):
    #Set command based on arg flag
    command = None
    if args.searchUnits is not None:
        command = f'show configuration | match {args.searchUnits} | display set'
    if args.searchMacs is not None:
        command = f'show ethernet-switching table | match {args.searchMacs}'
    #custom holds a list of at least 1 command
    if args.custom is not None:
        #Turns each custom argument into a command in the list
        command = [c for c in args.custom]

    #creates the pssh client based off the host file and enables logging.
    hosts = getHosts(args.hostFile)
    enable_host_logger()
    creds = getCredentials()
    universal_parameters = {'user': creds[0], 'password':creds[1], 'timeout': 120, 'num_retries': 0}
    client = ParallelSSHClient(hosts, **universal_parameters) if args.proxy is None else ParallelSSHClient(hosts, **universal_parameters, proxy_host=args.proxy[0], proxy_user=args.proxy[1], proxy_pkey=args.proxy[2])


    #runs the formatted command(s) on all servers
    if type(command) is list:
        print("Please wait while the commands are run on all hosts...")
        for c in command:
            safe_run_command(client, c)
            #client.run_command(c)
            #this will wait for all of the threads to finish, and consume_output prints the log
            #client.join(consume_output=True)
    else:
        safe_run_command(client, command)
        #client.run_command(command)
        #this will wait for all of the threads to finish, and consume_output prints the log
        #client.join(consume_output=True)

def safe_run_command(client, command: str):
    output = client.run_command(command, read_timeout=10, stop_on_errors=False)
    for host_out in output:
        host = host_out.host
        print(f"=====================\nHost: {host}, ExitCode: {host_out.exit_code}, Exception: {host_out.exception}\n=====================")
        try:
            for line in host_out.stdout:
                print(line)
            for line in host_out.stderr:
                pass
                #print(line)
        except Timeout:
            print(f"TIMEOUT WHILE READING: {host_out}")
        except TypeError:
            print("No data due to exception")
        print("\n\n\n")

#Host file path should be first argument (argv[0] is python file name)
def getHosts(hostsFilePath):
    hostFile = open(hostsFilePath)
    hosts = hostFile.read().splitlines()
    hostFile.close()
    return hosts

#Gets path to file then tests if the file is already there. This is a global variable for several functions
relativeCredentialPath = '.psshToSwitchesCredentials/credentials.json'
absoluteScriptPath = os.path.dirname(__file__)
credentialPath = os.path.join(absoluteScriptPath, relativeCredentialPath)

def getCredentials():
    #if there isn't a credential path, then make one and prompt them for credentials
    if not os.path.isfile(credentialPath):
        print('No credentials detected. Please provide them using the addCrential command instead of the runInstruction command.')
        quit()

    #read credentials from file. json should just return a dictionary: {user1: pass1, user2: pass2}
    creds = None
    with open(credentialPath) as credFile:
        creds = json.load(credFile)
    if creds is None:
        print("Credentials file exists, but is empty. Please delete credential file at: .psshToSwitchesCredentials/credentials.json")
        quit()

    #if multiple credentials then choose, if not then default to only one.
    username = list(creds.keys())[0]
    if len(creds) > 1:
        print("Please choose which credential you would like to use by typing its login name here.")
        keys = list(creds.keys())
        selection = None
        while True:
            selection = input("Please choose one of the following: {}".format(keys))
            if selection in keys:
                break
        #at this point selection should be the username of one of the credentials' username (such as smartnoc)       
        username = selection
    #set password based on username regardless of how many credentials there are
    password = creds.get(username)
    return [username, password]

def addCredentials(additionalCreds):
    #if there isn't a credential path make one.
    if not os.path.isfile(credentialPath):
        try:
            print("Creating credential file")
            os.mkdir('.psshToSwitchesCredentials')
        except:
            print("Failed to create credential file. Please delete previous file and try again.")
            pass

    with open(credentialPath, 'w+') as credFile:
        initialCreds = json.load(credFile)
        combinedCreds = initialCreds | additionalCreds
        credFile.write(json.dumps(combinedCreds))
    print("Credntials added successfully.")

if __name__ == '__main__':
    args = parse_command_line()

    #The selected command is addCredential
    if('credentials' in dir(args)):
        #If they did not provide credentials:
        if args.credentials is None:
            print("Please provide credentials with the --credentials flag.")
            quit()
        else:
            #If they did, then add them.
            addCredentials(args.credentials)
            quit()
    #The selected command is runInstruction
    elif('hostFile' in dir(args)):
        runInstruction(args)
    else:
        print("Please either select addCredential or runInstruction as a sub-command.")