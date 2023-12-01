# pssh-switches
This script is meant to allow running commands on several hosts (usually switches) at once. The typical applications of this script are mainly: searching a list of switches for a specific unit number, or searching a list of switches for a specific mac address connection. 

When you can it is typically quicker to search the switches by unit name spreadsheet. But that is not always up to date, and some properties are not listed. Also, this script allows you to search for connected MAC addresses as well as run custom commands on several switches.

The two default commands programmed in are for JunOS switches. But this could be easily circumvented by using the custom script functionality.

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
	
	python3 psshToSwitches.py <command> <hostsfile> [additional arguments]
 All of the pre-supplied commands only take one argument. But there is support for more than one additional argument if someone wants to program their own permanent custom commands in that can take additional arguments.

### List of commands
#### searchUnits: which requires 1 additional argument (the unit number)
This example will search MyHosts for any unit labeled 332: 

	python3 psshToSwitches.py searchUnits MyHosts.txt 332

 Specifically it is running this command: 

 	show configuration interfaces | match {unitNumber}
on every host in parallel. Then it compiles the output into your hell.
#### searchMacs: which requires 1 additional argument (the mac address or just a piece of one)
This example will search MyOtherHosts for any connected MAC addresses that contain f0:29:16: 

	python3 psshToSwitches.py searchMacs MyOtherHosts.txt f0:29:16
Specifically it is running this command:
	
 	show ethernet-switching table | match {macAddress}
on every host in parallel. Then it compiles the output into your shell.
#### custom: which requires 1 additional argument (the custom command to run)
This example will run the provided command (whats in the 'quotes') on all of the MyHosts.

	python3 psshToSwitches.py custom MyHosts.txt 'show class-of-service interface | match 684'
This command in particular searches all of the class of services for any index that matches 684.
As you can see, with the custom command, you can use this tool to do just about anything you can think of, in parallel on as many switches as you’d like.

#### addCredential: which requires no additional arguments (**it also does not require a hostfile**)
Example Usage:

	python3 psshToSwitches.py addCredential
It will then prompt you to input another username and password. In the future, when you use the program with multiple credentials, you will be prompted upon loading to determine which user you would like to use.
## Interpreting Output
This is the output from the example of how to use the custom command above. You can see the output from the custom command to the far right of each line. The part where it says Pyshical interface: ge-0/0/3x, Index: 684. The part to the left of that, is what the script prints. This allows you to see which switch the result was found on. For example, if we wanted to find the interface ge-0/0/39, Index: 684 we know that is on the switch with the ip: 1.1.1.1. This allows us to ssh directly into that switch if we wanted to perform any maintenance or troubleshooting on that port.
### Somtimes you will run into an output that doesn't make much sense.
This is a typical searchUnit output, it is rather easy to read: 

This tells us that unit 332 is found on the switch 10.1.1.6.

But lets say you wanted to look for unit 100 so you run: ... searchUnits MyHosts.txt 100. You might expect to get a similar output, when in reality you get: 

This is because the search command is not perfect, remember it just runs show configuration interfaces | match {number}. In this case that is also picking up all the of RLIMIT100's because it contains 100. A better way to search for unit 100 would be to run: ... searchUnits MyHosts.txt Unit_100.

## Hostfiles
In order to connect to switches you have to have their IP address. The same is true here. Except we need many IP addresses, one for each switch you need to connect to. We basically just make a list of switch IPs and I recommend calling it something like FancyPropertyNameHosts.txt. That way you can look through all of FancyPropertyName at once.

The IPs are delimited (aka separated) with a newline. So your files should be structured like this:

	10.1.1.1
 	10.1.1.2
	10.1.2.1
 	10.2.1.1
There should be no empty lines anywhere in the script. And no form of comments or other information, just include the IP addresses. The file doesn’t have to end in .txt, but it must be plaintext and readable by python.
I have also included an example host file in the project.
