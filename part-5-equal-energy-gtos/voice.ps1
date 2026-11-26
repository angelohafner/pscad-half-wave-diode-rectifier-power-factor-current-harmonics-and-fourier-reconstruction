$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot 'media\voice'
New-Item -ItemType Directory -Force $folder | Out-Null
$clips = [ordered]@{
    question = "If fundamental reactive power falls from three hundred and eighty-two Volt-Amperes reactive to zero, what happens to the power factor? <silence msec='700'/> Here are two alternating-current controllers, feeding the same resistor. One uses ordinary thyristors, the other uses gate turn-off thyristors. We will give them exactly the same energy budget."
    energy = "Our source is one hundred twenty volts R M S, at sixty hertz. The load is twelve ohms. Ten Joules per cycle means six hundred watts. During conduction the resistor absorbs voltage squared divided by resistance. In the S C R case, firing at ninety degrees delivers five Joules in each half cycle. The shaded area is energy when integrated over time."
    tune = "Start with a sixty-degree G T O conduction window. It extends from sixty to one hundred twenty degrees. That gives twelve point one eight Joules per cycle. <silence msec='450'/> Now move the two edges inward by the same amount. The area shrinks while the center stays at the voltage peak. We stop when each half cycle delivers five Joules."
    solve = "Call the full width of one conduction window w, measured in radians. Integrate the squared sine over that window and include both half cycles. An always-connected resistor would receive twenty Joules per cycle. For exactly half that energy, the width plus its sine must equal pi over two. The solution is forty-seven point six five degrees."
    gates = "The positive gate turns on at sixty-six point one seven degrees, and turns off at one hundred thirteen point eight three. The negative gate repeats the same command half a cycle later. Watch the separate gate signals. At turn-off, almost thirteen amps are still flowing. In this ideal resistive circuit the current falls straight to zero."
    phase = "Now look at the fundamentals. The dashed line marks the source voltage peak. The S C R current fundamental peaks about thirty-two and a half degrees later. The G T O pulse is symmetric about the voltage peak, so its fundamental peaks at exactly ninety degrees. Its reactive power at the fundamental is zero. Where did the remaining nonactive current go?"
    rms = "Both loads absorb six hundred watts. For the same resistor that fixes total R M S current at seven point zero seven amps. The source voltage is sinusoidal, so active power fixes the in-phase fundamental current at five amps in both cases. The S C R also draws quadrature fundamental current. The G T O has none. Its remaining five amps R M S are entirely harmonics."
    fourier = "Build the ideal G T O current with its Fourier series. Start with zero direct current, then add the fundamental. Half-wave antisymmetry cancels every even order. The odd harmonics reshape the sine wave into two short pulses. From order ten we move faster. Near a switching edge the partial sum rings. The dashed reference shows the instantaneous switch model."
    result = "Same energy, same watts, and the same Volt-Amperes. So the true power factor is the same, despite the change in fundamental phase. Current distortion rises from about sixty-five percent to one hundred percent. Unity displacement factor tells us that the fundamental is aligned. The true power factor also counts every Ampere carried by the source."
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
        $pitch = if ($key -in 'question','tune','result') { 3 } else { 1 }
        $xml = "<volume level='98'><pitch middle='$pitch'><rate speed='1'>" + $clips[$key] + '</rate></pitch></volume>'
        [void]$speaker.Speak($xml,8)
    } finally { $stream.Close() }
}
