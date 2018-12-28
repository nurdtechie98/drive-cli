from __future__ import print_function
import os
import sys
import io
import re
import getpass
import subprocess
import requests
import click
import json
import time
import colorama
from pick import pick
from pick import Picker
from prettytable import PrettyTable
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools

dirpath = os.path.dirname(os.path.realpath(__file__))
SCOPES = 'https://www.googleapis.com/auth/drive'
MIMETYPES={ 
            ".323":"text/h323" ,
            ".3g2":"video/3gpp2" ,
            ".3gp":"video/3gpp" ,
            ".3gp2":"video/3gpp2" ,
            ".3gpp":"video/3gpp" ,
            ".7z":"application/x-7z-compressed" ,
            ".aa":"audio/audible" ,
            ".AAC":"audio/aac" ,
            ".aaf":"application/octet-stream" ,
            ".aax":"audio/vnd.audible.aax" ,
            ".ac3":"audio/ac3" ,
            ".aca":"application/octet-stream" ,
            ".accda":"application/msaccess.addin" ,
            ".accdb":"application/msaccess" ,
            ".accdc":"application/msaccess.cab" ,
            ".accde":"application/msaccess" ,
            ".accdr":"application/msaccess.runtime" ,
            ".accdt":"application/msaccess" ,
            ".accdw":"application/msaccess.webapplication" ,
            ".accft":"application/msaccess.ftemplate" ,
            ".acx":"application/internet-property-stream" ,
            ".AddIn":"text/xml" ,
            ".ade":"application/msaccess" ,
            ".adobebridge":"application/x-bridge-url" ,
            ".adp":"application/msaccess" ,
            ".ADT":"audio/vnd.dlna.adts" ,
            ".ADTS":"audio/aac" ,
            ".afm":"application/octet-stream" ,
            ".ai":"application/postscript" ,
            ".aif":"audio/x-aiff" ,
            ".aifc":"audio/aiff" ,
            ".aiff":"audio/aiff" ,
            ".air":"application/vnd.adobe.air-application-installer-package+zip" ,
            ".amc":"application/x-mpeg" ,
            ".application":"application/x-ms-application" ,
            ".art":"image/x-jg" ,
            ".asa":"application/xml" ,
            ".asax":"application/xml" ,
            ".ascx":"application/xml" ,
            ".asd":"application/octet-stream" ,
            ".asf":"video/x-ms-asf" ,
            ".ashx":"application/xml" ,
            ".asi":"application/octet-stream" ,
            ".asm":"text/plain" ,
            ".asmx":"application/xml" ,
            ".aspx":"application/xml" ,
            ".asr":"video/x-ms-asf" ,
            ".asx":"video/x-ms-asf" ,
            ".atom":"application/atom+xml" ,
            ".au":"audio/basic" ,
            ".avi":"video/x-msvideo" ,
            ".axs":"application/olescript" ,
            ".bas":"text/plain" ,
            ".bcpio":"application/x-bcpio" ,
            ".bin":"application/octet-stream" ,
            ".bmp":"image/bmp" ,
            ".c":"text/plain" ,
            ".cab":"application/octet-stream" ,
            ".caf":"audio/x-caf" ,
            ".calx":"application/vnd.ms-office.calx" ,
            ".cat":"application/vnd.ms-pki.seccat" ,
            ".cc":"text/plain" ,
            ".cd":"text/plain" ,
            ".cdda":"audio/aiff" ,
            ".cdf":"application/x-cdf" ,
            ".cer":"application/x-x509-ca-cert" ,
            ".chm":"application/octet-stream" ,
            ".class":"application/x-java-applet" ,
            ".clp":"application/x-msclip" ,
            ".cmx":"image/x-cmx" ,
            ".cnf":"text/plain" ,
            ".cod":"image/cis-cod" ,
            ".config":"application/xml" ,
            ".contact":"text/x-ms-contact" ,
            ".coverage":"application/xml" ,
            ".cpio":"application/x-cpio" ,
            ".cpp":"text/plain" ,
            ".crd":"application/x-mscardfile" ,
            ".crl":"application/pkix-crl" ,
            ".crt":"application/x-x509-ca-cert" ,
            ".cs":"text/plain" ,
            ".csdproj":"text/plain" ,
            ".csh":"application/x-csh" ,
            ".csproj":"text/plain" ,
            ".css":"text/css" ,
            ".csv":"text/csv" ,
            ".cur":"application/octet-stream" ,
            ".cxx":"text/plain" ,
            ".dat":"application/octet-stream" ,
            ".datasource":"application/xml" ,
            ".dbproj":"text/plain" ,
            ".dcr":"application/x-director" ,
            ".def":"text/plain" ,
            ".deploy":"application/octet-stream" ,
            ".der":"application/x-x509-ca-cert" ,
            ".dgml":"application/xml" ,
            ".dib":"image/bmp" ,
            ".dif":"video/x-dv" ,
            ".dir":"application/x-director" ,
            ".disco":"text/xml" ,
            ".dll":"application/x-msdownload" ,
            ".dll.config":"text/xml" ,
            ".dlm":"text/dlm" ,
            ".doc":"application/msword" ,
            ".docm":"application/vnd.ms-word.document.macroEnabled.12" ,
            ".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document" ,
            ".dot":"application/msword" ,
            ".dotm":"application/vnd.ms-word.template.macroEnabled.12" ,
            ".dotx":"application/vnd.openxmlformats-officedocument.wordprocessingml.template" ,
            ".dsp":"application/octet-stream" ,
            ".dsw":"text/plain" ,
            ".dtd":"text/xml" ,
            ".dtsConfig":"text/xml" ,
            ".dv":"video/x-dv" ,
            ".dvi":"application/x-dvi" ,
            ".dwf":"drawing/x-dwf" ,
            ".dwp":"application/octet-stream" ,
            ".dxr":"application/x-director" ,
            ".eml":"message/rfc822" ,
            ".emz":"application/octet-stream" ,
            ".eot":"application/octet-stream" ,
            ".eps":"application/postscript" ,
            ".etl":"application/etl" ,
            ".etx":"text/x-setext" ,
            ".evy":"application/envoy" ,
            ".exe":"application/octet-stream" ,
            ".exe.config":"text/xml" ,
            ".fdf":"application/vnd.fdf" ,
            ".fif":"application/fractals" ,
            ".filters":"Application/xml" ,
            ".fla":"application/octet-stream" ,
            ".flr":"x-world/x-vrml" ,
            ".flv":"video/x-flv" ,
            ".fsscript":"application/fsharp-script" ,
            ".fsx":"application/fsharp-script" ,
            ".generictest":"application/xml" ,
            ".gif":"image/gif" ,
            ".group":"text/x-ms-group" ,
            ".gsm":"audio/x-gsm" ,
            ".gtar":"application/x-gtar" ,
            ".gz":"application/x-gzip" ,
            ".h":"text/plain" ,
            ".hdf":"application/x-hdf" ,
            ".hdml":"text/x-hdml" ,
            ".hhc":"application/x-oleobject" ,
            ".hhk":"application/octet-stream" ,
            ".hhp":"application/octet-stream" ,
            ".hlp":"application/winhlp" ,
            ".hpp":"text/plain" ,
            ".hqx":"application/mac-binhex40" ,
            ".hta":"application/hta" ,
            ".htc":"text/x-component" ,
            ".htm":"text/html" ,
            ".html":"text/html" ,
            ".htt":"text/webviewhtml" ,
            ".hxa":"application/xml" ,
            ".hxc":"application/xml" ,
            ".hxd":"application/octet-stream" ,
            ".hxe":"application/xml" ,
            ".hxf":"application/xml" ,
            ".hxh":"application/octet-stream" ,
            ".hxi":"application/octet-stream" ,
            ".hxk":"application/xml" ,
            ".hxq":"application/octet-stream" ,
            ".hxr":"application/octet-stream" ,
            ".hxs":"application/octet-stream" ,
            ".hxt":"text/html" ,
            ".hxv":"application/xml" ,
            ".hxw":"application/octet-stream" ,
            ".hxx":"text/plain" ,
            ".i":"text/plain" ,
            ".ico":"image/x-icon" ,
            ".ics":"application/octet-stream" ,
            ".idl":"text/plain" ,
            ".ief":"image/ief" ,
            ".iii":"application/x-iphone" ,
            ".inc":"text/plain" ,
            ".inf":"application/octet-stream" ,
            ".inl":"text/plain" ,
            ".ins":"application/x-internet-signup" ,
            ".ipa":"application/x-itunes-ipa" ,
            ".ipg":"application/x-itunes-ipg" ,
            ".ipproj":"text/plain" ,
            ".ipsw":"application/x-itunes-ipsw" ,
            ".iqy":"text/x-ms-iqy" ,
            ".isp":"application/x-internet-signup" ,
            ".ite":"application/x-itunes-ite" ,
            ".itlp":"application/x-itunes-itlp" ,
            ".itms":"application/x-itunes-itms" ,
            ".itpc":"application/x-itunes-itpc" ,
            ".IVF":"video/x-ivf" ,
            ".jar":"application/java-archive" ,
            ".java":"application/octet-stream" ,
            ".jck":"application/liquidmotion" ,
            ".jcz":"application/liquidmotion" ,
            ".jfif":"image/pjpeg" ,
            ".jnlp":"application/x-java-jnlp-file" ,
            ".jpb":"application/octet-stream" ,
            ".jpe":"image/jpeg" ,
            ".jpeg":"image/jpeg" ,
            ".jpg":"image/jpeg" ,
            ".js":"application/x-javascript" ,
            ".jsx":"text/jscript" ,
            ".jsxbin":"text/plain" ,
            ".latex":"application/x-latex" ,
            ".library-ms":"application/windows-library+xml" ,
            ".lit":"application/x-ms-reader" ,
            ".loadtest":"application/xml" ,
            ".lpk":"application/octet-stream" ,
            ".lsf":"video/x-la-asf" ,
            ".lst":"text/plain" ,
            ".lsx":"video/x-la-asf" ,
            ".lzh":"application/octet-stream" ,
            ".m13":"application/x-msmediaview" ,
            ".m14":"application/x-msmediaview" ,
            ".m1v":"video/mpeg" ,
            ".m2t":"video/vnd.dlna.mpeg-tts" ,
            ".m2ts":"video/vnd.dlna.mpeg-tts" ,
            ".m2v":"video/mpeg" ,
            ".m3u":"audio/x-mpegurl" ,
            ".m3u8":"audio/x-mpegurl" ,
            ".m4a":"audio/m4a" ,
            ".m4b":"audio/m4b" ,
            ".m4p":"audio/m4p" ,
            ".m4r":"audio/x-m4r" ,
            ".m4v":"video/x-m4v" ,
            ".mac":"image/x-macpaint" ,
            ".mak":"text/plain" ,
            ".man":"application/x-troff-man" ,
            ".manifest":"application/x-ms-manifest" ,
            ".map":"text/plain" ,
            ".master":"application/xml" ,
            ".mda":"application/msaccess" ,
            ".mdb":"application/x-msaccess" ,
            ".mde":"application/msaccess" ,
            ".mdp":"application/octet-stream" ,
            ".me":"application/x-troff-me" ,
            ".mfp":"application/x-shockwave-flash" ,
            ".mht":"message/rfc822" ,
            ".mhtml":"message/rfc822" ,
            ".mid":"audio/mid" ,
            ".midi":"audio/mid" ,
            ".mix":"application/octet-stream" ,
            ".mk":"text/plain" ,
            ".mmf":"application/x-smaf" ,
            ".mno":"text/xml" ,
            ".mny":"application/x-msmoney" ,
            ".mod":"video/mpeg" ,
            ".mov":"video/quicktime" ,
            ".movie":"video/x-sgi-movie" ,
            ".mp2":"video/mpeg" ,
            ".mp2v":"video/mpeg" ,
            ".mp3":"audio/mpeg" ,
            ".mp4":"video/mp4" ,
            ".mp4v":"video/mp4" ,
            ".mpa":"video/mpeg" ,
            ".mpe":"video/mpeg" ,
            ".mpeg":"video/mpeg" ,
            ".mpf":"application/vnd.ms-mediapackage" ,
            ".mpg":"video/mpeg" ,
            ".mpp":"application/vnd.ms-project" ,
            ".mpv2":"video/mpeg" ,
            ".mqv":"video/quicktime" ,
            ".ms":"application/x-troff-ms" ,
            ".msi":"application/octet-stream" ,
            ".mso":"application/octet-stream" ,
            ".mts":"video/vnd.dlna.mpeg-tts" ,
            ".mtx":"application/xml" ,
            ".mvb":"application/x-msmediaview" ,
            ".mvc":"application/x-miva-compiled" ,
            ".mxp":"application/x-mmxp" ,
            ".nc":"application/x-netcdf" ,
            ".nsc":"video/x-ms-asf" ,
            ".nws":"message/rfc822" ,
            ".ocx":"application/octet-stream" ,
            ".oda":"application/oda" ,
            ".odc":"text/x-ms-odc" ,
            ".odh":"text/plain" ,
            ".odl":"text/plain" ,
            ".odp":"application/vnd.oasis.opendocument.presentation" ,
            ".ods":"application/oleobject" ,
            ".odt":"application/vnd.oasis.opendocument.text" ,
            ".one":"application/onenote" ,
            ".onea":"application/onenote" ,
            ".onepkg":"application/onenote" ,
            ".onetmp":"application/onenote" ,
            ".onetoc":"application/onenote" ,
            ".onetoc2":"application/onenote" ,
            ".orderedtest":"application/xml" ,
            ".osdx":"application/opensearchdescription+xml" ,
            ".p10":"application/pkcs10" ,
            ".p12":"application/x-pkcs12" ,
            ".p7b":"application/x-pkcs7-certificates" ,
            ".p7c":"application/pkcs7-mime" ,
            ".p7m":"application/pkcs7-mime" ,
            ".p7r":"application/x-pkcs7-certreqresp" ,
            ".p7s":"application/pkcs7-signature" ,
            ".pbm":"image/x-portable-bitmap" ,
            ".pcast":"application/x-podcast" ,
            ".pct":"image/pict" ,
            ".pcx":"application/octet-stream" ,
            ".pcz":"application/octet-stream" ,
            ".pdf":"application/pdf" ,
            ".pfb":"application/octet-stream" ,
            ".pfm":"application/octet-stream" ,
            ".pfx":"application/x-pkcs12" ,
            ".pgm":"image/x-portable-graymap" ,
            ".pic":"image/pict" ,
            ".pict":"image/pict" ,
            ".pkgdef":"text/plain" ,
            ".pkgundef":"text/plain" ,
            ".pko":"application/vnd.ms-pki.pko" ,
            ".pls":"audio/scpls" ,
            ".pma":"application/x-perfmon" ,
            ".pmc":"application/x-perfmon" ,
            ".pml":"application/x-perfmon" ,
            ".pmr":"application/x-perfmon" ,
            ".pmw":"application/x-perfmon" ,
            ".png":"image/png" ,
            ".pnm":"image/x-portable-anymap" ,
            ".pnt":"image/x-macpaint" ,
            ".pntg":"image/x-macpaint" ,
            ".pnz":"image/png" ,
            ".pot":"application/vnd.ms-powerpoint" ,
            ".potm":"application/vnd.ms-powerpoint.template.macroEnabled.12" ,
            ".potx":"application/vnd.openxmlformats-officedocument.presentationml.template" ,
            ".ppa":"application/vnd.ms-powerpoint" ,
            ".ppam":"application/vnd.ms-powerpoint.addin.macroEnabled.12" ,
            ".ppm":"image/x-portable-pixmap" ,
            ".pps":"application/vnd.ms-powerpoint" ,
            ".ppsm":"application/vnd.ms-powerpoint.slideshow.macroEnabled.12" ,
            ".ppsx":"application/vnd.openxmlformats-officedocument.presentationml.slideshow" ,
            ".ppt":"application/vnd.ms-powerpoint" ,
            ".pptm":"application/vnd.ms-powerpoint.presentation.macroEnabled.12" ,
            ".pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation" ,
            ".prf":"application/pics-rules" ,
            ".prm":"application/octet-stream" ,
            ".prx":"application/octet-stream" ,
            ".ps":"application/postscript" ,
            ".psc1":"application/PowerShell" ,
            ".psd":"application/octet-stream" ,
            ".psess":"application/xml" ,
            ".psm":"application/octet-stream" ,
            ".psp":"application/octet-stream" ,
            ".pub":"application/x-mspublisher" ,
            ".pwz":"application/vnd.ms-powerpoint" ,
            ".qht":"text/x-html-insertion" ,
            ".qhtm":"text/x-html-insertion" ,
            ".qt":"video/quicktime" ,
            ".qti":"image/x-quicktime" ,
            ".qtif":"image/x-quicktime" ,
            ".qtl":"application/x-quicktimeplayer" ,
            ".qxd":"application/octet-stream" ,
            ".ra":"audio/x-pn-realaudio" ,
            ".ram":"audio/x-pn-realaudio" ,
            ".rar":"application/octet-stream" ,
            ".ras":"image/x-cmu-raster" ,
            ".rat":"application/rat-file" ,
            ".rc":"text/plain" ,
            ".rc2":"text/plain" ,
            ".rct":"text/plain" ,
            ".rdlc":"application/xml" ,
            ".resx":"application/xml" ,
            ".rf":"image/vnd.rn-realflash" ,
            ".rgb":"image/x-rgb" ,
            ".rgs":"text/plain" ,
            ".rm":"application/vnd.rn-realmedia" ,
            ".rmi":"audio/mid" ,
            ".rmp":"application/vnd.rn-rn_music_package" ,
            ".roff":"application/x-troff" ,
            ".rpm":"audio/x-pn-realaudio-plugin" ,
            ".rqy":"text/x-ms-rqy" ,
            ".rtf":"application/rtf" ,
            ".rtx":"text/richtext" ,
            ".ruleset":"application/xml" ,
            ".s":"text/plain" ,
            ".safariextz":"application/x-safari-safariextz" ,
            ".scd":"application/x-msschedule" ,
            ".sct":"text/scriptlet" ,
            ".sd2":"audio/x-sd2" ,
            ".sdp":"application/sdp" ,
            ".sea":"application/octet-stream" ,
            ".searchConnector-ms":"application/windows-search-connector+xml" ,
            ".setpay":"application/set-payment-initiation" ,
            ".setreg":"application/set-registration-initiation" ,
            ".settings":"application/xml" ,
            ".sgimb":"application/x-sgimb" ,
            ".sgml":"text/sgml" ,
            ".sh":"application/x-sh" ,
            ".shar":"application/x-shar" ,
            ".shtml":"text/html" ,
            ".sit":"application/x-stuffit" ,
            ".sitemap":"application/xml" ,
            ".skin":"application/xml" ,
            ".sldm":"application/vnd.ms-powerpoint.slide.macroEnabled.12" ,
            ".sldx":"application/vnd.openxmlformats-officedocument.presentationml.slide" ,
            ".slk":"application/vnd.ms-excel" ,
            ".sln":"text/plain" ,
            ".slupkg-ms":"application/x-ms-license" ,
            ".smd":"audio/x-smd" ,
            ".smi":"application/octet-stream" ,
            ".smx":"audio/x-smd" ,
            ".smz":"audio/x-smd" ,
            ".snd":"audio/basic" ,
            ".snippet":"application/xml" ,
            ".snp":"application/octet-stream" ,
            ".sol":"text/plain" ,
            ".sor":"text/plain" ,
            ".spc":"application/x-pkcs7-certificates" ,
            ".spl":"application/futuresplash" ,
            ".src":"application/x-wais-source" ,
            ".srf":"text/plain" ,
            ".SSISDeploymentManifest":"text/xml" ,
            ".ssm":"application/streamingmedia" ,
            ".sst":"application/vnd.ms-pki.certstore" ,
            ".stl":"application/vnd.ms-pki.stl" ,
            ".sv4cpio":"application/x-sv4cpio" ,
            ".sv4crc":"application/x-sv4crc" ,
            ".svc":"application/xml" ,
            ".swf":"application/x-shockwave-flash" ,
            ".t":"application/x-troff" ,
            ".tar":"application/x-tar" ,
            ".tcl":"application/x-tcl" ,
            ".testrunconfig":"application/xml" ,
            ".testsettings":"application/xml" ,
            ".tex":"application/x-tex" ,
            ".texi":"application/x-texinfo" ,
            ".texinfo":"application/x-texinfo" ,
            ".tgz":"application/x-compressed" ,
            ".thmx":"application/vnd.ms-officetheme" ,
            ".thn":"application/octet-stream" ,
            ".tif":"image/tiff" ,
            ".tiff":"image/tiff" ,
            ".tlh":"text/plain" ,
            ".tli":"text/plain" ,
            ".toc":"application/octet-stream" ,
            ".tr":"application/x-troff" ,
            ".trm":"application/x-msterminal" ,
            ".trx":"application/xml" ,
            ".ts":"video/vnd.dlna.mpeg-tts" ,
            ".tsv":"text/tab-separated-values" ,
            ".ttf":"application/octet-stream" ,
            ".tts":"video/vnd.dlna.mpeg-tts" ,
            ".txt":"text/plain" ,
            ".u32":"application/octet-stream" ,
            ".uls":"text/iuls" ,
            ".user":"text/plain" ,
            ".ustar":"application/x-ustar" ,
            ".vb":"text/plain" ,
            ".vbdproj":"text/plain" ,
            ".vbk":"video/mpeg" ,
            ".vbproj":"text/plain" ,
            ".vbs":"text/vbscript" ,
            ".vcf":"text/x-vcard" ,
            ".vcproj":"Application/xml" ,
            ".vcs":"text/plain" ,
            ".vcxproj":"Application/xml" ,
            ".vddproj":"text/plain" ,
            ".vdp":"text/plain" ,
            ".vdproj":"text/plain" ,
            ".vdx":"application/vnd.ms-visio.viewer" ,
            ".vml":"text/xml" ,
            ".vscontent":"application/xml" ,
            ".vsct":"text/xml" ,
            ".vsd":"application/vnd.visio" ,
            ".vsi":"application/ms-vsi" ,
            ".vsix":"application/vsix" ,
            ".vsixlangpack":"text/xml" ,
            ".vsixmanifest":"text/xml" ,
            ".vsmdi":"application/xml" ,
            ".vspscc":"text/plain" ,
            ".vss":"application/vnd.visio" ,
            ".vsscc":"text/plain" ,
            ".vssettings":"text/xml" ,
            ".vssscc":"text/plain" ,
            ".vst":"application/vnd.visio" ,
            ".vstemplate":"text/xml" ,
            ".vsto":"application/x-ms-vsto" ,
            ".vsw":"application/vnd.visio" ,
            ".vsx":"application/vnd.visio" ,
            ".vtx":"application/vnd.visio" ,
            ".wav":"audio/wav" ,
            ".wave":"audio/wav" ,
            ".wax":"audio/x-ms-wax" ,
            ".wbk":"application/msword" ,
            ".wbmp":"image/vnd.wap.wbmp" ,
            ".wcm":"application/vnd.ms-works" ,
            ".wdb":"application/vnd.ms-works" ,
            ".wdp":"image/vnd.ms-photo" ,
            ".webarchive":"application/x-safari-webarchive" ,
            ".webtest":"application/xml" ,
            ".wiq":"application/xml" ,
            ".wiz":"application/msword" ,
            ".wks":"application/vnd.ms-works" ,
            ".WLMP":"application/wlmoviemaker" ,
            ".wlpginstall":"application/x-wlpg-detect" ,
            ".wlpginstall3":"application/x-wlpg3-detect" ,
            ".wm":"video/x-ms-wm" ,
            ".wma":"audio/x-ms-wma" ,
            ".wmd":"application/x-ms-wmd" ,
            ".wmf":"application/x-msmetafile" ,
            ".wml":"text/vnd.wap.wml" ,
            ".wmlc":"application/vnd.wap.wmlc" ,
            ".wmls":"text/vnd.wap.wmlscript" ,
            ".wmlsc":"application/vnd.wap.wmlscriptc" ,
            ".wmp":"video/x-ms-wmp" ,
            ".wmv":"video/x-ms-wmv" ,
            ".wmx":"video/x-ms-wmx" ,
            ".wmz":"application/x-ms-wmz" ,
            ".wpl":"application/vnd.ms-wpl" ,
            ".wps":"application/vnd.ms-works" ,
            ".wri":"application/x-mswrite" ,
            ".wrl":"x-world/x-vrml" ,
            ".wrz":"x-world/x-vrml" ,
            ".wsc":"text/scriptlet" ,
            ".wsdl":"text/xml" ,
            ".wvx":"video/x-ms-wvx" ,
            ".x":"application/directx" ,
            ".xaf":"x-world/x-vrml" ,
            ".xaml":"application/xaml+xml" ,
            ".xap":"application/x-silverlight-app" ,
            ".xbap":"application/x-ms-xbap" ,
            ".xbm":"image/x-xbitmap" ,
            ".xdr":"text/plain" ,
            ".xht":"application/xhtml+xml" ,
            ".xhtml":"application/xhtml+xml" ,
            ".xla":"application/vnd.ms-excel" ,
            ".xlam":"application/vnd.ms-excel.addin.macroEnabled.12" ,
            ".xlc":"application/vnd.ms-excel" ,
            ".xld":"application/vnd.ms-excel" ,
            ".xlk":"application/vnd.ms-excel" ,
            ".xll":"application/vnd.ms-excel" ,
            ".xlm":"application/vnd.ms-excel" ,
            ".xls":"application/vnd.ms-excel" ,
            ".xlsb":"application/vnd.ms-excel.sheet.binary.macroEnabled.12" ,
            ".xlsm":"application/vnd.ms-excel.sheet.macroEnabled.12" ,
            ".xlsx":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ,
            ".xlt":"application/vnd.ms-excel" ,
            ".xltm":"application/vnd.ms-excel.template.macroEnabled.12" ,
            ".xltx":"application/vnd.openxmlformats-officedocument.spreadsheetml.template" ,
            ".xlw":"application/vnd.ms-excel" ,
            ".xml":"text/xml" ,
            ".xmta":"application/xml" ,
            ".xof":"x-world/x-vrml" ,
            ".XOML":"text/plain" ,
            ".xpm":"image/x-xpixmap" ,
            ".xps":"application/vnd.ms-xpsdocument" ,
            ".xrm-ms":"text/xml" ,
            ".xsc":"application/xml" ,
            ".xsd":"text/xml" ,
            ".xsf":"text/xml" ,
            ".xsl":"text/xml" ,
            ".xslt":"text/xml" ,
            ".xsn":"application/octet-stream" ,
            ".xss":"application/xml" ,
            ".xtp":"application/octet-stream" ,
            ".xwd":"image/x-xwindowdump" ,
            ".z":"application/x-compress" ,
            ".zip":"application/x-zip-compressed"
        }

