Dim rs, ws, fso, conn, stream, connStr, theFolder
Set rs = CreateObject("ADODB.RecordSet")
Set stream = CreateObject("ADODB.Stream")
Set conn = CreateObject("ADODB.Connection")
Set fso = CreateObject("Scripting.FileSystemObject")
dbname=inputbox("���������ݿ�����,���ݿ����ͱ�������ͬһĿ¼","��ʾby XiaoC[81sec.com]")
connStr = "Provider=Microsoft.Jet.OLEDB.4.0;Data Source="&dbname&";"

conn.Open connStr
rs.Open "select * from [filedata]", conn, 1, 1
stream.Open
stream.Type = 1

On Error Resume Next

Do Until rs.Eof
theFolder = Left(rs("path"), InStrRev(rs("path"), "\"))
If fso.FolderExists(theFolder) = False Then
createFolder(theFolder)
End If
stream.SetEos()
stream.Write rs("file")
stream.SaveToFile str & rs("path"), 2
rs.MoveNext
Loop

rs.Close
conn.Close
stream.Close
Set ws = Nothing
Set rs = Nothing
Set stream = Nothing
Set conn = Nothing

Wscript.Echo "������ļ��Ѿ���ѹ��ɣ�"

Sub createFolder(path)
Dim i
i = Instr(path, "\")
Do While i > 0
If fso.FolderExists(Left(path, i)) = False Then
fso.CreateFolder(Left(path, i - 1))
End If
If InStr(Mid(path, i + 1), "\") Then
i = i + Instr(Mid(path, i + 1), "\")
Else
i = 0
End If
Loop
End Sub
