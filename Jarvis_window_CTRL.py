import os
import subprocess
import logging
import sys
import asyncio
from fuzzywuzzy import process

try:
    from livekit.agents import function_tool
except ImportError:
    def function_tool(func): 
        return func

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import pyautogui
except Exception:
    pyautogui = None

# Setup encoding and logger
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App command map
APP_MAPPINGS = {
     "notepad": "notepad",
    "calculator": "calc",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "command prompt": "cmd",
    "control panel": "control",
    "settings": "start ms-settings:",
    "paint": "mspaint",
    "vs code": r"C:\Users\HP\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "postman": r"C:\Users\HP\AppData\Local\Postman\Postman.exe",
    "whatsapp": r"shell:AppsFolder\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "spotify": os.path.expanduser("~") + r"\AppData\Roaming\Spotify\Spotify.exe",
    "steam": r"C:\Program Files (x86)\Steam\Steam.exe",
    "gta 5": r"C:\Program Files\Rockstar Games\Grand Theft Auto V\GTA5.exe",
    "task manager": "taskmgr",
    "telegram": os.path.expanduser("~") + r"\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "file explorer": "explorer",
    "microsoft camera": r"C:\Windows\System32\WindowsCamera.exe",
    "gallery": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
    "opera": r"C:\Users\HP\AppData\Local\Programs\Opera\launcher.exe",
    "notepad launcher": "notepad",
    "virtualbox": r"C:\Program Files\Oracle\VirtualBox\VirtualBox.exe",
    "microsoft capcut": r"C:\Program Files\Microsoft CapCut\CapCut.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "outlook": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
    "onenote": r"C:\Program Files\Microsoft Office\root\Office16\ONENOTE.EXE",
    "access": r"C:\Program Files\Microsoft Office\root\Office16\MSACCESS.EXE",
    "publisher": r"C:\Program Files\Microsoft Office\root\Office16\MSPUB.EXE",
    "skype": r"C:\Program Files (x86)\Microsoft\Skype for Desktop\Skype.exe",
    "zoom": r"C:\Users\HP\AppData\Roaming\Zoom\bin\Zoom.exe",
    "discord": r"C:\Users\HP\AppData\Local\Discord\app-1.0.9003\Discord.exe",
    "slack": r"C:\Users\HP\AppData\Local\slack\slack.exe",
    "teams": r"C:\Users\HP\AppData\Local\Microsoft\Teams\current\Teams.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "opera gx": r"C:\Users\HP\AppData\Local\Programs\Opera GX\launcher.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "vivaldi": r"C:\Program Files\Vivaldi\Application\vivaldi.exe",
    "tor": r"C:\Users\HP\Desktop\Tor Browser\Browser\firefox.exe",
    "adobe reader": r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
    "adobe photoshop": r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
    "adobe illustrator": r"C:\Program Files\Adobe\Adobe Illustrator 2023\Support Files\Contents\Windows\Illustrator.exe",
    "adobe premiere": r"C:\Program Files\Adobe\Adobe Premiere Pro 2023\Adobe Premiere Pro.exe",
    "adobe after effects": r"C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\AfterFX.exe",
    "blender": r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    "gimp": r"C:\Program Files\GIMP 2\bin\gimp-2.10.exe",
    "audacity": r"C:\Program Files\Audacity\audacity.exe",
    "vlc media player": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "potplayer": r"C:\Program Files\Daum\PotPlayer\PotPlayerMini64.exe",
    "kmplayer": r"C:\Program Files (x86)\KMPlayer\KMPlayer.exe",
    "winrar": r"C:\Program Files\WinRAR\WinRAR.exe",
    "7zip": r"C:\Program Files\7-Zip\7zFM.exe",
    "notepad++": r"C:\Program Files\Notepad++\notepad++.exe",
    "sublime text": r"C:\Program Files\Sublime Text\sublime_text.exe",
    "atom": r"C:\Users\HP\AppData\Local\atom\atom.exe",
    "visual studio": r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
    "android studio": r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
    "eclipse": r"C:\Users\HP\eclipse\java-2023-03\eclipse\eclipse.exe",
    "intellij idea": r"C:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2023.1\bin\idea64.exe",
    "pycharm": r"C:\Program Files\JetBrains\PyCharm Community Edition 2023.1\bin\pycharm64.exe",
    "webstorm": r"C:\Program Files\JetBrains\WebStorm 2023.1\bin\webstorm64.exe",
    "clion": r"C:\Program Files\JetBrains\CLion 2023.1\bin\clion64.exe",
    "rider": r"C:\Program Files\JetBrains\Rider 2023.1\bin\rider64.exe",
    "datagrip": r"C:\Program Files\JetBrains\DataGrip 2023.1\bin\datagrip64.exe",
    "goland": r"C:\Program Files\JetBrains\GoLand 2023.1\bin\goland64.exe",
    "phpstorm": r"C:\Program Files\JetBrains\PhpStorm 2023.1\bin\phpstorm64.exe",
    "rubymine": r"C:\Program Files\JetBrains\RubyMine 2023.1\bin\rubymine64.exe",
    "appcode": r"C:\Program Files\JetBrains\AppCode 2023.1\bin\appcode64.exe",
    "resharper": r"C:\Program Files\JetBrains\ReSharper\v2023.1\bin\JetBrains.ReSharper.CommandLineTools.dll",
    "dotpeek": r"C:\Program Files\JetBrains\dotPeek\v2023.1\bin\dotPeek64.exe",
    "teamcity": r"C:\Program Files\JetBrains\TeamCity\bin\teamcity-server.bat",
    "youtrack": r"C:\Program Files\JetBrains\YouTrack\bin\youtrack.bat",
    "upsource": r"C:\Program Files\JetBrains\Upsource\bin\upsource.bat",
    "hub": r"C:\Program Files\JetBrains\Hub\bin\hub.bat",
    "toolbox": r"C:\Users\HP\AppData\Local\JetBrains\Toolbox\bin\jetbrains-toolbox.exe",
    "git": "git",
    "github desktop": r"C:\Users\HP\AppData\Local\GitHubDesktop\GitHubDesktop.exe",
    "tortoisegit": r"C:\Program Files\TortoiseGit\bin\TortoiseGitProc.exe",
    "sourcetree": r"C:\Users\HP\AppData\Local\Atlassian\SourceTree\SourceTree.exe",
    "mysql workbench": r"C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe",
    "postgresql": r"C:\Program Files\PostgreSQL\14\bin\pgAdmin4.exe",
    "mongodb compass": r"C:\Users\HP\AppData\Local\MongoDBCompass\MongoDBCompass.exe",
    "redis": r"C:\Program Files\Redis\redis-cli.exe",
    "docker": r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
    "kubernetes": r"C:\Program Files\Kubernetes\kubectl.exe",
    "aws cli": r"C:\Program Files\Amazon\AWSCLIV2\aws.exe",
    "azure cli": r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.exe",
    "gcp cli": r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
    "terraform": r"C:\Program Files\Terraform\terraform.exe",
    "ansible": r"C:\Program Files\Ansible\bin\ansible.exe",
    "jenkins": r"C:\Program Files\Jenkins\jenkins.exe",
    "sonarqube": r"C:\Program Files\SonarQube\bin\windows-x86-64\StartSonar.bat",
    "jira": r"C:\Program Files\Atlassian\JIRA\bin\start-jira.bat",
    "confluence": r"C:\Program Files\Atlassian\Confluence\bin\start-confluence.bat",
    "bitbucket": r"C:\Program Files\Atlassian\Bitbucket\bin\start-bitbucket.bat",
    "trello": r"shell:AppsFolder\45273LiamForsyth.PawsforTrello_7pb5ddty8z1pa!App",
    "asana": r"shell:AppsFolder\Asana.Asana_4n4kq3p7z4x8a!App",
    "todoist": r"shell:AppsFolder\Todoist.ToDoist_4n4kq3p7z4x8a!App",
    "evernote": r"C:\Program Files (x86)\Evernote\Evernote\Evernote.exe",
    "onenote": r"C:\Program Files\Microsoft Office\root\Office16\ONENOTE.EXE",
    "google keep": r"shell:AppsFolder\com.google.android.keep_1.0.0.0_x64__8wekyb3d8bbwe!App",
    "microsoft to do": r"shell:AppsFolder\Microsoft.Todos_8wekyb3d8bbwe!App",
    "calendar": r"shell:AppsFolder\microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.calendar",
    "mail": r"shell:AppsFolder\microsoft.windowscommunicationsapps_8wekyb3d8bbwe!microsoft.windowslive.mail",
    "weather": r"shell:AppsFolder\Microsoft.BingWeather_8wekyb3d8bbwe!App",
    "news": r"shell:AppsFolder\Microsoft.BingNews_8wekyb3d8bbwe!Microsoft.BingNews",
    "maps": r"shell:AppsFolder\Microsoft.WindowsMaps_8wekyb3d8bbwe!App",
    "calculator": "calc",
    "snipping tool": r"C:\Windows\System32\SnippingTool.exe",
    "steps recorder": r"C:\Windows\System32\psr.exe",
    "magnifier": r"C:\Windows\System32\Magnify.exe",
    "narrator": r"C:\Windows\System32\Narrator.exe",
    "onscreen keyboard": r"C:\Windows\System32\osk.exe",
    "character map": r"C:\Windows\System32\charmap.exe",
    "disk cleanup": r"C:\Windows\System32\cleanmgr.exe",
    "disk defragmenter": r"C:\Windows\System32\dfrgui.exe",
    "system restore": r"C:\Windows\System32\rstrui.exe",
    "system information": r"C:\Windows\System32\msinfo32.exe",
    "device manager": r"C:\Windows\System32\devmgmt.msc",
    "event viewer": r"C:\Windows\System32\eventvwr.exe",
    "services": r"C:\Windows\System32\services.msc",
    "task scheduler": r"C:\Windows\System32\taskschd.msc",
    "registry editor": r"C:\Windows\System32\regedit.exe",
    "command prompt admin": "cmd",
    "powershell": "powershell",
    "powershell admin": "powershell",
    "file explorer": "explorer",
    "run": "explorer.exe shell:::{2559a1f3-21d7-11d4-bdaf-00c04f60b9f0}",
    "control panel": "control",
    "system properties": r"C:\Windows\System32\SystemPropertiesComputerName.exe",
    "network connections": r"C:\Windows\System32\ncpa.cpl",
    "sound": r"C:\Windows\System32\mmsys.cpl",
    "display": r"C:\Windows\System32\desk.cpl",
    "mouse": r"C:\Windows\System32\main.cpl",
    "keyboard": r"C:\Windows\System32\control.exe keyboard",
    "printers": r"C:\Windows\System32\control.exe printers",
    "programs and features": r"C:\Windows\System32\appwiz.cpl",
    "windows defender": r"C:\Program Files\Windows Defender\MSASCui.exe",
    "windows security": r"C:\Windows\System32\SecHealthUI.exe",
    "windows update": r"C:\Windows\System32\control.exe /name Microsoft.WindowsUpdate",
    "backup and restore": r"C:\Windows\System32\control.exe /name Microsoft.BackupAndRestore",
    "troubleshooting": r"C:\Windows\System32\control.exe /name Microsoft.Troubleshooting",
    "recovery": r"C:\Windows\System32\control.exe /name Microsoft.Recovery",
    "system reset": r"C:\Windows\System32\SystemReset.exe",
    "shutdown": "shutdown /s /t 0",
    "restart": "shutdown /r /t 0",
    "log off": "shutdown /l",
    "lock": "rundll32.exe user32.dll,LockWorkStation",
    "hibernate": "shutdown /h",
    "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
    "screen saver": r"C:\Windows\System32\control.exe desk.cpl,,1",
    "themes": r"C:\Windows\System32\control.exe desk.cpl,,2",
    "desktop icons": r"C:\Windows\System32\control.exe desk.cpl,,0",
    "taskbar": r"C:\Windows\System32\control.exe /name Microsoft.Taskbar",
    "start menu": r"C:\Windows\System32\control.exe /name Microsoft.StartMenu",
    "action center": r"C:\Windows\System32\control.exe /name Microsoft.ActionCenter",
    "notification area": r"C:\Windows\System32\control.exe /name Microsoft.NotificationAreaIcons",
    "ease of access": r"C:\Windows\System32\control.exe /name Microsoft.EaseOfAccessCenter",
    "speech recognition": r"C:\Windows\System32\control.exe /name Microsoft.SpeechRecognition",
    "windows mobility center": r"C:\Windows\System32\mblctr.exe",
    "windows firewall": r"C:\Windows\System32\control.exe /name Microsoft.WindowsFirewall",
    "windows features": r"C:\Windows\System32\OptionalFeatures.exe",
    "internet options": r"C:\Windows\System32\inetcpl.cpl",
    "network and sharing center": r"C:\Windows\System32\control.exe /name Microsoft.NetworkAndSharingCenter",
    "homegroup": r"C:\Windows\System32\control.exe /name Microsoft.HomeGroup",
    "work folders": r"C:\Windows\System32\control.exe /name Microsoft.WorkFolders",
    "sync center": r"C:\Windows\System32\control.exe /name Microsoft.SyncCenter",
    "remote desktop": r"C:\Windows\System32\control.exe /name Microsoft.RemoteDesktop",
    "system": r"C:\Windows\System32\control.exe system",
    "advanced system settings": r"C:\Windows\System32\SystemPropertiesAdvanced.exe",
    "environment variables": r"C:\Windows\System32\SystemPropertiesAdvanced.exe",
    "user accounts": r"C:\Windows\System32\control.exe /name Microsoft.UserAccounts",
    "credential manager": r"C:\Windows\System32\control.exe /name Microsoft.CredentialManager",
    "stored user names and passwords": r"C:\Windows\System32\control.exe /name Microsoft.UserAccounts /page pageStoredUserNames",
    "certificate manager": r"C:\Windows\System32\certmgr.msc",
    "computer management": r"C:\Windows\System32\compmgmt.msc",
    "disk management": r"C:\Windows\System32\diskmgmt.msc",
    "shared folders": r"C:\Windows\System32\fsmgmt.msc",
    "local users and groups": r"C:\Windows\System32\lusrmgr.msc",
    "performance monitor": r"C:\Windows\System32\perfmon.exe",
    "resource monitor": r"C:\Windows\System32\resmon.exe",
    "reliability monitor": r"C:\Windows\System32\control.exe /name Microsoft.ReliabilityMonitor",
    "problem reports": r"C:\Windows\System32\control.exe /name Microsoft.ProblemReports",
    "windows experience index": r"C:\Windows\System32\control.exe /name Microsoft.WindowsExperienceIndex",
    "windows activation": r"C:\Windows\System32\slui.exe",
    "product key": r"C:\Windows\System32\slui.exe 0x2a 0x80070005",
    "system file checker": "sfc /scannow",
    "disk check": "chkdsk /f",
    "bootrec": "bootrec /fixmbr",
    "bcdedit": "bcdedit",
    "msconfig": r"C:\Windows\System32\msconfig.exe",
    "regedit": r"C:\Windows\System32\regedit.exe",
    "gpedit": r"C:\Windows\System32\gpedit.msc",
    "secpol": r"C:\Windows\System32\secpol.msc",
    "lusrmgr": r"C:\Windows\System32\lusrmgr.msc",
    "compmgmt": r"C:\Windows\System32\compmgmt.msc",
    "devmgmt": r"C:\Windows\System32\devmgmt.msc",
    "diskmgmt": r"C:\Windows\System32\diskmgmt.msc",
    "eventvwr": r"C:\Windows\System32\eventvwr.exe",
    "fsmgmt": r"C:\Windows\System32\fsmgmt.msc",
    "perfmon": r"C:\Windows\System32\perfmon.exe",
    "resmon": r"C:\Windows\System32\resmon.exe",
    "taskschd": r"C:\Windows\System32\taskschd.msc",
    "services": r"C:\Windows\System32\services.msc",
    "wmimgmt": r"C:\Windows\System32\wbem\wmimgmt.msc",
    "adsiedit": r"C:\Windows\System32\adsiedit.msc",
    "dsa": r"C:\Windows\System32\dsa.msc",
    "dssite": r"C:\Windows\System32\dssite.msc",
    "domain": r"C:\Windows\System32\domain.msc",
    "dssites": r"C:\Windows\System32\dssites.msc",
    "dfs": r"C:\Windows\System32\dfs.msc",
    "dfsmgmt": r"C:\Windows\System32\dfsmgmt.msc",
    "dns": r"C:\Windows\System32\dns.msc",
    "dhcp": r"C:\Windows\System32\dhcp.msc",
    "wins": r"C:\Windows\System32\wins.msc",
    "routing": r"C:\Windows\System32\routing.msc",
    "rras": r"C:\Windows\System32\rras.msc",
    "ias": r"C:\Windows\System32\ias.msc",
    "nps": r"C:\Windows\System32\nps.msc",
    "tsconfig": r"C:\Windows\System32\tsconfig.msc",
    "tsadmin": r"C:\Windows\System32\tsadmin.exe",
    "rdp": r"C:\Windows\System32\mstsc.exe",
    "hyper-v": r"C:\Windows\System32\virtmgmt.msc",
    "vmconnect": r"C:\Windows\System32\vmconnect.exe",
    "vmms": r"C:\Windows\System32\vmms.exe",
    "vmm": r"C:\Windows\System32\vmm.exe",
    "vds": r"C:\Windows\System32\vds.msc",
    "iscsi": r"C:\Windows\System32\iscsicpl.exe",
    "mpc": r"C:\Windows\System32\mpc-hc64.exe",
    "wmplayer": r"C:\Program Files\Windows Media Player\wmplayer.exe",
    "wmp": r"C:\Program Files\Windows Media Player\wmplayer.exe",
    "quicktime": r"C:\Program Files (x86)\QuickTime\QuickTimePlayer.exe",
    "itunes": r"C:\Program Files\iTunes\iTunes.exe",
    "winamp": r"C:\Program Files (x86)\Winamp\winamp.exe",
    "foobar2000": r"C:\Program Files (x86)\foobar2000\foobar2000.exe",
    "aimp": r"C:\Program Files (x86)\AIMP\AIMP.exe",
    "clementine": r"C:\Program Files\Clementine\clementine.exe",
    "rhythmbox": r"C:\Program Files\Rhythmbox\rhythmbox.exe",
    "banshee": r"C:\Program Files\Banshee\banshee.exe",
    "amarok": r"C:\Program Files\Amarok\amarok.exe",
    "spotify": os.path.expanduser("~") + r"\AppData\Roaming\Spotify\Spotify.exe",
    "deezer": r"shell:AppsFolder\Deezer.DeezerMusic_0.0.0.0_x64__z1c4v35pc3y7t!App",
    "tidal": r"shell:AppsFolder\TIDALMusicAS.tidalMusicAS_0.0.0.0_x64__7e9zc8jpqqe6e!App",
    "pandora": r"shell:AppsFolder\PandoraMediaInc.29680B314EFC2_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "soundcloud": r"shell:AppsFolder\SoundCloud.SoundCloud_desktop_0.0.0.0_x64__a7j6p0v1b1a7e!App",
    "youtube music": r"shell:AppsFolder\GoogleInc.YouTubeMusic_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "apple music": r"shell:AppsFolder\AppleInc.iTunes_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "amazon music": r"shell:AppsFolder\AmazonMusic.AmazonMusic_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "microsoft groove": r"shell:AppsFolder\Microsoft.ZuneMusic_8wekyb3d8bbwe!Microsoft.ZuneMusic",
    "microsoft movies & tv": r"shell:AppsFolder\Microsoft.ZuneVideo_8wekyb3d8bbwe!Microsoft.ZuneVideo",
    "netflix": r"shell:AppsFolder\4DF9E0F8.Netflix_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "amazon prime video": r"shell:AppsFolder\AmazonVideo.PrimeVideo_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "disney+": r"shell:AppsFolder\Disney.37853FC22B2CE_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "hulu": r"shell:AppsFolder\HuluLLC.HuluPlus_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "hbo max": r"shell:AppsFolder\HBO.HBOMax_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "peacock": r"shell:AppsFolder\PeacockTV.Peacock_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "paramount+": r"shell:AppsFolder\Paramount.ParamountPlus_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "crunchyroll": r"shell:AppsFolder\Crunchyroll.Crunchyroll_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "funimation": r"shell:AppsFolder\Funimation.Funimation_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "twitch": r"shell:AppsFolder\TwitchInteractiveInc.Twitch_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "youtube": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Note: This is a placeholder; actual YouTube app may vary
    "instagram": r"shell:AppsFolder\Facebook.Instagram_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "facebook": r"shell:AppsFolder\Facebook.Facebook_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "twitter": r"shell:AppsFolder\Twitter.Twitter_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "linkedin": r"shell:AppsFolder\Microsoft.LinkedInforWindows_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "tiktok": r"shell:AppsFolder\TikTok.TikTok_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "snapchat": r"shell:AppsFolder\Snapchat.Snapchat_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "pinterest": r"shell:AppsFolder\Pinterest.Pinterest_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "reddit": r"shell:AppsFolder\RedditInc.Reddit_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "tumblr": r"shell:AppsFolder\Tumblr.Tumblr_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "flickr": r"shell:AppsFolder\Flickr.Flickr_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "imgur": r"shell:AppsFolder\Imgur.Imgur_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "deviantart": r"shell:AppsFolder\DeviantArt.DeviantArt_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "behance": r"shell:AppsFolder\AdobeSystemsIncorporated.Behance_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "dribbble": r"shell:AppsFolder\Dribbble.Dribbble_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "github": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "stackoverflow": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "quora": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "medium": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "wordpress": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "dropbox": r"C:\Users\HP\AppData\Roaming\Dropbox\bin\Dropbox.exe",
    "googledrive": r"C:\Program Files\Google\Drive File Stream\launch.bat",
    "onedrive": r"C:\Users\HP\AppData\Local\Microsoft\OneDrive\OneDrive.exe",
    "box": r"C:\Program Files\Box\Box.exe",
    "mega": r"C:\Users\HP\AppData\Local\MEGAsync\MEGAsync.exe",
    "pcloud": r"C:\Users\HP\AppData\Local\pCloud\pCloud.exe",
    "icloud": r"C:\Program Files (x86)\Common Files\Apple\Internet Services\iCloudServices.exe",
    "google photos": r"shell:AppsFolder\GoogleInc.GooglePhotos_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "flickr": r"shell:AppsFolder\Flickr.Flickr_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "imgur": r"shell:AppsFolder\Imgur.Imgur_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "photoshop express": r"shell:AppsFolder\AdobeSystemsIncorporated.PhotoshopExpress_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "lightroom": r"C:\Program Files\Adobe\Adobe Lightroom Classic\Lightroom.exe",
    "capture one": r"C:\Program Files\Phase One\Capture One 23\CaptureOne.exe",
    "darktable": r"C:\Program Files\darktable\bin\darktable.exe",
    "rawtherapee": r"C:\Program Files\RawTherapee\rawtherapee.exe",
    "digikam": r"C:\Program Files\digiKam\bin\digikam.exe",
    "shotwell": r"C:\Program Files\Shotwell\shotwell.exe",
    "gthumb": r"C:\Program Files\gThumb\gthumb.exe",
    "eog": r"C:\Program Files\eog\eog.exe",
    "gwenview": r"C:\Program Files\KDE\kde4\bin\gwenview.exe",
    "irfanview": r"C:\Program Files (x86)\IrfanView\i_view64.exe",
    "xnview": r"C:\Program Files\XnView\xnview.exe",
    "faststone": r"C:\Program Files (x86)\FastStone Image Viewer\FSViewer.exe",
    "honeyview": r"C:\Program Files\Honeyview\Honeyview.exe",
    "nomacs": r"C:\Program Files\nomacs\bin\nomacs.exe",
    "geeqie": r"C:\Program Files\Geeqie\geeqie.exe",
    "feh": r"C:\Program Files\feh\feh.exe",
    "sxiv": r"C:\Program Files\sxiv\sxiv.exe",
    "ristretto": r"C:\Program Files\Ristretto\ristretto.exe",
    "gpicview": r"C:\Program Files\GPicView\gpicview.exe",
    "mirage": r"C:\Program Files\Mirage\mirage.exe",
    "viewnior": r"C:\Program Files\Viewnior\viewnior.exe",
    "eom": r"C:\Program Files\MATE\eom.exe",
    "gthumb": r"C:\Program Files\gThumb\gthumb.exe",
    "shotwell": r"C:\Program Files\Shotwell\shotwell.exe",
    "digikam": r"C:\Program Files\digiKam\bin\digikam.exe",
    "darktable": r"C:\Program Files\darktable\bin\darktable.exe",
    "rawtherapee": r"C:\Program Files\RawTherapee\rawtherapee.exe",
    "capture one": r"C:\Program Files\Phase One\Capture One 23\CaptureOne.exe",
    "lightroom": r"C:\Program Files\Adobe\Adobe Lightroom Classic\Lightroom.exe",
    "photoshop express": r"shell:AppsFolder\AdobeSystemsIncorporated.PhotoshopExpress_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "google photos": r"shell:AppsFolder\GoogleInc.GooglePhotos_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "flickr": r"shell:AppsFolder\Flickr.Flickr_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "imgur": r"shell:AppsFolder\Imgur.Imgur_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "deviantart": r"shell:AppsFolder\DeviantArt.DeviantArt_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "behance": r"shell:AppsFolder\AdobeSystemsIncorporated.Behance_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "dribbble": r"shell:AppsFolder\Dribbble.Dribbble_0.0.0.0_x64__6b4xz7sj4mx0a!App",
    "github": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "stackoverflow": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "quora": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "medium": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "wordpress": r"shell:AppsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App",  # Placeholder
    "dropbox": r"C:\Users\HP\AppData\Roaming\Dropbox\bin\Dropbox.exe",
    "googledrive": r"C:\Program Files\Google\Drive File Stream\launch.bat",
    "onedrive": r"C:\Users\HP\AppData\Local\Microsoft\OneDrive\OneDrive.exe",
    "box": r"C:\Program Files\Box\Box.exe",
    "mega": r"C:\Users\HP\AppData\Local\MEGAsync\MEGAsync.exe",
    # add or override with your paths
}

