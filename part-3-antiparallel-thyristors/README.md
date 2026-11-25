# Part 3 · Two antiparallel thyristors at 90°

[Watch or download the narrated film](./Antiparallel_Thyristors_Same_Power_Factor.mp4) · [Dedicated PSCAD workspace](./pscad/Part3_Antiparallel_90deg.pswx) · [PSCAD case](./pscad/AntiParallelSCR90.pscx)

How can two circuits take the same watts and volt-amperes from a sinusoidal source while drawing such different currents? This film compares the Part 1 diode with an AC voltage controller made from two antiparallel thyristors. Both circuits use a 120 V RMS, 60 Hz source and a 12 Ω resistor. The upper device fires at 90° and the lower device at 270°, measured from the rising source-voltage zero. Each gate pulse lasts 10°. Conduction continues to the next natural current zero.

| Source-port quantity | Part 1 diode | Part 3 antiparallel pair |
| --- | ---: | ---: |
| Active power | 599.95 W | 599.95 W |
| Apparent power | 848.46 VA | 848.46 VA |
| RMS line current | 7.0705 A | 7.0705 A |
| DC line current | 4.5012 A | 0 A |
| Fundamental current lag | 0° | 32.48° |
| Displacement factor | 1.0000 | 0.8436 |
| Current distortion factor, including DC | 0.7071 | 0.8382 |
| True power factor | 0.7071 | 0.7071 |

For the symmetric controller, shifting the single-SCR pulse by half a cycle and subtracting it creates the negative current pulse. The result obeys $i(t+T/2)=-i(t)$. The DC and even-order coefficients cancel. Each odd coefficient is twice its value for the Part 2 single-SCR circuit. Under a sinusoidal supply the product of the displacement factor and $I_{1,\mathrm{rms}}/I_{\mathrm{rms}}$ gives the true input power factor. The current ratio includes DC in its denominator.

## Data used in the published film

The diode values and waveform come from the [Part 1 PSCAD recording](../pscad/HalfWaveDiode.gf81). The antiparallel case uses an independently computed Python time-domain circuit model. Each SCR latches when it receives a forward-biased gate pulse, turns off at current zero and uses the same 1 mΩ / 100 MΩ on/off resistances as the PSCAD project. At every time step the load and switch conductances determine the source current. Six steady-state cycles determine the reported powers and Fourier fundamental. The native Part 3 PSCAD run is pending.

The Fourier animation starts with DC, visits every order from 1 to 50, and speeds up at order 10. The readout displays peak amplitude and cosine-reference phase. A dash denotes undefined phase for a zero-amplitude term. The final sum overlays independent time-domain samples. Order 49 is the last term that changes the curve. The final two panels compare the measured diode and the modeled antiparallel circuit.

## Reproduce

Use Python 3.11 with the [project requirements](../requirements.txt), FFmpeg/FFprobe, LaTeX with dvisvgm, and Windows PowerShell with the US English Mark voice. Run commands in this folder.

1. Run `python study.py` to process the archived diode recording, solve the antiparallel circuit, and prepare the Schemdraw schematic and Fourier coefficients.
2. To use native PSCAD samples for the pair, open `pscad/Part3_Antiparallel_90deg.pswx` and run `AntiParallelSCR90`. Keep the workspace and case files together. Run `python study.py --native pscad/AntiParallelSCR90.gf81` (substitute your compiler's build directory). The script checks the two gate times, current turn-on in both directions, recording units, and the six-cycle measurement interval. The label and narration for the overlay then switch to PSCAD.
3. Run `powershell -NoProfile -ExecutionPolicy Bypass -File voice.ps1` followed by `python render.py` for the English-narrated 1080p video.
4. Run `python verify.py` to check circuit topology, compare the analytical coefficients against an independent FFT through order 50, and decode and verify the audio and video. Use `--electrical-only` to skip the media check.

[Part 1 · Diode](../README.md) · [Part 2 · Single thyristor](../part-2-thyristor/README.md)