def login():
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    if not creds or creds.invalid:
        client_id = os.path.join(dirpath,'oauth.json')
        flow = client.flow_from_clientsecrets(client_id,SCOPES)
        flags=tools.argparser.parse_args(args=[])
        creds = tools.run_flow(flow, store,flags) 

def go_back(picker):
	return None, -1

def drive_data(*argv):
	dclipath = os.path.join(dirpath,'.drivecli')
	if not os.path.isfile(dclipath):
			with open(dclipath,'w')as outfile:
				if(not len(argv)):
					data = {}
				else:
					data = argv[0]
				json.dump(data,outfile)
	else:
		if(not len(argv)):
			with open(dclipath, 'r') as infile:
				data = json.load(infile)
		else:
			with open(dclipath,'w') as outfile:
				data = argv[0]
				json.dump(data,outfile)
	return data

def get_request(service,fid,mimeType):
    if(re.match('^application/vnd\.google-apps\..+',mimeType)):
        if(mimeType == 'application/vnd.google-apps.document'):
            mimeTypes={
                "pdf": 'application/pdf',
                "txt":'text/plain',
                "doc":'application/msword',
                "zip":'application/zip',
                "html":'text/html',
                "rtf":"application/rtf",
                "odt":"application/vnd.oasis.opendocument.text"
		    }
        elif(mimeType == 'application/vnd.google-apps.spreadsheet'):
            mimeTypes={
                "pdf": 'application/pdf',
                "xlsx" :'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                "zip":'application/zip',
                "html":'text/html',
                "ods":'application/vnd.oasis.opendocument.spreadsheet',
                "csv":'text/plain',
                "tsv":"text/tab-separated-values" ,
		    }
        elif(mimeType == 'application/vnd.google-apps.presentation'):
            mimeTypes={
                "pdf": 'application/pdf',
                "zip":'application/zip',
                "html":'text/html',
                "pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "plain txt":'text/plain'
		    }
        else:
            mimeTypes={
                "ods":'application/vnd.oasis.opendocument.spreadsheet',
                "csv":'text/plain',
                "tmpl":'text/plain',
                "pdf": 'application/pdf',
                "php":'application/x-httpd-php',
                "jpg":'image/jpeg',
                "png":'image/png',
                "gif":'image/gif',
                "bmp":'image/bmp',
                "txt":'text/plain',
                "doc":'application/msword',
                "js":'text/js',
                "swf":'application/x-shockwave-flash',
                "mp3":'audio/mpeg',
                "zip":'application/zip',
                "rar":'application/rar',
                "tar":'application/tar',
                "arj":'application/arj',
                "cab":'application/cab',
                "html":'text/html',
                "htm":'text/html'
            }
        promptMessage = 'Choose type to export to \n(ENTER to select, s to stop):'
        title = promptMessage
        options = [x for x in mimeTypes.keys()]
        picker = Picker(options, title, indicator = '=>', default_index = 0)
        picker.register_custom_handler(ord('s'),  go_back)
        chosen, index = picker.start()
        if index!=-1:
            request = service.files().export_media(fileId=fid,mimeType=mimeTypes[chosen])
            return request,str("."+chosen)
        else:
            sys.exit(0)
    else:
        request = service.files().get_media(fileId=fid)
        return request,""

