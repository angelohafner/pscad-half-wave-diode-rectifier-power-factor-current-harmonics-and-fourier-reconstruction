# Half-wave diode rectifier power factor, current harmonics and Fourier reconstruction in PSCAD

How can the input power factor fall to 0.707 when the fundamental current is in phase with the source voltage? This project compares a 12 Ω resistor on a 120 V RMS, 60 Hz sinusoidal source with the same resistor fed through a single diode without a filter capacitor. Both cases run in one dedicated PSCAD 5.1 workspace.

[Watch or download the English-narrated film (MP4, 5 min 23 s, 1080p)](./Half_Wave_Power_Factor.mp4) · [Download the two PSCAD models and workspace (ZIP)](./Half_Wave_Rectifier_PSCAD.zip)

[Part 2: Thyristor firing at 90 degrees, fundamental phase lag and Gibbs ringing](./part-2-thyristor/README.md)

[Part 3: Two antiparallel thyristors, half-wave symmetry and equal power factors](./part-3-antiparallel-thyristors/README.md)

[Part 4: Two antiparallel GTOs, gate turn-off at 120 degrees and load energy](./part-4-antiparallel-gtos/README.md)

## Measured at the source

| Circuit | RMS voltage | RMS current | Active power | Apparent power | Power factor |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct resistor | 120.0 V | 10.000 A | 1,200.00 W | 1,200.00 VA | 1.0000 |
| Half-wave rectifier | 120.0 V | 7.070 A | 599.95 W | 848.46 VA | 0.7071 |

The rectifier's fundamental current is in phase with the voltage. Its DC and higher-order components increase total RMS current. Under a sinusoidal source, only the fundamental current contributes to the cycle integral for active power. The diode model approximates an ideal switch using 1 mΩ on-resistance, 100 MΩ off-resistance, zero forward drop and no snubber.

The animation shows the signed energy areas for the DC, fundamental, second and fourth current components, extends the power triangle to include current distortion, and reconstructs the current through harmonic order 50. The final comparison with the PSCAD trace gives an RMS current error of 7.1 mA.

## Open the simulation

Open [Half_Wave_Rectifier.pswx](./pscad/Half_Wave_Rectifier.pswx) in PSCAD 5.1 and run **DirectResistor** and **HalfWaveDiode**. Keep the workspace file and both project files in the same folder. Each case records source voltage in volts and source current in amperes. The repository also includes the native measurement files from both runs.

## Reproduce the analysis and film

The project was rendered on Windows with Python 3.11, Manim Community, Schemdraw, FFmpeg, FFprobe and a LaTeX installation with dvisvgm. The supplied English WAV clips can be used directly. To regenerate the narration, run `voice.ps1` in Windows PowerShell with the Microsoft David English (US) OneCore voice installed.

From the repository root in PowerShell, install the Python dependencies and process the recorded waveforms:

```powershell
python -m pip install -r requirements.txt
python prepare.py
```

To regenerate the native measurements with PSCAD, install `mhi-pscad==3.1.2` and run `python run_pscad.py` in a licensed PSCAD environment before running `prepare.py`. The analysis uses six complete cycles and aligns the Fourier phases to the rising voltage zero crossing.

To render and check the film using the included audio:

```powershell
python -u work/render_film.py | Out-File -Encoding utf8 work/integral_final.log
python work/attach_narration.py
python work/check_film.py
```

Use a fresh clone to reproduce the published results. Rendering writes `Half_Wave_Power_Factor.mp4` in the repository root. The supplied cue timings also let you run `python work/check_film.py` on the published video.

## Project files

| Path | Contents |
| --- | --- |
| `pscad/` | Dedicated workspace, editable native cases and recorded EMTDC channel data |
| `prepare.py`, `assets/data.json` | Measurement processing, phase-aligned Fourier coefficients and numerical results |
| `film.py`, `assets/*.png` | Manim scenes and Schemdraw circuit diagrams |
| `voice.ps1`, `assets/voice/` | English narration script and 25 audio clips |
| `work/` | Render, narration alignment and verification scripts, plus the published cue timings |