# -------------------------
# Global focus utility
# -------------------------
async def focus_window(title_keyword: str) -> bool:
    if not gw:
        logger.warning("⚠ pygetwindow")
        return False

    await asyncio.sleep(1.5)  # Give time for window to appear
    title_keyword = title_keyword.lower().strip()

    for window in gw.getAllWindows():
        if title_keyword in window.title.lower():
            if window.isMinimized:
                window.restore()
            window.activate()
            return True
    return False

# Index files/folders
async def index_items(base_dirs):
    item_index = []
    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            for d in dirs:
                item_index.append({"name": d, "path": os.path.join(root, d), "type": "folder"})
            for f in files:
                item_index.append({"name": f, "path": os.path.join(root, f), "type": "file"})
    logger.info(f"✅ Indexed {len(item_index)} items.")
    return item_index

async def search_item(query, index, item_type):
    filtered = [item for item in index if item["type"] == item_type]
    choices = [item["name"] for item in filtered]
    if not choices:
        return None
    best_match, score = process.extractOne(query, choices)
    logger.info(f"🔍 Matched '{query}' to '{best_match}' with score {score}")
    if score > 70:
        for item in filtered:
            if item["name"] == best_match:
                return item
    return None

# File/folder actions
async def open_folder(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया। {e}")

async def play_file(path):
    try:
        os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
        await focus_window(os.path.basename(path))
    except Exception as e:
        logger.error(f"❌ फ़ाइल open करने में error आया।: {e}")

async def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Folder create हो गया।: {path}"
    except Exception as e:
        return f"❌ फ़ाइल create करने में error आया।: {e}"

async def rename_item(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        return f"✅ नाम बदलकर {new_path} कर दिया गया।"
    except Exception as e:
        return f"❌ नाम बदलना fail हो गया: {e}"

async def delete_item(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return f"🗑️ Deleted: {path}"
    except Exception as e:
        return f"❌ Delete नहीं हुआ।: {e}"

# App control
@function_tool
async def open(app_title: str) -> str:
    app_title = app_title.lower().strip()
    app_command = APP_MAPPINGS.get(app_title, app_title)
    try:
        # Try Start Menu search first (more reliable for UWP / Store apps and pinned items)
        if pyautogui:
            try:
                # Run the start/search sequence in a thread to avoid blocking the event loop
                async def _start_search_and_open():
                    # Press the Windows key to open Start
                    await asyncio.to_thread(pyautogui.press, 'win')
                    # Small delay to allow Start menu to open
                    await asyncio.sleep(0.6)
                    # Type the app title
                    await asyncio.to_thread(pyautogui.write, app_title, 0.05)
                    await asyncio.sleep(0.6)
                    # Press Enter to open the top result
                    await asyncio.to_thread(pyautogui.press, 'enter')
                await _start_search_and_open()
                # Give time for window to appear
                await asyncio.sleep(1.2)
                focused = await focus_window(app_title)
                if focused:
                    return f"🚀 App launched via Start search and focused: {app_title}."
                # If not focused, fallback to start command below
            except Exception as e:
                logger.warning(f"Start-search launcher failed: {e}")

        # Fallback: use start shell command
        await asyncio.create_subprocess_shell(f'start "" "{app_command}"', shell=True)
        focused = await focus_window(app_title)
        if focused:
            return f"🚀 App launch हुआ और focus में है: {app_title}."
        else:
            return f"🚀 {app_title} Launch किया गया, लेकिन window पर focus नहीं हो पाया।"
    except Exception as e:
        return f"❌ {app_title} Launch नहीं हो पाया।: {e}"

@function_tool
async def close(window_title: str) -> str:
    if not win32gui:
        return "❌ win32gui"

    def enumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    win32gui.EnumWindows(enumHandler, None)
    return f"❌ Window बंद हो गई है।: {window_title}"

# ADA command logic
@function_tool
async def folder_file(command: str) -> str:
    folders_to_index = ["D:/"]
    index = await index_items(folders_to_index)
    command_lower = command.lower()

    if "create folder" in command_lower:
        folder_name = command.replace("create folder", "").strip()
        path = os.path.join("D:/", folder_name)
        return await create_folder(path)

    if "rename" in command_lower:
        parts = command_lower.replace("rename", "").strip().split("to")
        if len(parts) == 2:
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            item = await search_item(old_name, index, "folder")
            if item:
                new_path = os.path.join(os.path.dirname(item["path"]), new_name)
                return await rename_item(item["path"], new_path)
        return "❌ rename command valid नहीं है।"

    if "delete" in command_lower:
        item = await search_item(command, index, "folder") or await search_item(command, index, "file")
        if item:
            return await delete_item(item["path"])
        return "❌ Delete करने के लिए item नहीं मिला।"

    if "folder" in command_lower or "open folder" in command_lower:
        item = await search_item(command, index, "folder")
        if item:
            await open_folder(item["path"])
            return f"✅ Folder opened: {item['name']}"
        return "❌ Folder नहीं मिला।."

    item = await search_item(command, index, "file")
    if item:
        await play_file(item["path"])
        return f"✅ File opened: {item['name']}"

    return "⚠ कुछ भी match नहीं हुआ।"
