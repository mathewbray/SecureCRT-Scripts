#$language = "Python"
#$interface = "1.0"

# ConnectToMultipleSessionsAndSendCommands.py
#
# Description:
#	 Reads in sessions from a file (one session per line) and
#	 connects to each one (one at a time) and sends a series of
#	 commands to the remote, then disconnects from the session
#	 and moves on to the next session.
#	 
#	 By default, the file containing the sessions is expected to be named
#	 "SessionList.txt", and should be located in the current user's home
#	 directory.  Each line of the file is expected to contain the
#	 path to the session as it appears within the Connect dialog (excluding
#	 the leading "Sessions/" component.  Here is an example file contents:
#		 
#		 redhat
#		 redhat8
#		 192.168.0.123
#		 192.168.0.131
#		 Redhat Sessions\RedHat - XTerm
#
#	 For the sake of simplicity, this example assumes that all
#	 sessions we're connecting to are using the SSH1 and SSH2
#	 protocols, with usernames and passwords saved encrypted
#	 as part of the session configuration so that we don't need
#	 to worry about authentication within this script.
#	 The global option "Show connection closed dialog" should be off.

import os
import codecs
import subprocess

LOG_DIRECTORY = os.path.join(os.path.expanduser('~'), 'LogOutputOfSpecificCommand')

LOG_FILE_TEMPLATE = os.path.join(LOG_DIRECTORY, "Command_%(NUM)s_Results.txt")

#SCRIPT_TAB = crt.GetScriptTab()

COMMANDS = [
	"show version | i ptime",
	"show inventory",
	"show running-config",
	#"tail -100 /var/log/messages",
#	"sh run",
#	"",
#	"",
	]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def Main():
	errorMessages = ""

	if not os.path.exists(LOG_DIRECTORY):
		os.mkdir(LOG_DIRECTORY)

	if not os.path.isdir(LOG_DIRECTORY):
		crt.Dialog.MessageBox(
			"Log output directory %r is not a directory" % LOG_DIRECTORY)
		return

	# if not SCRIPT_TAB.Session.Connected:
	# 	crt.Dialog.MessageBox(
	# 		"Not Connected.  Please connect before running this script.")
	# 	return

	sessionsFileName = os.path.expanduser("~") + "/Desktop/SessionList.txt"
	if not os.path.exists(sessionsFileName):
		crt.Dialog.MessageBox(
			"Session list file not found:\n\n" +
			sessionsFileName + "\n\n" +
			"Create a session list file as described in the description of " +
			"this script code and then run the script again.")
		return

	sessionFile = codecs.open(sessionsFileName, "r", "utf-8")
	sessionsArray = []

	for line in sessionFile:
		session = line.strip()
		if session:	# Don't add empty lines/sessions
			sessionsArray.append(session)

	sessionFile.close()

	# Connect to each session and issue a few commands, then disconnect.
	for session in sessionsArray:
		#crt.Dialog.MessageBox("Connecting to Session: " + session)

		try:
			#crt.Session.Connect("/S \"" + session + "\"")
			crt.Session.Connect("/SSH2 /ACCEPTHOSTKEYS /AUTH keyboard-interactive \"" + session + "\"")
		except ScriptError:
			error = crt.GetLastErrorMessage()

		# If we successfully connected, we'll do the work we intend to do...
		# otherwise, we'll skip the work and move on to the next session in 
		# the list.
		if crt.Session.Connected:
			crt.Screen.Synchronous = True

			# When we first connect, there will likely be data arriving from the
			# remote system.  This is one way of detecting when it's safe to
			# start sending data.
			while True:				
				if not crt.Screen.WaitForCursor(1):
					break
			# Once the cursor has stopped moving for about a second, we'll
			# assume it's safe to start interacting with the remote system.

			# Get the shell prompt so that we can know what to look for when
			# determining if the command is completed. Won't work if the prompt
			# is dynamic (e.g. changes according to current working folder, etc)
			row = crt.Screen.CurrentRow
			prompt = crt.Screen.Get(row, 0, row, crt.Screen.CurrentColumn - 1)
			prompt = prompt.strip()

			
			for (index, command) in enumerate(COMMANDS):
				command = command.strip()

				# Set up the log file for this specific command
				logFileName = LOG_FILE_TEMPLATE % {"NUM" : NN(index + 1, 2)}
				
				# Send the command text to the remote
				crt.Screen.Send(command + '\r')

				# Wait for the command to be echoed back to us.
				crt.Screen.WaitForString('\r', 1)
				crt.Screen.WaitForString('\n', 1)

				# Use the ReadString() method to get the text displayed while
				# the command was running.  Note also that the ReadString()
				# method captures escape sequences sent from the remote machine
				# as well as displayed text.  As mentioned earlier in comments
				# above, if you want to suppress escape sequences from being
				# captured, set the Screen.IgnoreEscape property = True.
				result = crt.Screen.ReadString(prompt)
				result = result.strip()
				
				filep = codecs.open(logFileName, 'wb+', "utf-8")

				# If you don't want the command logged along with the results, comment
				# out the very next line
				filep.write("Results of command: " + command + os.linesep)

				# Write out the results of the command to our log file
				filep.write(result + os.linesep)
				
				# Close the log file
				filep.close()

			# Once we're complete, let's bring up the directory containing the
			# log files.
			LaunchViewer(LOG_DIRECTORY)


			#crt.Screen.Send("show version\n")
			# Wait for the command to complete, by looking for the prompt to
			# appear once again.
			#crt.Screen.WaitForString(prompt)

			#crt.Screen.Send("pwd\n")
			# Wait for the command to complete, by looking for the prompt to
			# appear once again.
			#crt.Screen.WaitForString(prompt)

			#crt.Screen.Send("who\n")
			# Wait for the command to complete, by looking for the prompt to
			# appear once again.
			#crt.Screen.WaitForString(prompt)

			# Now disconnect from the remote machine...
			crt.Session.Disconnect()
			# Wait for the connection to close
			while crt.Session.Connected == True:
				crt.Sleep(100)

			crt.Sleep(1000)
		else:
			errorMessages = errorMessages + "\n" + "*** Error connecting to " + session + ": " + error

	if errorMessages == "":
		crt.Dialog.MessageBox("Tasks completed.  No Errors were detected.")
	else:
		crt.Dialog.MessageBox("Tasks completed.  The following errors occurred:\n" + errorMessages)

	#crt.Quit()
	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def LaunchViewer(filename):
	try:
		os.startfile(filename)
	except AttributeError:
		subprocess.call(['open', filename])


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def NN(number, digitCount):
	# Normalizes a single digit number to have digitCount 0s in front of it
	format = "%0" + str(digitCount) + "d"
	return format % number 

Main()
