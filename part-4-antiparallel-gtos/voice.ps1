$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot 'media\voice'
New-Item -ItemType Directory -Force $folder | Out-Null
$results = Get-Content -Raw (Join-Path $PSScriptRoot 'data\results.json') | ConvertFrom-Json
$clips = [ordered]@{
  intro = "Could a shorter conduction interval deliver more power to the same resistor? <silence msec='450'/> In Part Three, each thyristor conducted for ninety degrees. This time, we replace both devices with gate turn-off thyristors. Each will conduct for just sixty degrees."
  freeze = "The upper device turns on at sixty degrees. The current follows the top of the voltage wave. Freeze the clock a moment before one hundred twenty degrees. <silence msec='450'/> More than twelve amps are still flowing. What happens if we turn the gate command off right here?"
  off = "The current drops to zero! The voltage is still positive, but a gate turn-off thyristor can interrupt forward current. In this ideal resistive circuit, there is no stored magnetic energy to keep it flowing. <silence msec='400'/> Half a cycle later, the lower device repeats the pattern, from two hundred forty to three hundred degrees."
  area = "Here is the positive half cycle. For ideal switches, load power during conduction is voltage squared divided by resistance. The shaded areas show where the resistor gains energy. Both circuits share the middle interval. The G T O adds the high-power shoulder on the left. The S C R keeps the longer, lower-power tail on the right. Which shaded area is larger?"
  energy = "The shorter shoulder wins. The negative half cycle delivers the same energy again, because voltage and current both change sign. The resistor receives ten joules per cycle with the S C Rs and about twelve point one eight with the G T Os. At sixty cycles per second, average power rises from six hundred watts to about seven hundred thirty-one."
  phase = "Now compare the fundamental currents with the source voltage. The S C R fundamental lags by about thirty-two and a half degrees. The G T O windows are centered on both voltage peaks. Its fundamental peaks exactly with the voltage. Fundamental reactive power is zero."
  spectrum = "Half-wave symmetry removes D C and every even harmonic in both circuits. But look at the third harmonic. Changing the conduction window changes its size. With the G T Os, the current fundamental is about six point zero nine amps R M S, while total current is seven point eight zero. Their ratio gives a power factor of point seven eight zero."
  synthesis = "Start with zero D C and add the fundamental. It peaks at ninety degrees. Now add the third harmonic. Watch the broad sine wave become two narrower pulses. Each even order adds zero. Watch what the fifth and seventh harmonics do to the edges."
  fast = "From order ten, the sum speeds up. Follow the leading and trailing edges of each pulse. All four switching events leave a signature in the reconstruction."
  overlay = "The dots are samples from the independent Python switch model. The line is the ideal fifty-order Fourier sum. They agree away from the four switching edges. The small ripples cluster around turn-on and turn-off. The gate controls when the current flows, and that timing controls how much energy reaches the resistor."
}
if ($results.source -eq 'PSCAD') {
  $clips.overlay = 'The dots are current samples recorded in P S cad. The line is the ideal fifty-order Fourier sum. They agree away from the four switching edges. The small ripples cluster around turn-on and turn-off. The gate controls when the current flows, and that timing controls how much energy reaches the resistor.'
}
$token = New-Object -ComObject SAPI.SpObjectToken
$token.SetId('HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\MSTTS_V110_enUS_MarkM')
$speaker = New-Object -ComObject SAPI.SpVoice
$speaker.Voice = $token
foreach ($key in $clips.Keys) {
  $stream = New-Object -ComObject SAPI.SpFileStream
  $stream.Format.Type = 22
  $stream.Open((Join-Path $folder ($key + '.wav')), 3, $false)
  try {
    $speaker.AudioOutputStream = $stream
    $pitch = if ($key -in 'intro','off','energy','fast') { 3 } else { 1 }
    $rate = if ($key -in 'intro','off','fast') { 2 } else { 1 }
    $xml = "<volume level='98'><pitch middle='$pitch'><rate speed='$rate'>" + $clips[$key] + '</rate></pitch></volume>'
    [void]$speaker.Speak($xml,8)
  } finally { $stream.Close() }
}