def write_needed(dir_name,item,sync_time):
    drive_time = time.mktime(time.strptime(item['modifiedTime'],'%Y-%m-%dT%H:%M:%S.%fZ'))
    local_time = os.path.getmtime(dir_name)
    #print(dir_name)
    #print(time.time(),"||",drive_time,"||",local_time,"||",sync_time)
    sync_time-=float(19800.00)
    local_time-=float(19800.00)
    c_time = time.time()-float(19800.00)
    if(sync_time<drive_time):
        if(sync_time<local_time):
            input=''
            while(input!='s' and input!='o'):
                input = click.prompt("Conflict: both local and online copy of "+dir_name+" has been modified\npress o to OVERWRITE s to SKIP")
            if(input=='o'):
                return True
        else:
            return True
    return False

def push_needed(drive,item_path):
    drive_time = time.mktime(time.strptime(drive['modifiedTime'],'%Y-%m-%dT%H:%M:%S.%fZ'))
    local_time = os.path.getmtime(item_path)-float(19800.00)
    return drive_time<local_time

def modified_or_created(sync_time,item_path):
    mtime = os.path.getmtime(item_path)
    ctime = os.path.getctime(item_path)
    #print(ctime,mtime,sync_time)
    if(ctime>sync_time):
        click.echo("created: "+item_path)
        return 1
    elif(mtime>sync_time):
        click.echo("modified: "+item_path)
        return 1
    return 0

