# Part 2 · Half-wave SCR fired at the voltage peak

[Download the English-narrated film](./Thyristor_90deg_Power_Factor_and_Gibbs.mp4) · [Open the dedicated PSCAD workspace](./pscad/Part2_Thyristor_90deg.pswx) · [Return to the diode study](../README.md)

The source is 120 V RMS at 60 Hz and the load is 12 Ω. A thyristor replaces the diode. A ten-degree gate pulse begins 90° after the rising source-voltage zero. The device latches and current flows until the natural zero at 180°. Power quantities below are evaluated at the source terminals.

| Ideal steady-state value | Diode | SCR at 90° |
| --- | ---: | ---: |
| RMS source current | 7.071 A | 5.000 A |
| Active power | 600 W | 300 W |
| Apparent power | 848.528 VA | 600 VA |
| Phase lag of fundamental current | 0° | 32.482° |
| Fundamental reactive power | 0 var | 190.986 var |
| DC current | 4.502 A | 2.251 A |
| Power factor | 0.7071 | 0.5000 |

For a sine voltage reference, the SCR fundamental has a sine coefficient of $\hat I/4$ and a cosine coefficient of $-\hat I/(2\pi)$. Its lag is $\arctan(2/\pi)$, where $\hat I=\sqrt{2}V_{\rm rms}/R$. The displacement factor is 0.8436 and the current distortion factor (including DC) is 0.5927. Their product is 0.5000. The third power-box edge is $D=V_{\rm rms}\sqrt{I_{\rm rms}^2-I_{1,\rm rms}^2}$ and includes DC for this sinusoidal supply.

The Fourier readout uses **cosine-reference phase** and peak amplitude. The fundamental lag quoted above is relative to the source voltage. The spectrum uses RMS magnitudes for AC components and the absolute mean for DC. The zoom at the firing instant shows why increasing the number of terms narrows the Gibbs ringing around the current jump.

## Data provenance

The published film uses the exact ideal switched-current waveform and its Fourier coefficients. The reference dots in the overlay are analytical samples. The PSCAD project uses a finite on-resistance of 1 mΩ, an off-resistance of 100 MΩ, zero forward voltage and no snubber. The gate clock is set for this source's phase and frequency. The independent workspace contains only the new case.

## Reproduce

Use Python 3.11 and the shared [requirements file](../requirements.txt), FFmpeg/FFprobe, LaTeX with dvisvgm, and Windows PowerShell with Microsoft David (US English). Commands below run from this folder.

1. For an ideal-reference film, run `python analyze.py`.
2. For a measured film, open `pscad/Part2_Thyristor_90deg.pswx` in PSCAD 5.1, select `HalfWaveSCR90`, and click **Run**. With the GFortran 8.1 compiler, run `python analyze.py --native pscad/HalfWaveSCR90.gf81`. For another compiler, pass its output directory instead. The script reads the native voltage, current and gate channels, checks the gate and conduction against the positive voltage peak, and exports the six-cycle measurement window.
3. Run `powershell -ExecutionPolicy Bypass -File voice.ps1` and then `python render.py`. The selected data source also determines the overlay legend and narration.
4. Run `python verify.py` to check analytical identities, the Fourier coefficients, the encoded film and its narration timings.
