# $language = "VBScript"
# $interface = "1.0"

crt.Screen.Synchronous = True
crt.Screen.IgnoreEscape = True

Sub Main()
    '--- check for active session
    If Not crt.Session.Connected Then
        crt.Dialog.MessageBox "Sending data requires an active connection."
        Exit Sub
    End If

    '--- check for anything in clipboard
    If Trim(crt.Clipboard.Text) = "" Then
        crt.Dialog.MessageBox "No text found in the Windows Clipboard."
        Exit Sub
    End If
	

	'--- check if we are in configure terminal
    strGoodToGO = "Testing"
    Do While strGoodToGO = "Testing"
	crt.Screen.Send vbcr
        If Not crt.Screen.WaitForString(")#", 1) Then

            strTitle = "Error"
            strMsg = "I don't think you're in global config mode." & vbcrlf & _
            vbcrlf & _
            "Send 'enable' and 'conf t'?"
            ' Set the buttons as Yes and No, with the default button to the second button ("No", in this example) 
            nButtons = vbYesNo + vbDefaultButton2
            ' Set the icon to a question mark
            nIcon = vbQuestion
            ' Display the dialog and set the return value of our function accordingly
            If MsgBox(strMsg, nButtons + nIcon, strTitle) = vbYes Then
	            crt.Screen.Send vbcr
                crt.Sleep 100                
                crt.Screen.Send "enable"
	            crt.Screen.Send vbcr                
                crt.Sleep 50
                crt.Screen.Send "configure terminal"
	            crt.Screen.Send vbcr                
                crt.Sleep 50
            Else
                Exit Sub
            End If
        Else
            strGoodToGO = "Good"
        End If	
    Loop

	

    '--- start timer to display when finished
    nStartTime = Timer

    '--- Multiple lines in the Windows Clipboard are typically stored with a CRLF
    '--- separator, but this script example tries to accommodate other line endings
    '--- that might be supported by some editors. Break up lines into an array
    '--- (each line as an element within the array).
    If Instr(crt.Clipboard.Text, vbcrlf) > 0 Then
        vLines = Split(crt.Clipboard.Text, vbcrlf)
    ElseIf Instr(crt.Clipboard.Text, vblf) > 0 Then
        vLines = Split(crt.Clipboard.Text, vblf)
    Else
        vLines = Split(crt.Clipboard.Text, vbcr)
    End If
	
	'--- Count lines
	numLineNumber = 0
	For Each strLine In vLines
		numLineNumber = numLineNumber + 1
	Next
	
	
	' ask if we are good to go for paste operation
	strTitle = "Good to go?"
	strMsg = "Looks like we've got " & numLineNumber & " lines with " & Len(crt.Clipboard.Text) & " characters in the clipboard."  & vbcrlf & _
					vbcrlf & _ 
                    "Start paste operation?"
	' Set the buttons as Yes and No, with the default button to the second button ("No", in this example) 
	nButtons = vbYesNo + vbDefaultButton2
    ' Set the icon to a question mark
	nIcon = vbQuestion
	' Display the dialog and set the return value of our function accordingly
	If MsgBox(strMsg, nButtons + nIcon, strTitle) = vbYes Then
		
	Else
		Exit Sub
	End If

    nLineNumber = 0
    For Each strLine In vLines
        '--- Send the next line to the remote
        crt.Screen.Send strLine & vbcr
		crt.Sleep 50
	
			'--- Check for )# or the line, If not found then check for the whole line
			nResult = crt.Screen.WaitForStrings(")#", strLine, 25)
			'nResult = crt.Screen.WaitForStrings(strLine, 25)
			
            If  nResult = 0 Then

                ' ask if we are good to go for paste operation
                strTitle = "No echo received."
                strMsg = "Sent " & nLineNumber + 1 & " lines, but the last one was " & _
					"not echoed back to SecureCRT." & vbcrlf & _
					vbcrlf & _
					"Continue?"
                ' Set the buttons as Yes and No, with the default button to the second button ("No", in this example) 
                nButtons = vbYesNo + vbDefaultButton2
                ' Set the icon to a question mark
                nIcon = vbQuestion
                ' Display the dialog and set the return value of our function accordingly
                If MsgBox(strMsg, nButtons + nIcon, strTitle) = vbYes Then
                Else
                    Exit Sub
                End If
			End If

        nLineNumber = nLineNumber + 1
    Next

    ' Inform that the data has all been sent.
    crt.Dialog.MessageBox _
        nLineNumber & " lines from the clipboard have been sent." & _
        vbcrlf & vbcrlf & _
        "Time elapsed: " & GetMinutesAndSeconds(Timer - nStartTime)
End Sub

'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Function GetMinutesAndSeconds(nTotalSecondsElapsed)
    Dim nMinutes, nSeconds, nMSeconds
    Dim nMinutesElapsed, nSecondsValue, nSecondsElapsed

    If nTotalSecondsElapsed = 0 Then
        GetMinutesAndSeconds = "less than a millisecond."
        Exit Function
    End If

    ' convert seconds into a fractional minutes value
    nMinutesElapsed = nTotalSecondsElapsed / 60

    ' convert the decimal portion into the number of remaining seconds
    nSecondsValue = nMinutesElapsed - Fix(nMinutesElapsed)
    nSecondsElapsed = Fix(nSecondsValue * 60)

    ' Remove the decimal from the minutes value
    nMinutesElapsed = Fix(nMinutesElapsed)

    ' Get the number of Milliseconds, Seconds, and Minutes to return to the
    ' caller byref
    nMSeconds = fix(1000 * (nTotalSecondsElapsed - Fix(nTotalSecondsElapsed)))
    nSeconds = nSecondsElapsed
    nMinutes = nMinutesElapsed

    ' Form the final string to be returned
    GetMinutesAndSeconds = nMinutesElapsed & " minutes, " & _
        nSecondsElapsed & " seconds, and " & _
        nMSeconds & " ms"
End Function