def get_fid(inp):
    if 'drive' in inp:
        if 'open' in link:
            fid = link.split('=')[-1]
        else:
            fid = link.split('/')[-1].split('?')[0]
    else:
        fid = inp
    return inp

def create_new(cwd,fid,exist=False):
    if not exist:
        os.mkdir(cwd)
    data = drive_data()
    data[cwd] = {}
    data[cwd]['id'] = fid
    data[cwd]['time'] = time.time()
    drive_data(data)

def delete_file(fid):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v2', http=creds.authorize(Http()))
    fid = fid['id']
    try:
        service.files().delete(fileId=fid).execute()
    except:
        click.secho("Error Ocurred:\n make sure that you have appropriate access",fg='red')

def get_file(fid):
    data=drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    files = service.files().get(fileId=fid).execute()
    return files

def get_child(cwd):
    # print(fid)
    data=drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    drive_lis = {}
    query = "'"+data[cwd]['id']+"' in parents"
    # print(query) 
    while True:
        children = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id,mimeType,name,modifiedTime)',
                                        pageToken=page_token
                                        ).execute()                                 
        for child in children.get('files', []):
            drive_lis[child['name']] = child
        page_token = children.get('nextPageToken', None)
        if page_token is None:
            break
    return drive_lis

def get_child_id(pid,item):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query = "'"+pid+"' in parents and"
    query += " name = '"+item+"'"
    response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
    fils = response.get('files', [])[0]
    return fils.get('id')

