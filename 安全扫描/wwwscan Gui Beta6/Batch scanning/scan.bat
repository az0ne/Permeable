@echo off
color 0a
rem MODE CON COLS=80 LINES=36
cls
echo �X------------------------------------�[
echo ��
echo ��           Just_Fun_Fun!
echo ��
echo �^------------------------------------�a
for /f %%a in (url.txt) do wwwscan %%a -m 20