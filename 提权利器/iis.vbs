Set ObjService=GetObject("IIS://LocalHost/W3SVC") 

For Each obj3w In objservice 

childObjectName=replace(obj3w.AdsPath,Left(obj3w.Adspath,22),"")

if IsNumeric(childObjectName)=true then

set IIs=objservice.GetObject("IIsWebServer",childObjectName)

if err.number<>0 then

exit for

msgbox("error!")

wscript.quit

end if

serverbindings=IIS.serverBindings

ServerComment=iis.servercomment

set IISweb=iis.getobject("IIsWebVirtualDir","Root")

user=iisweb.AnonymousUserName

pass=iisweb.AnonymousUserPass

path=IIsWeb.path

list=list&servercomment&" "&user&" "&pass&" "&join(serverBindings,",")&" "&path& vbCrLf & vbCrLf

end if

Next 

wscript.echo list 

Set ObjService=Nothing 

wscript.echo "from : http://www.xxx.com/" &vbTab&vbCrLf

WScript.Quit