def create_dir(cwd,pid,name):
    file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents':[pid]
        }
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    fid = service.files().create(body=file_metadata,fields='id').execute()
    fid['time']=time.time()
    full_path = os.path.join(cwd,name)
    #print(full_path)
    data = drive_data()
    data[full_path] = fid
    drive_data(data)
    click.secho("Created a tracked directory",fg='magenta')
    return full_path,fid['id']

def file_download(item,cwd,sync_time=time.time()):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    fid = item['id']
    fname = item['name']
    fh = io.BytesIO()
    files = service.files().get(fileId=fid).execute()
    click.echo("Preparing: "+click.style(fname,fg='red')+" for download")
    request,ext= get_request(service,fid,item['mimeType'])
    file_path=(os.path.join(cwd,fname)+ext)
    if((os.path.exists(file_path)) and (not write_needed(file_path,item,sync_time))):
        return
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    with click.progressbar(length=100,label='downloading file') as bar:
        pstatus=0
        while done is False:
            status, done = downloader.next_chunk()
            status=int(status.progress() * 100)
            bar.update(int(status-pstatus))
            pstatus=status
        with open(file_path, 'wb') as f: #add dynamic name
            f.write(fh.getvalue())

def identify_mimetype(name):
    extension = "."+str(name.split('.')[-1])
    if(extension in MIMETYPES.keys()):
        return MIMETYPES[extension]
    else:
        return 'application/octet-stream'

