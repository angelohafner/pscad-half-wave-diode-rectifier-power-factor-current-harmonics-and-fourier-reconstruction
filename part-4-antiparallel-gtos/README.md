# Part 4 · Gate turn-off and power factor with two antiparallel GTOs

[Download the English-narrated film](./GTO_Gate_Turn_Off_and_Power_Factor.mp4) · [PSCAD workspace](./pscad/Part4_GTO_60_120.pswx) · [PSCAD case](./pscad/AntiParallelGTO.pscx) · [Part 3 SCR case](../part-3-antiparallel-thyristors/README.md)

Can a shorter conduction interval deliver more power? Both circuits use a 120 V RMS, 60 Hz sinusoidal source and a 12 Ω resistor. The Part 3 SCRs conduct from 90° to 180° and from 270° to 360°. The reverse-blocking GTOs conduct from 60° to 120° and from 240° to 300°. The commands are shifted by 180°; both devices block between conduction windows. The model uses logical gate commands of 1 for on and 0 for off. In the positive half-cycle the GTO interrupts 12.25 A at 120° in the ideal circuit. The switching model omits gate-driver dynamics and physical turn-off transients.

## Ideal reference

| Quantity | Part 3 · SCR pair | Part 4 · GTO pair |
| --- | ---: | ---: |
| Conduction per device and cycle | 90° | 60° |
| Energy delivered to the resistor per cycle | 10.00 J | 12.18 J |
| Average load power | 600.0 W | 730.8 W |
| RMS source current | 7.0711 A | 7.8038 A |
| Apparent power | 848.53 VA | 936.46 VA |
| Fundamental current lag | 32.48° | 0° |
| Fundamental reactive power | 381.97 var | 0 var |
| True input power factor | 0.7071 | 0.7804 |

During ideal conduction, $p_R=v_s^2/R$. For each positive half-cycle, both circuits use 90°–120°. The GTO gains 60°–90° (3.045 J) and gives up the SCR tail from 120°–180° (1.955 J). The energy difference repeats in the negative half-cycle. The average load power therefore increases by about 130.8 W.

For the GTO case, $k=(2/\pi)\int_{\pi/3}^{2\pi/3}\sin^2\theta\,d\theta=1/3+\sqrt{3}/(2\pi)$. It follows that $P=(V_{\rm rms}^2/R)k$, $I_{\rm rms}=(V_{\rm rms}/R)\sqrt{k}$ and $\mathrm{PF}=\sqrt{k}$. Half-wave antisymmetry eliminates the DC and even harmonics. Symmetry about each voltage peak also places the fundamental current in phase with the source voltage. The Fourier animation starts at DC, visits every order through 50, and speeds up at order 10. Amplitudes are peak values in the reconstruction and RMS values in the spectrum. The displayed phase uses a cosine reference.

## Published data and reproduction

The published GTO current samples come from the independent Python time-domain switch model. The Part 3 SCR current and fundamental come from its archived Python switch-model results. The two models include 1 mΩ on-resistance and 100 MΩ off-resistance. Six complete steady-state cycles determine the numerical readings. The [results file](./data/results.json) distinguishes source active power from resistor dissipation. The energy comparison in the film uses ideal switches. A native PSCAD recording for the GTO pair is pending.

1. In PSCAD 5.1, open `pscad/Part4_GTO_60_120.pswx`. Keep it together with `AntiParallelGTO.pscx` and run **AntiParallelGTO**. Each master-library `peswitch` is set to GTO, with the integer control input and no snubber. The case saves source voltage, source current and both gate commands. [PSCAD GTO gate semantics](https://www.pscad.com/webhelp/Master_Library_Models/HVDC_and_FACTS/PE_Switch/GTO_IGBT.htm)
2. Run `python study.py` for the numerical reference. To use a PSCAD recording instead, run `python study.py --native pscad/AntiParallelGTO.gf81`. Change the directory suffix to match your compiler. Acquisition checks both gate and current edges at all four angles and saves the native record. The overlay legend and narration identify the data source automatically.
3. From this directory, run `powershell -NoProfile -ExecutionPolicy Bypass -File voice.ps1`, then `python render.py`. Use the [series requirements](../requirements.txt), FFmpeg/FFprobe, LaTeX with dvisvgm, and Windows with the US English Mark voice.
4. Run `python verify.py` to check circuit wiring, switching angles, ideal energy, Fourier coefficients against a separate FFT, and the encoded video and narration. Use `--electrical-only` for the electrical checks alone.
