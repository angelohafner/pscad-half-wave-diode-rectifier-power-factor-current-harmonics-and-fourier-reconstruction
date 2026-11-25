$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot 'media\voice'
New-Item -ItemType Directory -Force $folder | Out-Null
$native = (Get-Content -Raw (Join-Path $PSScriptRoot 'data\study.json') | ConvertFrom-Json).native
$token = New-Object -ComObject SAPI.SpObjectToken
$token.SetId('HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\MSTTS_V110_enUS_DavidM')
$voice = New-Object -ComObject SAPI.SpVoice
$voice.Voice = $token
$lines = [ordered]@{
intro='Same source. Same resistor. This time, we replace the diode with a thyristor. <silence msec="360"/> The gate will fire at the positive voltage peak. Here is the question: how far will the fundamental current lag behind the voltage?'
freeze='Start at the rising voltage zero. The diode would already conduct. Our thyristor waits. <silence msec="450"/> Freeze the circuit just before ninety degrees. The voltage is at its peak. What is the current right now?'
fire='Zero! Now send a short gate pulse. <silence msec="400"/> The current jumps to about fourteen amps. Watch what happens when the pulse ends. The thyristor stays on! Current follows the voltage down, then turns off naturally at the next zero crossing.'
phase='Look at the dotted guides. The voltage peaks at ninety degrees. The fundamental current peaks about thirty-two and a half degrees later. <silence msec="600"/> A ninety-degree firing delay and a thirty-two-degree fundamental phase shift describe two different events.'
power='The source still supplies one hundred twenty volts R M S. The current is five amps, so apparent power is six hundred volt-amperes. <silence msec="350"/> Integrate voltage times current over one cycle. You get three hundred watts. The input power factor is one half.'
box='In the diode case, the fundamental reactive power was zero. Now watch the blue edge grow. Its length is about one hundred ninety-one vars. <silence msec="480"/> The purple edge counts D C and higher harmonics. Both effects contribute to the six hundred volt-ampere diagonal, even though the load is a resistor.'
spectrum='Look at the third and fifth harmonics. With the diode, they vanish. Firing late changes the symmetry, and both appear. The D C level falls to about two and a quarter amps. Can you already see where the sharper edge in the waveform comes from?'
slow='Build the current one term at a time. First the D C level. <silence msec="600"/> Add the fundamental with its phase shift. Now the second harmonic. Watch the third and fourth bend the leading edge.'
fast='At order ten we speed up. Watch the curve as each new term joins the sum. Look closely at the firing instant.'
overlay='Compare the reference dots with the gold line. They agree along the smooth part. But near ninety degrees, the gold line overshoots. Let us zoom in.'
gibbs='At the jump, the Fourier series approaches the midpoint between zero and the peak current. Adding harmonics squeezes the ringing into a narrower region. The maximum overshoot approaches about nine percent of the jump. <silence msec="480"/> That is the Gibbs phenomenon.'
}
if ($native) { $lines.overlay='The dots are current samples from P S cad. Compare them with the gold fifty-order sum. The smooth portion matches closely. But near ninety degrees the sum overshoots. Let us zoom in.' }
else { $lines.overlay='The dots are samples of the ideal switched-current reference. Compare them with the gold fifty-order sum. The smooth portion matches closely. But near ninety degrees the sum overshoots. Let us zoom in.' }
foreach ($key in $lines.Keys) {
    $stream = New-Object -ComObject SAPI.SpFileStream
    $stream.Format.Type = 22
    $stream.Open((Join-Path $folder ($key + '.wav')), 3, $false)
    try {
        $voice.AudioOutputStream = $stream
        $pitch = if ($key -in 'intro','fire','box','fast','gibbs') { 3 } else { 1 }
        $pace = if ($key -in 'fire','intro','fast') { 2 } else { 1 }
        $xml = "<volume level='98'><pitch middle='$pitch'><rate speed='$pace'>" + $lines[$key] + '</rate></pitch></volume>'
        [void]$voice.Speak($xml,8)
    } finally { $stream.Close() }
}