def upload_file(name,path,pid):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    file_mimeType = identify_mimetype(name)
    file_metadata = {   
                        'name':name,
                        'parents':[pid],
                        'mimeType':file_mimeType
                    }
    media = MediaFileUpload(path,mimetype=file_mimeType)
    new_file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    return new_file

def update_file(name,path,fid):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    file_mimeType = identify_mimetype(name)
    media = MediaFileUpload(path,mimetype=file_mimeType)
    new_file = service.files().update(fileId=fid,
                                        media_body=media,
                                        fields='id').execute()
    return new_file

def pull_content(cwd,fid):
    data=drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    lis = []
    query = "'"+data[cwd]['id']+"' in parents" 
    while True:
        children = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id,mimeType,name,modifiedTime)',
                                        pageToken=page_token
                                        ).execute()                                 
        for child in children.get('files', []):
            lis.append(child)
        page_token = children.get('nextPageToken', None)
        if page_token is None:
            break
    for item in lis:
        dir_name = os.path.join(cwd,item['name'])
        if(item['mimeType']!='application/vnd.google-apps.folder'):
            if((not os.path.exists(dir_name)) or write_needed(dir_name,item,data[cwd]['time'])):
                file_download(item,cwd,data[cwd]['time'])
        else:
            if(not os.path.exists(dir_name)):
                click.secho("creating: "+dir_name)
                os.mkdir(dir_name)
                data=drive_data()
                data[dir_name]={'id':item['id'],'time':time.time()}
                data=drive_data(data)
            else:
                click.secho("updating: "+dir_name)
            pull_content(dir_name,item['id'])
    data=drive_data()      
    data[cwd]['time']=time.time()
    data=drive_data(data)
    drive_data(data)

