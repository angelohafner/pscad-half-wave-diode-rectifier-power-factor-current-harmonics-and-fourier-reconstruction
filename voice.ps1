$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot 'assets\voice'
New-Item -ItemType Directory -Force $folder | Out-Null
$token = New-Object -ComObject SAPI.SpObjectToken
$token.SetId('HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\MSTTS_V110_enUS_DavidM')
$voice = New-Object -ComObject SAPI.SpVoice
$voice.Voice = $token

# Each question has a separate clip. The film controls the reveal and its silent observation interval.
$lines = [ordered]@{
intro='One source. One resistor. <silence msec="320"/> Now add <emph>one diode.</emph> Before the traces appear, picture the current. Which half of the wave will get through?'
waves='Follow the turquoise line. It swings both ways. <silence msec="500"/> Now follow the gold. Same peak. Same timing. But the whole negative half is gone! What does that do to power?'
inst='Watch one instant move across all three traces. Voltage times current gives the power right there. <silence msec="400"/> Across the second half, the source voltage swings negative. The current is zero. So the power is zero, too.'
rms='Start with the two meter readings. For voltage, square the samples, integrate over one period, divide by the period, then take the square root. Same recipe for current. <silence msec="350"/> Look at the readings. The voltage stays at one hundred twenty volts. The current changes.'
power='Now multiply voltage and current <emph>at each instant.</emph> Integrate that product over one period and divide by the period. That gives active power, in watts. <silence msec="350"/> Multiply the two meter readings instead, and you get apparent power, in volt-amperes. Can you predict the power factor in each case?'
pf='Divide watts by volt-amperes. On the left, one. On the right? <silence msec="320"/> About six hundred divided by eight hundred forty-eight. That gives <emph>zero point seven zero seven.</emph> Where does that difference come from?'
spectrum='One peak for the resistor. <silence msec="300"/> Add the diode, and look at the spectrum now! A D C level, a fundamental, and even harmonics. Which of them delivers net energy from the source?'
phase='Compare the voltage with the fundamental current. Both traces are scaled to their own peak. <silence msec="380"/> Their peaks line up. So do their zero crossings! Zero phase shift means zero fundamental reactive power.'
product_intro='Take one current component at a time. Multiply by source voltage, then integrate over a cycle and divide by the period. This integral is their inner product. <silence msec="480"/> Watch the colors. Turquoise counts up. Purple counts down.'
product0='First, the D C current. One lobe above zero. One below. <pitch middle="2">What do you think the integral will give?</pitch>'
result0='Exactly zero! Follow the two energy readings. The second lobe takes away everything the first one adds.'
product1='Try the fundamental. Halfway through, both voltage and current change sign. <pitch middle="2">Which way does their product go?</pitch>'
result1='Up again! Both lobes add. This one component accounts for the full six hundred watts of average power drawn from the source.'
product2='Now double the current frequency. Look past the first lobe. <silence msec="380"/> Over the whole cycle, which color wins?'
result2='A tie! The positive and negative areas have the same magnitude. The second harmonic adds current, yet its contribution to active power is zero.'
product4='At four times the frequency, the lobes get smaller and more numerous. <pitch middle="2">Can you predict the result before the numbers appear?</pitch>'
result4='Zero again. Each color covers the same total area. With a sinusoidal source, only the current fundamental transfers net energy over the cycle.'
triangle='Here is the familiar power triangle. Active power runs across, reactive power runs up, and apparent power is the diagonal. <silence msec="320"/> For the direct resistor, the reactive side shrinks to zero.'
box='Watch that triangle open into a box! The new direction represents the D C and higher harmonic currents. <silence msec="460"/> Follow the gold diagonal from one corner to the opposite corner. Its length gives apparent power.'
face='Now use the phase angle we measured. Zero! The reactive side collapses. <silence msec="470"/> But the purple side is still there. That is why the diagonal is longer than the active-power side.'
distortion='Here is the same story in amps. Five amps in the fundamental. Just over seven in total. <silence msec="380"/> Their ratio gives the power factor here. D C counts in total current, even though the usual harmonic distortion measure leaves it out.'
slow='Let us rebuild that current! Start with the D C level. <silence msec="650"/> Add the fundamental. <silence msec="450"/> Now the second harmonic pulls the blocked half down. Watch how little the third changes it.'
fast='Order ten. Ready? <silence msec="300"/> Let us speed up! Look at the corners as the even harmonics fill in.'
end='Compare the gold line with the simulation dots. <silence msec="700"/> After fifty orders, the two currents differ by just over seven milliamps R M S.'
rules='Two different sums. For active power, add the signed integrals, each divided by the period. <silence msec="480"/> For total current, square the R M S components, include D C, add, then take the square root. <silence msec="520"/> And there it is! Extra current raises apparent power, even with the fundamental perfectly in phase.'
}
foreach ($key in $lines.Keys) {
    $stream = New-Object -ComObject SAPI.SpFileStream
    $stream.Format.Type = 22
    $stream.Open((Join-Path $folder ($key + '.wav')), 3, $false)
    try {
        $voice.AudioOutputStream = $stream
        $accent = if ($key -in 'intro','result0','result1','result2','box','fast','rules') { 3 } else { 1 }
        $pace = if ($key -in 'intro','waves','result1','result2','slow','fast') { 2 } else { 1 }
        $xml = "<volume level='98'><pitch middle='$accent'><rate speed='$pace'>" + $lines[$key] + '</rate></pitch></volume>'
        [void]$voice.Speak($xml,8)
    } finally {
        $stream.Close()
    }
}
Write-Output ("Narrator: " + $voice.Voice.GetDescription() + " | Clips: " + $lines.Count)
