# $language = "python"
# $interface = "1.0"

# PasteWithEchoFlowControl.py
#
# Description:
#   Demonstrates how to send a block of lines from the clipboard and
#   wait for those lines to be echoed back by the remote host before the next
#   block of lines is sent. This is one approach to prevent overwhelming a
#   remote host that cannot accept data as fast as SecureCRT normally sends it
#   by making sure the remote machine has received each block of lines before
#   moving on with the next block.

import SecureCRT
import time

crt.Screen.Synchronous = True
crt.Screen.IgnoreEscape = True

def main():
    # If there isn't an active connection, there's no point in continuing
    # since we can't send data.
    if not crt.Session.Connected:
        crt.Dialog.MessageBox("Sending data requires an active connection.")
        return
    
    # If there isn't anything in the clipboard, it doesn't make any
    # sense to continue with the script.
    if crt.Clipboard.Text.strip() == "":
        crt.Dialog.MessageBox("No text found in the clipboard.")
        return


    # check if we are in configure terminal
	crt.Screen.Send("\r\n\r\n")
	if not crt.Screen.WaitForString(")#", 1):

	#--- remote fails to echo the line back to us within 3 seconds.
	#`ElseIf Not crt.Screen.WaitForString(strLine, 3) Then
		crt.Dialog.MessageBox("I don't think you're in global config mode\r\n\r\nAbandoning paste operation.")
		return




    
    
    # Keep timing information so that we can display how long it took for the
    # data to be sent to the remote (each line sent only after the prior line
    # was echo'd back to SecureCRT, as a flow control mechanism).
    nStartTime = time.time()

    # Multiple lines in the clipboard are typically stored with a CRLF
    # separator, but this script example tries to accommodate other line endings
    # that might be supported by some editors. Break up lines into an array
    # (each line as an element within the array).
    if crt.Clipboard.Text.find("\r\n") > -1:
        vLines = crt.Clipboard.Text.split("\r\n")
    elif crt.Clipboard.Text.find("\n") > -1:
        vLines = crt.Clipboard.Text.split("\n")
    else:
        vLines = crt.Clipboard.Text.split("\r")
    
    #--- Count lines
    numLineNumber = 0
    for strLine in vLines:
        numLineNumber = numLineNumber + 1

    # ask if we're ready to roll
	strTitle = "Good to go?"
    strMsg = "Looks like we've got " + str(numLineNumber) + " lines in the clipboard. Start paste operation?"
    result = crt.Dialog.MessageBox(strMsg, strTitle, ICON_QUESTION | BUTTON_YESNO | DEFBUTTON2 )
    if result == IDNO:
        return

    
    nLineNumber = 0
    for strLine in vLines:
        # Send the next line to the remote
        crt.Screen.Send(strLine + "\r")
        
        bSuccess = False
        # If the current line isn't empty, wait for it to be echo'd back to us
        if not strLine == "":
            # Wait for the remote to echo the line back to SecureCRT; bail if
            # the remote fails to echo the line back to us within 3 seconds.
            bSuccess = crt.Screen.WaitForString(")#", 3)
        else:
            crt.Session.SetStatusText(
                "Sent a blank line; waiting for cursor to move...")
            bSuccess = crt.Screen.WaitForCursor(3)
            crt.Session.SetStatusText("")
        
        if not bSuccess:
            # ask if we want to continue
            strTitle = "Continue?"
            result = crt.Dialog.MessageBox("Sent %d lines, but the most recent line sent " % (nLineNumber + 1) +
                "was not echoed back to SecureCRT within 3 seconds.\r\n\r\n" +
                "Continue?", strTitle, ICON_QUESTION | BUTTON_YESNO | DEFBUTTON2 )
            if result == IDNO:
                return

            crt.Dialog.MessageBox(
                "Sent %d lines, but the most recent line sent " % (nLineNumber + 1) +
                "was not echoed back to SecureCRT within 3 seconds.\r\n\r\n" +
                "Abandoning paste operation.")
            return

        nLineNumber += 1
    
    # Calculate seconds elapsed
    nTimeElapsed = time.time() - nStartTime
    
    # Inform that the data has all been sent.
    crt.Dialog.MessageBox(
        "%d lines from the clipboard have been sent.\r\n\r\n" % (nLineNumber) + 
        "Time elapsed: %2.3f seconds." % (nTimeElapsed))

main()
