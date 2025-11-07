; T-Arabic Installer Script
[Setup]
AppName=T-Arabic
AppVersion=1.0
DefaultDirName={autopf}\T-Arabic
DefaultGroupName=T-Arabic
OutputBaseFilename=T-Arabic-Setup
OutputDir=Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\T-Arabic.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\T-Arabic"; Filename: "{app}\T-Arabic.exe"
Name: "{commondesktop}\T-Arabic"; Filename: "{app}\T-Arabic.exe"
