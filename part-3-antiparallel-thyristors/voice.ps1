$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot 'media\voice'
New-Item -ItemType Directory -Force $folder | Out-Null
$results = Get-Content -Raw (Join-Path $PSScriptRoot 'data\results.json') | ConvertFrom-Json
$clips = [ordered]@{
    intro = "Here is a puzzle. Can two circuits draw the same watts and have the same power factor, while their current waveforms look completely different? <silence msec='550'/> Let's add a second thyristor, facing the other way. Keep the same source and the same resistor."
    positive = "Start at the rising voltage zero. The upper device fires at ninety degrees. Current jumps to the positive peak, follows the voltage down, and reaches zero at one hundred eighty degrees. <silence msec='500'/> Now watch the negative half cycle. What will the second gate change?"
    negative = "At two hundred seventy degrees, the lower thyristor fires. Current jumps in the opposite direction. It continues after the short gate pulse ends and turns off at the next current zero. Both devices fire ninety degrees into their own half cycle."
    symmetry = "Take the positive current pulse, shift it by half a cycle, and reverse its sign. There is the second pulse! The two signed areas cancel, so the average current is zero. <silence msec='500'/> What else disappears when you add the pulses?"
    spectrum = "Follow order two. A half-cycle shift gives a second harmonic one full turn. Reversing the sign then cancels it. At order three, the shift gives one and a half turns. The sign reversal brings the two contributions back together. Every even order cancels. Every odd order doubles relative to the single thyristor."
    synthesis = "Start the Fourier sum at zero D C. Add the fundamental. <silence msec='350'/> Here comes order two. Does the curve move? <silence msec='500'/> Now add the third. The waveform changes. Follow the next few orders and look for that same pattern."
    fast = "From order ten, the counter speeds up. Only the odd terms change the waveform. Watch the two sharp firing edges take shape."
    overlay = "The dots come from an independent switched-circuit simulation in Python. The line uses the ideal Fourier series through order fifty. Notice the ringing near both firing instants. The fiftieth order is even, so the last change came at forty-nine."
    power = "Look at the diode and the two thyristors side by side. Each draws about seven point zero seven amps R M S. Both deliver six hundred watts to the resistor. The source supplies about eight hundred forty-eight and a half volt-amperes in each case. Dividing watts by volt-amperes gives the same power factor."
    finish = "Now compare their fundamentals. The diode current fundamental is in phase with the source voltage. With two thyristors, it lags by thirty-two and a half degrees. A larger fraction of the total current now lies in the fundamental. Multiply the two factors in each column. Both products give point seven zero seven."
}
if ($results.source -eq 'PSCAD') {
    $clips.overlay = 'The dots are current samples from P S cad. The line uses the ideal Fourier series through order fifty. Notice the ringing near both firing instants. The fiftieth order is even, so the last change came at forty-nine.'
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
        $pitch = if ($key -in 'intro','negative','synthesis','fast') { 3 } else { 1 }
        $speed = if ($key -in 'intro','fast','negative') { 2 } else { 1 }
        $xml = "<volume level='98'><pitch middle='$pitch'><rate speed='$speed'>" + $clips[$key] + '</rate></pitch></volume>'
        [void]$speaker.Speak($xml, 8)
    } finally { $stream.Close() }
}
