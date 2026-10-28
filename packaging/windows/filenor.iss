; Inno Setup betigi.  Derleme:  ISCC /DAppVersion=2.0.0 /Odist packaging\windows\filenor.iss
; Kullanici basina kurulur (yonetici yetkisi gerekmez); uygulama klasoru dist\Filenor\ olmalidir.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6F1E1D4B-3B7A-4C55-9C0E-8F0A2D5F4A11}
AppName=Filenor
AppVersion={#AppVersion}
AppPublisher=MiracLight
AppPublisherURL=https://github.com/MiracLight/filenor
DefaultDirName={autopf}\Filenor
DefaultGroupName=Filenor
UninstallDisplayIcon={app}\Filenor.exe
SetupIconFile=..\..\filenor\simge\filenor.ico
OutputBaseFilename=Filenor-{#AppVersion}-setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
LicenseFile=..\..\LICENSE

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\Filenor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Filenor"; Filename: "{app}\Filenor.exe"
Name: "{autodesktop}\Filenor"; Filename: "{app}\Filenor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Filenor.exe"; Description: "{cm:LaunchProgram,Filenor}"; Flags: nowait postinstall skipifsilent
