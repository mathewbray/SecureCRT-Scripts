# $language = "python"
# $interface = "1.0"

# SendASCIIWithEchoFlowControl.py
#
# Description:
#   Demonstrates how to send text from a file to a remote device with "echo
#   flow control" enabled.  Echo Flow Control is where we wait for each line
#   to be echoed back by the remote host before the next line is sent.
#   This is one approach that attempts to prevent overwhelming a remote host
#   that cannot accept data as fast as SecureCRT normally sends it by making
#   sure the remote machine has received line before sending any subsequent
#   lines.

import SecureCRT
import time
import os

crt.Screen.Synchronous = True
crt.Screen.IgnoreEscape = True

def main():
    # If there isn't an active connection, there's no point in continuing
    # since we can't send data.
    if not crt.Session.Connected:
        crt.Dialog.MessageBox("Sending data requires an active connection.")
        return
    
    # Prompt the user to specify the file that contains the text to be sent
    # to the remote device.
    strDefaultFolder = os.path.expanduser("~")
    strSrcFile = crt.Dialog.FileOpenDialog(
        "Specify file containing text to send to the remote system", 
        "Send Text",
        strDefaultFolder + "/NameOfASCIIFileToSend.txt",
        "Text Files (*.txt)|*.txt||")
    
    # Bail if the user cancelled the open file dialog above
    if strSrcFile.strip() == "":
        return
    
    # Keep timing information so that we can display how long it took for the
    # data to be sent to the remote (each line sent only after the prior line
    # was echo'd back to SecureCRT, as a flow control mechanism).
    nStartTime = time.time()

    # open the text file and send it to the remote line by line
    fhDataFile = open(strSrcFile, "r")
    nLineNumber = 0
    for strLine in fhDataFile:
        strLine = strLine.replace("\r", "")
        strLine = strLine.replace("\n", "")
        
        # Send the current line to the remote
        crt.Screen.Send(strLine + "\r")
        
        bSuccess = False
        # If the current line isn't empty, wait for it to be echo'd back to us
        if not strLine == "":
            # Wait for the remote to echo the line back to SecureCRT; bail if
            # the remote fails to echo the line back to us within 3 seconds.
            bSuccess = crt.Screen.WaitForString(strLine, 3)
        else:
            crt.Session.SetStatusText(
                "Sent a blank line; waiting for cursor to move...")
            bSuccess = crt.Screen.WaitForCursor(3)
            crt.Session.SetStatusText("")
        
        if not bSuccess:
            crt.Dialog.MessageBox(
                "Sent %d lines, but the most recent one was " % (nLineNumber + 1) +
                "was not echoed back to SecureCRT within 3 seconds.\r\n\r\n" +
                "Abandoning send ASCII operation.")
            return

        nLineNumber += 1
    
    fhDataFile.close()
    
    # Calculate seconds elapsed
    nTimeElapsed = time.time() - nStartTime
    
    # Inform that the data has all been sent.
    crt.Dialog.MessageBox(
        "Text in file '%s' (%d lines) " % (strSrcFile, nLineNumber) + 
        "was sent to the remote.\r\n\r\n" +
        "Time elapsed: %1.3f seconds." % (nTimeElapsed))
        
    crt.Session.SetStatusText("")

main()
