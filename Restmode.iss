; Restmode Inno Setup Script
[Setup]
AppName=Restmode
AppVersion=1.0
AppPublisher=Manish Rathaur
DefaultDirName={autopf}\Restmode
DefaultGroupName=Restmode
UninstallDisplayIcon={app}\icon.ico
OutputDir=dist
OutputBaseFilename=RestmodeSetup
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Restmode.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; Add other files if needed (e.g., config, assets)

[Icons]
Name: "{group}\Restmode Settings"; Filename: "{app}\Restmode.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\Restmode Settings"; Filename: "{app}\Restmode.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\Restmode.exe"; Description: "Launch Restmode"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[UninstallRun]
Filename: "taskkill"; Parameters: "/IM Restmode.exe /F"; StatusMsg: "Closing Restmode if running..." 