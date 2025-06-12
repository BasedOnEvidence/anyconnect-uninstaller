
<h2 align="center">Cisco Anyconnect Uninstaller</h2>

<p align="center">
  <a href="#descrition">Description</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#download">Download</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#build">Build</a>
</p>


## Description

Program for removing cisco anyconnect. Helps to remove bad installations and update client.

## Key Features

* Autodetect anyconnect version and its modules
* Allows to avoid many uninstall bugs
* Allows to uninstall anyconnect even if .msi is damaged
* Silent mode support
* Allows to uninstall folowing modules: ISE Compliance, ISE Posture, Posture, Network Access Manager, DART
* Allows to uninstall acnamfd driver, even if Windows can not detect it
* Kaspersky antivirus compatibility

## Download

You can [download](https://github.com/rift0nix/anyconnect-uninstaller/releases) the latest installable version of anyconnect uninstaller for Windows

## How To Use

Just run .exe as administrator. Uninstallation will start immediately.
You can use command line interface for silent run.

Optional arguments: <br />
  -h, --help            show this help message and exit <br />
  -r {yes,no,ask}, --restart {yes,no,ask} set restart parametr

Example:
```powershell
.\anyconnect-uninstaller-1.2.7.exe  --restart no
```

## Build

If you want to build .exe yourself, you'll need [Git](https://git-scm.com) and [Python3](https://www.python.org/downloads/) installed on your computer. Fast way to get them:

* Install [chocolatey](https://docs.chocolatey.org/en-us/choco/setup/#install-with-cmd.exe)
* Install folowing dependencies:
```powershell
choco install git.install -y
choco install python --version=3.10.0 -y
exit
```

Now you can build binary

```powershell
# Clone this repository
git clone https://github.com/rift0nix/anyconnect-uninstaller/
# Go into the repository
cd anyconnect-uninstaller
python -m venv .venv
.\.venv\scripts\activate
# Install dependencies
pip install pyinstaller==4.10
# Build dist\anyconnect-uninstaller.exe
.\build.bat
```
