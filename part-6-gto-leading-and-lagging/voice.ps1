$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot 'media\voice'
New-Item -ItemType Directory -Force $folder | Out-Null
$clips = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'narration.json') | ConvertFrom-Json
$token = New-Object -ComObject SAPI.SpObjectToken
$token.SetId('HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\MSTTS_V110_enUS_MarkM')
$speaker = New-Object -ComObject SAPI.SpVoice
$speaker.Voice = $token
foreach ($property in $clips.PSObject.Properties) {
    $key = $property.Name
    $stream = New-Object -ComObject SAPI.SpFileStream
    $stream.Format.Type = 22
    $stream.Open((Join-Path $folder ($key + '.wav')), 3, $false)
    try {
        $speaker.AudioOutputStream = $stream
        $pitch = if ($key -in 'question','lag','lead','result') { 3 } else { 1 }
        $xml = "<volume level='98'><pitch middle='$pitch'><rate speed='1'>" + $property.Value + '</rate></pitch></volume>'
        [void]$speaker.Speak($xml,8)
    } finally { $stream.Close() }
}
