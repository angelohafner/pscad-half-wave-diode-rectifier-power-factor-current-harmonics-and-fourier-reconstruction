# Part 6 · Leading and lagging GTO currents at 10 J per cycle

[Watch the English-narrated film](./GTO_Leading_and_Lagging_at_10J.mp4) · [Open the three-case PSCAD workspace](./pscad/Part6_GTO_10J.pswx)

Two antiparallel GTOs feed a 12 Ω resistor from a sinusoidal 120 V RMS, 60 Hz source. The ideal-switch comparison fixes the load energy at 10 J per cycle, or 5 J in each half-cycle. All three cases draw 7.0711 A RMS and deliver 600 W, giving 848.5281 VA and a true power factor of 0.7071.

| Fundamental current | Positive gate window | Negative gate window | RMS fundamental current | Displacement factor | Fundamental reactive power | Current THD |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| In phase | 66.17323°–113.82677° | 246.17323°–293.82677° | 5.0000 A | 1.0000 | 0 VAr | 100.00% |
| Lagging by 30° | 89.44236°–162.24375° | 269.44236°–342.24375° | 5.7735 A | 0.8660 | +346.41 VAr | 70.71% |
| Leading by 30° | 17.75625°–90.55764° | 197.75625°–270.55764° | 5.7735 A | 0.8660 | −346.41 VAr | 70.71% |

Gate angles are measured from the rising voltage zero crossing. With source voltage as the real-axis reference, the tip of the fundamental RMS current phasor moves along the line with real component 5 A. Its imaginary component reaches −2.88675 A for lag and +2.88675 A for lead. A lagging current has positive fundamental reactive power in the passive sign convention. The instantaneous resistor power is nonnegative in every case.

The animation solves the equal-energy constraint throughout the sweep. Independent time-domain quadrature checks the case energies and the complex Fourier coefficients through order 50. The displayed THD includes all higher harmonics. An early window and its reflection about the voltage peak have equal harmonic magnitudes.

## Reproduce

From this directory, with the series Python requirements, Manim, LaTeX, FFmpeg and the Windows US English Mark voice installed, run the commands below. The study and drawing scripts reuse the earlier episodes in this repository.

```powershell
python study6.py
powershell -NoProfile -ExecutionPolicy Bypass -File voice.ps1
python render.py
```

Open the workspace with the three project files in the same folder in PSCAD 5.1. All graphs in the film come from the analytical ideal-switch model. The supplied cases have been checked against the commanded gate angles. Native PSCAD execution was blocked at startup by Windows error 623.
