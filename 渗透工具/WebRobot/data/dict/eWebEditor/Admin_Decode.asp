<!--#include file = "Include/Startup.asp"-->
<!--#include file = "admin_private.asp"-->
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

sPosition = sPosition & "��ȡ���ͺ�������"

Call Header()
Call Content()
Call Footer()


Sub Content()
	%>
	
	<Script Language=JavaScript>
	function MakeCode(){
		var b = false;
		var str = "<!--#" + "include file = \"....../eWebEditor/Include/DeCode.asp\"-->\n\n\n<" + "%\n\n";
		str += "Response.Write eWebEditor_DeCode(sContent, \"";
		for (var i=0;i<document.all("filterItem").length;i++){
			if (document.all("filterItem")[i].checked){
				if (b) str += ", ";
				str += document.all("filterItem")[i].value.toUpperCase();
				b = true;
			}
		}
		str += "\")\n\n%" + ">";
		okcode.value = str;
	}
	</Script>

	<p class=highlight2>������͹��ܣ�Ŀ����Ϊ�˷�ֹһЩ�˶�����ύһЩ���룬Ӱ��ϵͳ�İ�ȫʹ�ã�ͨ���ַ�ת���ķ�������ֹ��������ķ��������µ����ļ���·���������ʵ�ʵİ�װ���и��ġ�����Ҫ���õĵط����ȵð���deCode.asp�ļ����������£�</p>
	<textarea rows=3 cols=65 style='width:100%'>&lt;!--#include file = &quot;....../eWebEditor/Include/DeCode.asp&quot;--&gt;</textarea>
	<p class=highlight2>����ѡ����Ҫ�Ľ��͵Ķ���Ҳ���ǲ������û�ʹ�õĶ���Ȼ�������ɼ��ɡ�</p>
	<table border=1 cellpadding=3 cellspacing=0 width="100%">
	<tr>
		<td><input type="checkbox" name="filterItem" value="script" checked> �ű�����(<span class=highlight1>SCRIPT</span>)����������ʹ��javascript,vbscript�ȣ��¼�onclick,ondlbclick��</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="object"> �������(<span class=highlight1>OBJECT</span>)���������� object, param, embed ��ǩ������Ƕ�����</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="table"> ������(<span class=highlight1>TABLE</span>)����������ʹ��table,th,td,tr��ǩ</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="class"> ��ʽ�����(<span class=highlight1>CLASS</span>)����������ʹ�� class= �����ı�ǩ</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="style"> ��ʽ����(<span class=highlight1>STYLE</span>)����������ʹ�� style= �����ı�ǩ</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="xml"> XML����(<span class=highlight1>XML</span>)����������ʹ�� xml ��ǩ</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="namespace"> �����ռ����(<span class=highlight1>NAMESPACE</span>)����������ʹ�� &lt;o:p&gt;&lt;/o:p&gt; ���ָ�ʽ</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="font"> �������(<span class=highlight1>FONT</span>)����������ʹ�� font ��ǩ��������ʹ��</td>
	</tr>
	<tr>
		<td><input type="checkbox" name="filterItem" value="marquee"> ��Ļ����(<span class=highlight1>MARQUEE</span>)����������ʹ�� marquee ��ǩ��Ҳ��û���ƶ�����������</td>
	</tr>
	<tr>
		<td><input type=button name=b value=" ���ɴ��� " onclick="MakeCode()"></td>
	</tr>
	</table>
	
	<p class=highlight2>���ɵĴ��루��Ҫ���õĴ��룩���£�</p>
	<textarea id=okcode rows=10 cols=65 style='width:100%'></textarea><br><br>
	
	<Script Language=JavaScript>MakeCode();</Script>


	<%
End Sub
%>