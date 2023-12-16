# pssh-switches
This script is meant to allow running commands on several hosts (usually switches) at once. The typical applications of this script are mainly: searching a list of switches for a specific unit number, or searching a list of switches for a specific mac address connection. 

When you can it is typically quicker to search the switches by unit name spreadsheet. But that is not always up to date, and some properties are not listed. Also, this script allows you to search for connected MAC addresses as well as run custom commands on several switches.

The two default commands programmed in are for JunOS switches. But this could be easily circumvented by using the custom script functionality.

# Warning
This script was created to be used in a particular corporate environment. This environment has some instances where it cannot use proper key exchanging protocols. As such, this script was designed to ssh into servers using just a username and password. With little effort this could be changed to use keys.

# HowTo Install
This script requires Python 3.6 or later along with a custom library parallel-ssh. (Note: parallel-ssh is only available on linux, so you will have to run this on WSL) You will install both below (Note: these installation commands are for Ubuntu installations, you will have to install them yourself for other installations):

Check if you have python3 installed by typing this into your terminal

    python3 --version

If you have python3 installed it will print what version you have. If you do not have python3 then install it by typing the following:

	sudo apt install python3

Note you may need to update the apt package manager first by running:

    sudo apt update

Now we will install the parallel-ssh (aka pssh) python package.

First ensure that you have pip installed. If you do not you can install it with: 

	sudo apt-get install python3-pip

Pip is another package manager similar to apt.

Next install parallel-ssh by running: 

    pip install parallel-ssh

Now download the script file: psshToSwitches.py

 . I would recommend placing it within its own folder, as it will have to be in the same directory as any host files, which can clutter your home directory. If you missed it earlier, this script must be run on your Linux machine/VM/WSL.

Note, the first time you run this script, it will prompt you for your credentials.

# HowTo Use/Docs
## Initial Setup
This script is a command-line only tool. It has 3 commands built in: searchUnits, searchMacs, and custom. Along with one additional special command: addCredential which is used for running the script. The instructions on how to use each are below.

The first time you run the script (regardless of which command you choose) you will be prompted to input your credentials. I would not recommend running the addCredential command unless you have multiple sets of credentials you would like to set. 

You will have to ensure your command is a properly structured, valid command. I have an example command below, but see following steps for more of an explanation.

	python3 psshToSwitches.py searchUnits MyHosts.txt 332

The above code will get the IP addresses from a file that you create, in this case MyHosts.txt. And search them all for a unit with a description containing: 332.

The script will only prompt you credentials until you provide one set. It will use this default set without prompting in the future. If you require 2 different logins, for example if you want to use your smartnoc credentials sometimes and your radius credentials other times, you can use the addCredential command (below). This will add a second (or more) set of credentials, and every time you use the program you will be prompted to choose which one you’d like to use.
## Basic Command Structure
To see help page run:
 
	python3 psshServers.py -h
 For more detailed help pages run:

 	python3 psshServers.py runInstruction -h
  	python3 psshServers.py addCredential -h

## Hostfiles
In order to connect to switches you have to have their IP address. The same is true here. Except we need many IP addresses, one for each switch you need to connect to. We basically just make a list of switch IPs and I recommend calling it something like FancyPropertyNameHosts.txt. That way you can look through all of FancyPropertyName at once.

The IPs are delimited (aka separated) with a newline. So your files should be structured like this:

	10.1.1.1
 	10.1.1.2
	10.1.2.1
 	10.2.1.1
There should be no empty lines anywhere in the script. And no form of comments or other information, just include the IP addresses. The file doesn’t have to end in .txt, but it must be plaintext and readable by python.
I have also included an example host file in the project.
