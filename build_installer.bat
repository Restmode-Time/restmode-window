@echo off
REM Batch file to build RestmodeSetup.exe using Inno Setup
REM Update the path below if your Inno Setup is installed elsewhere
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
%INNO_PATH% Restmode.iss
pause 