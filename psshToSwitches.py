#Script usage. Run script with python3. 1st argument should be what kind of command you want to run. 2nd argument should be hosts file name delimmited by \n and in the same directory as script. Options are listed in command options below. Any addtional arguments will be inserted into commands
#searchUnits requires 1 argument: the unitNumber. searchMacs requires 1 argument: the macAddress. custom requires 1 argument: the command. (Be sure to format command in a string: 'this is my command here | asdf | grep'
#Example Usage: $python3 searchSwitches.py MidtownHosts.txt searchUnits 445



from pssh.clients import ParallelSSHClient
from pssh.utils import enable_host_logger
import sys
import os
import json

def main():
    #Choose which command to run
    givenCommand = sys.argv[1]
    additionalArguments = sys.argv[3:]

    commandOptions = {'searchUnits': 'show configuration interfaces | match {}',
                      'searchMacs': 'show ethernet-switching table | match {}',
                      'custom': '{}',
                      'addCredential':''}
    selectedCommandName = getCommandFromInput(givenCommand, list(commandOptions.keys()))

    #this gets the command based off the chosen name
    selectedCommand = commandOptions.get(selectedCommandName)
    #if the special addCredential command is chosen, then run this method. Note this will end the program early and not return here.
    if selectedCommandName == 'addCredential':
        addCredential()
    #this formats the commands by inserting any extra command line arguments from the shell into the command. (For custom commands this adds the entire command)
    formattedCommand = selectedCommand.format(*additionalArguments)



    #creates the pssh client based off the host file and enables logging.
    hosts = getHosts(sys.argv[2])
    enable_host_logger()
    creds = getCredentials()
    client = ParallelSSHClient(hosts, user=creds[0], password=creds[1])



    #runs the formatted command on all servers
    print("Please wait while command is run on all hosts...")
    client.run_command(formattedCommand)
    #this will wait for all of the threads to finish, and consume_output prints the log
    client.join(consume_output=True)

#checks user input and compares it to a list of potential commands
def getCommandFromInput(commandSelector, potentialCommands):
    while(True):
        for potentialCommand in potentialCommands:
            if commandSelector == potentialCommand:
                return potentialCommand
        #If the code executes this far it means that the command given isn't in the list. So print off the options and check again
        print("The given command is not an option. Please select one of the follow commands:")
        print(potentialCommands)
        commandSelector = input()

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
        login = promptCredentialInput()
        try:
            os.mkdir('.psshToSwitchesCredentials')
        except:
            pass
        with open(credentialPath, 'w') as credFile:
            credFile.write(json.dumps(login))

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

def promptCredentialInput():
    userName = input("Please type your ssh username (will likely be smartnoc):")
    password = input("Please type your ssh password (will likely be smartnoc password):")
    print("Credentials recorded. If you made any errors please navigate to .psshToSwitchesCredentials/credentials.json to either edit the credentials in the file, or delete the file to reset this prompt")
    print("You can also add additional credentials by using the 'addCredential' subcommand.")
    return {userName: password}

def addCredential():
    additionalCreds = promptCredentialInput()
    with open(credentialPath, 'w+') as credFile:
        initialCreds = json.load(credFile)
        combinedCreds = initialCreds | additionalCreds
        credFile.write(json.dumps(combinedCreds))
    quit()

if __name__ == '__main__':
    main()
