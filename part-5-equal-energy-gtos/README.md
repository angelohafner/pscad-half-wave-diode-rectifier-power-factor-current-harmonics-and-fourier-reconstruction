# Part 5 · Equal energy with antiparallel SCRs and GTOs

[Watch the English-narrated film](./Equal_Energy_GTO_and_SCR.mp4) · [PSCAD workspace](./pscad/Part5_Equal_Energy.pswx) · [PSCAD case](./pscad/EqualEnergyGTO.pscx)

Both controllers deliver 10 J per cycle to a 12 Ω load on a 120 V RMS, 60 Hz sine source with ideal switches. The SCRs fire at 90° and 270°. The positive GTO conducts from 66.17323° to 113.82677°, and the negative GTO from 246.17323° to 293.82677°. For a full window width \(w\) in radians, \(E_R=(V_{\rm rms}^2/Rf)(w+\sin w)/\pi\).

| Ideal quantity | SCR | GTO |
| --- | ---: | ---: |
| Source active power | 600 W | 600 W |
| RMS current | 7.0711 A | 7.0711 A |
| Fundamental RMS current | 5.9272 A | 5.0000 A |
| Fundamental lag | 32.48° | 0° |
| Fundamental reactive power | 381.97 VAr | 0 VAr |
| Harmonic RMS current, all orders | 3.8559 A | 5.0000 A |
| Current THD | 65.05% | 100.00% |
| True power factor | 0.7071 | 0.7071 |

The plots use analytical waveforms. Independent numerical integration checks cycle energy and Fourier coefficients through order 50. THD uses the full harmonic RMS from mean-square current. The 50th-order reconstruction illustrates convergence at the switching edges.

The PSCAD 5.1 case uses the specified gate angles. The film uses the analytical waveforms.

## Reproduce

Use the Python dependencies, LaTeX and FFmpeg/FFprobe from the series repository. Run the following from this directory on Windows with the US English Mark voice installed. The animation reuses the Schemdraw figures and chart styles from Parts 3 and 4.

```powershell
python study.py
powershell -NoProfile -ExecutionPolicy Bypass -File voice.ps1
python render.py
```
