<%@ Language=VBScript CODEPAGE=936%>
<% Option Explicit %>
<%
'������������������������������������
'��                                                                  ��
'��                eWebEditor - eWebSoft���߱༭��                   ��
'��                                                                  ��
'��  ��Ȩ����: eWebSoft.com                                          ��
'��                                                                  ��
'��  ��������: eWeb�����Ŷ�                                          ��
'��            email:webmaster@webasp.net                            ��
'��            QQ:589808                                             ��
'��                                                                  ��
'��  �����ַ: [��Ʒ����]http://www.eWebSoft.com/Product/eWebEditor/ ��
'��            [֧����̳]http://bbs.eWebSoft.com/                    ��
'��                                                                  ��
'��  ��ҳ��ַ: http://www.eWebSoft.com/   eWebSoft�ŶӼ���Ʒ         ��
'��            http://www.webasp.net/     WEB������Ӧ����Դ��վ      ��
'��            http://bbs.webasp.net/     WEB����������̳            ��
'��                                                                  ��
'������������������������������������
%>

<%

' ����������ʽ�༭���ýӿ��ļ�
' �������
'	style	: ��ʽ��
'	form	: Ҫ���ػ�����ֵ�ı�form��
'	field	: Ҫ���ػ�����ֵ�ı���textarea��


Dim sStyleName, sFormName, sFieldName
sStyleName = Trim(Request("style"))
sFormName = Trim(Request("form"))
sFieldName = Trim(Request("field"))

If sStyleName = "" Then sStyleName = "s_popup"
%>

<html>
<head>
<title>eWebEditor - eWebSoft���߱༭��</title>
<meta http-equiv="Content-Type" content="text/html; charset=gb2312">
<style>
body,td,input,textarea {font-size:9pt}
</style>
<script language=javascript>
var objField=opener.document.<%=sFormName%>.<%=sFieldName%>;

function doSave(){
	objField.value = eWebEditor1.getHTML();
	self.close();
}

function setValue(){
	try{
		if (eWebEditor1.bInitialized){
			eWebEditor1.setHTML(objField.value);
		}else{
			setTimeout("setValue();",1000);
		}
	}
	catch(e){
		setTimeout("setValue();",1000);
	}
}
</script>

</head>
<body>

<FORM method="POST" name="myform">
<INPUT type="hidden" name="content1" value="">
<IFRAME ID="eWebEditor1" src="ewebeditor.asp?id=content1&style=<%=sStyleName%>" frameborder="0" scrolling="no" width="100%" height="100%"></IFRAME>
</FORM>

<script language=javascript>
setTimeout("setValue();",1000);
</script>
</body>
</html>