def list_status(cwd,sync_time):
    local_lis = os.listdir(cwd)
    changes = 0
    for item in local_lis:
        item_path = os.path.join(cwd,item)
        if(os.path.isdir(item_path)):
            if(modified_or_created(sync_time,item_path)):
                changes += 1
                data = drive_data()
                if item in data.keys(): 
                    sync_time = data[item]
                else:
                    sync_time = float(0)
                list_status(item_path,sync_time)  
        else:
            changes += modified_or_created(sync_time,item_path)
    if changes == 0:
        click.secho("No changes made since the last sync")

def push_content(cwd,fid):
    drive_lis = get_child(cwd)
    local_lis = os.listdir(cwd)
    data = drive_data()
    sync_time = data[cwd]['time']
    #print(local_lis,"\n",drive_lis.keys())
    for item in local_lis:
        item_path = os.path.join(cwd,item)
        if(os.path.isdir(item_path)):
            if item not in drive_lis.keys():
                child_cwd,child_id = create_dir(cwd,fid,item)
            else:
                child_cwd = os.path.join(cwd,item)
                child_id = drive_lis[item]['id']
                if child_cwd not in data.keys():
                    data[child_cwd] = {'id':child_id,'time':time.time()}
                    data = drive_data(data)
            push_content(child_cwd,child_id)
        else:
            item_path = os.path.join(cwd,item)
            if item not in drive_lis.keys():
                click.secho("uploading "+item)
                upload_file(item,item_path,fid)
            else:
                if(push_needed(drive_lis[item],item_path)):
                    click.secho("updating "+item)
                    fid = get_child_id(fid,item)
                    update_file(item,item_path,fid)
    data = drive_data()
    data[cwd]['time']=time.time()
    drive_data(data)



@click.group()
def cli():
    login()

@cli.command('login',short_help='login to your google account and authenticate the service')
def loggin():
    pass

@cli.command('view-files',short_help='filter search files and file ID for files user has access to')
@click.option('--name',is_flag=bool,help='provide username in whose repos are to be listed.')
@click.option('--types',is_flag=bool,help='provide username in whose repos are to be listed.')
def viewFile(name,types):
    """
    view-files: Filter based list of the names and ids of the first 10 files the user has access to
    """
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query=""
    if name:
        q_name=click.prompt('enter search search value')
        query="name contains '"+q_name+"' "
    if types:
        mimeTypes={
			"xls":'application/vnd.ms-excel',
    		"xlsx" :'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    		"xml" :'text/xml',
    		"ods":'application/vnd.oasis.opendocument.spreadsheet',
    		"csv":'text/plain',
    		"tmpl":'text/plain',
    		"pdf": 'application/pdf',
    		"php":'application/x-httpd-php',
    		"jpg":'image/jpeg',
    		"png":'image/png',
    		"gif":'image/gif',
    		"bmp":'image/bmp',
    		"txt":'text/plain',
    		"doc":'application/msword',
    		"js":'text/js',
    		"swf":'application/x-shockwave-flash',
    		"mp3":'audio/mpeg',
    		"zip":'application/zip',
    		"rar":'application/rar',
    		"tar":'application/tar',
    		"arj":'application/arj',
    		"cab":'application/cab',
    		"html":'text/html',
    		"htm":'text/html',
    		"default":'application/octet-stream',
            "audio":'application/vnd.google-apps.audio',	
            "Google Docs":'application/vnd.google-apps.document',
            "Google Drawing":'application/vnd.google-apps.drawing',
            "Google Drive file":'application/vnd.google-apps.file',	
            "Google Forms":'application/vnd.google-apps.form',	
            "Google Fusion Tables":'application/vnd.google-apps.fusiontable',	
            "Google My Maps":'application/vnd.google-apps.map',	
            "Google Photos":'application/vnd.google-apps.photo',	
            "Google Slides":'application/vnd.google-apps.presentation',	
            "Google Apps Scripts":'application/vnd.google-apps.script',	
            "Google Sites":'application/vnd.google-apps.site',	
            "Google Sheets":'application/vnd.google-apps.spreadsheet',	
            "3rd party shortcut":'application/vnd.google-apps.drive-sdk',	
    		"folder":'application/vnd.google-apps.folder'
		}
        promptMessage = 'Choose a media type to filter \n(press SPACE to mark, ENTER to continue, s to stop):'
        title = promptMessage
        options = [x for x in mimeTypes.keys()]
        picker = Picker(options, title, multi_select=True, min_selection_count=1)
        picker.register_custom_handler(ord('s'),go_back)
        selected = picker.start()
        if type(selected) == list:
            query+="and ("
            for types in selected:
                query+="mimeType='"+mimeTypes[types[0]]+"' or "
            query=query[:-3]
            query+=")"
        if (not name) and types:
            query=query[4:]
    while True:
        response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute() 
        t = PrettyTable(['Name','ID'])                                  
        for fils in response.get('files', []):
            t.add_row([fils.get('name')[:25], fils.get('id')])
        print(t)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
        click.confirm('Do you want to continue?',abort=True)
        click.clear()

@cli.command('clone',short_help='download any file using sharing link or file ID it will be automatically tracked henceforth')
@click.option('--link',help='give sharing link of the file')
@click.option('--id',help='give file id of the file')
def download(link,id):
    '''
    clone: download a file/folder  using either the sharing link or using the file ID  for the file
    '''
    if id != None :
        fid = id
    elif link != None :
        if 'open' in link:
            fid = link.split('=')[-1]
        else:
            fid = link.split('/')[-1].split('?')[0]
    else:
        with click.Context(download) as ctx:
                click.echo(download.get_help(ctx))
        sys.exit(0)
    clone = get_file(fid)
    cwd = os.getcwd()
    if clone['mimeType'] == 'application/vnd.google-apps.folder':
        new_dir = os.path.join(cwd,clone['name'])
        create_new(new_dir,fid)
        pull_content(new_dir,fid)
    else:
        file_download(clone,cwd)

@cli.command('add_remote',short_help='upload any existing file to drive')
@click.option('--file',help='specify the partcular file to uploaded else entire directory is uploaded')
@click.option('--pid',help='specify particular folder id/sharing_link of the folder under which remote must must be added')
def create_remote(file,pid):
    """
    add_remote: create remote equivalent for existing file/folder in local device
    """
    cwd = os.getcwd()
    if pid == None :
        pid = 'root'
    if file != None :
        file_path = os.path.join(cwd,file)
        if os.path.isfile(file_path):
            upload_file(file,file_path,pid)
        else:
            click.secho("No such file exist: "+file_path,fg="red")
            with click.Context(create_remote) as ctx:
                click.echo(create_remote.get_help(ctx))
    else:
        sep = os.sep
        dir_cd,name = sep.join(cwd.split(sep)[:-1]),cwd.split(sep)[-1]
        child_cwd,child_id = create_dir(dir_cd,pid,name)
        push_content(child_cwd,child_id)

@cli.command('rm',short_help='delete a particular file in drive')
@click.option('--file',help='specify the partcular file to deleted else entire directory is deleted')
@click.option('--id',help='delete untracked file directly using id or sharing link, can be used even for unlinked files')
def delete(file,remote,id):
    '''
    rm: delete a particular file/folder from the directory in the remote drive
    '''
    cwd = os.getcwd()
    if id == None:
        if file != None:
            file_path = os.path.join(cwd,file)
            if os.path.isfile(file_path):
                local_dir = get_child(cwd)
                fid = local_dir[file]
            else:
                click.secho("No such file exist: "+file_path,fg="red")
                with click.Context(delete) as ctx:
                    click.echo(delete.get_help(ctx))
            cwd = file_path
        else:
            data = drive_data()
            fid = data[cwd]
            data.pop(cwd,None)
            drive_data(data)
        delete_file(fid)
    else:
        fid = get_fid(id)
        delete_file(fid)

@cli.command('ls',short_help='list out all the files present in this directory in the drive for tracked directories')
def list_out():
    """
    ls: Print files belonging to a folder in the drive folder of the current directory
    """
    data = drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    lis = []
    cwd = os.getcwd()
    if cwd not in data.keys():
        click.secho("following directory has not been added: \nuse drive add_remote ",fg='red')
        sys.exit(0)
    query = "'"+data[cwd]['id']+"' in parents"
    #print(query)
    t = PrettyTable(['Name','File ID','Type'])  
    while True:
        children = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id,mimeType,name)',
                                        pageToken=page_token
                                        ).execute()                                 
        for child in children.get('files', []):
            t.add_row([child.get('name')[:25], child.get('id'),child.get('mimeType')])
        page_token = children.get('nextPageToken', None)
        if page_token is None:
            break
    print(t)

@cli.command('status',short_help='list changes commited since last sync')
def status():
    '''
    status: get a change log of files changed since you had the last sync(push/pull/clone)
    '''
    cwd = os.getcwd()
    data = drive_data()
    if cwd not in data.keys():
        click.secho("following directory has not been added: \nuse drive add_remote ",fg='red')
        sys.exit(0)
    sync_time = data[cwd]['time']
    list_status(cwd,sync_time)

@cli.command('pull',short_help='get latest updates from online drive of the file')
def pull():
    data=drive_data()
    cwd=os.getcwd()
    if cwd not in data.keys():
        click.secho("following directory has not been added: \nuse drive add_remote ",fg='red')
        sys.exit(0)
    fid=data[cwd]['id']
    syn_time=data[cwd]['time']
    pull_content(cwd,fid)

@cli.command('push',short_help='push modification from local files to the drive')
def push():
    '''
    push the latest changes from your local folder that has been added/cloned to google drive.
    '''
    data=drive_data()
    cwd=os.getcwd()
    if cwd not in data.keys():
        click.secho("following directory has not been added: \nuse drive add_remote ",fg='red')
        sys.exit(0)
    fid=data[cwd]['id']
    syn_time=data[cwd]['time']
    push_content(cwd,fid)

@cli.command('logout',short_help='logout from the account')
def destroyToken():
    '''
    logout: logout from the account that has been logged in
    '''
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    if creds:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': creds.access_token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    
    os.remove(token)

if __name__ == '__main__':
    login()