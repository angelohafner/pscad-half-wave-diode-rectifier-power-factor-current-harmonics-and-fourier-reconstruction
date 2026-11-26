"""Part 5. Narrated comparison of equal-energy SCR and GTO controllers."""
import sys
import wave
from pathlib import Path
import numpy as np
from manim import (
    AnimationGroup, Create, DashedVMobject, DecimalNumber, Dot, FadeIn,
    FadeOut, ImageMobject, Integer, MathTex, Polygon, Rectangle, Scene,
    Text, Transform, ValueTracker, VGroup, always_redraw, config, linear,
)
from study import ROOT, ALPHA, BETA, SCR, GTO, PEAK, WIDTH, coefficients, quantities

# The series shares its chart geometry, type sizes and palette across episodes.
PREVIOUS = ROOT.parent / 'part-4-antiparallel-gtos'
sys.path.insert(0, str(PREVIOUS))
from film import Chart, box, label, left, legend, math, pos, put, seg
from film import BLUE, GOLD, GRID, MINT, MUTED, VIOLET, WHITE_INK

G = quantities(GTO)
S = quantities(SCR)
TICKS = [0, 90, 180, 270, 360]
config.background_color = '#10212d'


def small(text, x, y, color=MUTED, size=21):
    return left(label(text, size, color), x, y)


def placed_tex(text, x, y, size=34, color=WHITE_INK):
    return put(math(text, size, color), x, y)


def switch_curve(chart, angles, color, width=4):
    """Construct each ideal limit at the edge angle, including vertical jumps."""
    x, y = [0.], [0.]
    for start, stop in [angles, (angles[0]+180, angles[1]+180)]:
        samples = np.linspace(start, stop, 120)
        x.extend([start, *samples, stop])
        y.extend([0., *(PEAK*np.sin(np.deg2rad(samples))), 0.])
    x.append(360.)
    y.append(0.)
    return chart.curve(x, y, color, width)


def power(x):
    return 2.4*np.sin(np.deg2rad(x))**2


def shaded_power(chart, a, b, color):
    xx = np.linspace(a, b, 110)
    vertices = [pos(chart.x(a),chart.y(0))]
    vertices.extend(pos(chart.x(v),chart.y(power(v))) for v in xx)
    vertices.append(pos(chart.x(b),chart.y(0)))
    area = Polygon(*vertices, fill_color=color, fill_opacity=.42, stroke_width=0)
    return VGroup(area, chart.curve(xx, power(xx), color, 4),
                  seg(chart.x(a),chart.y(0),chart.x(a),chart.y(power(a)),color,2.5),
                  seg(chart.x(b),chart.y(0),chart.x(b),chart.y(power(b)),color,2.5))


class EqualEnergyFilm(Scene):
    def chapter(self, key, title):
        self.clear()
        with wave.open(str(ROOT/'media'/'voice'/(key+'.wav'))) as clip:
            duration = clip.getnframes()/clip.getframerate()
        self.cues.append((key, len(self.renderer.file_writer.partial_movie_files), duration))
        self.start = self.time
        self.end = self.start + duration + .6
        self.add(small('POWER ELECTRONICS   /   PART 5',-6.40,3.56,MINT,18),
                 left(Text(title,font='Georgia',font_size=40,color=WHITE_INK),-6.40,2.85),
                 seg(-6.40,2.30,6.40,2.30))

    def at(self, seconds):
        delay = self.start + seconds - self.time
        if delay >= 1/24:
            self.wait(delay)

    def finish(self):
        self.at(self.end - self.start)

    def question(self):
        self.chapter('question', 'What happens when 382 VAr disappear?')
        for x, name, source, color in [
            (-3.22,'Antiparallel SCRs',ROOT.parent/'part-3-antiparallel-thyristors/data/antiparallel.png',VIOLET),
            (3.22,'Antiparallel GTOs',PREVIOUS/'data/gto_circuit.png',GOLD)]:
            self.add(box(x,0,6.10,3.77),small(name,x-2.67,1.45,color,26))
            art = ImageMobject(str(source)).scale_to_fit_width(4.25)
            self.play(FadeIn(put(art,x,-.12)),run_time=.65)
        self.play(FadeIn(placed_tex(r'Q_1=382\,\mathrm{VAr}',-3.22,-1.47,31,VIOLET)),
                  FadeIn(placed_tex(r'Q_1=0\,\mathrm{VAr}',3.22,-1.47,31,GOLD)),run_time=.7)
        self.at(8.8)
        self.play(FadeIn(placed_tex(r'E_R=10.00\,\mathrm{J/cycle}\qquad \mathrm{PF}_{\rm SCR}\ \overset{?}{=}\ \mathrm{PF}_{\rm GTO}',0,-2.85,37)),run_time=.7)
        self.add(put(label('Ideal switches   /   sinusoidal source   /   resistive load',19,MUTED),0,-3.55))
        self.finish()

    def energy(self):
        self.chapter('energy','Ten Joules per cycle fixes the average power')
        ch = Chart(-5.7,.85,-2.22,.96,(0,2.6),(0,180))
        x = np.linspace(0,180,241)
        self.add(small('Positive half-cycle  ·  resistor power [kW]',-5.99,1.63,WHITE_INK,23),
                 ch.grid([0,45,90,135,180],[0,1,2]),
                 DashedVMobject(ch.curve(x,power(x),MUTED,2),num_dashes=42))
        self.add(box(3.96,-.19,4.62,3.94),
                 small('Source and load',1.96,1.20,MINT,23),
                 left(math(r'120\,\mathrm{V_{rms}},\quad 60\,\mathrm{Hz}',31),1.96,.53),
                 left(math(r'R=12\,\Omega',32),1.96,-.13))
        self.at(4.0)
        self.play(FadeIn(left(math(r'P=fE_R=600\,\mathrm W',32,GOLD),1.96,-1.17)),run_time=.65)
        self.at(8.0)
        self.play(FadeIn(shaded_power(ch,90,180,VIOLET)),run_time=1.20)
        self.add(small('SCR',ch.x(110),ch.y(.55),WHITE_INK,22))
        self.at(12.5)
        self.play(FadeIn(placed_tex(r'E_{R,+}=\frac{1}{\omega}\int_{\pi/2}^{\pi}\frac{v_s^2}{R}\,d\theta=5.00\,\mathrm{J}',0,-3.15,32)),run_time=.7)
        self.finish()

    def tune(self):
        self.chapter('tune','Narrow the window and keep its center fixed')
        ch = Chart(-5.67,2.86,-2.10,1.20,(0,2.6),(0,180))
        x = np.linspace(0,180,251)
        self.add(small('GTO load power [kW]  ·  positive half-cycle',-5.98,1.76,WHITE_INK,22),
                 ch.grid([0,30,60,90,120,150,180],[0,1,2]),
                 DashedVMobject(ch.curve(x,power(x),MUTED,2.2),num_dashes=55))
        tracker = ValueTracker(60.)
        patch = always_redraw(lambda: shaded_power(ch,90-tracker.get_value()/2,90+tracker.get_value()/2,GOLD))
        self.add(patch,ch.mark(90,WHITE_INK),small('Full window',3.52,.98,MUTED),
                 small('Energy / cycle',3.52,-.68,MUTED))
        def width_read():
            return left(DecimalNumber(tracker.get_value(),num_decimal_places=2,unit=r'^{\circ}',font_size=42,color=GOLD),3.52,.40)
        def energy_read():
            w = np.deg2rad(tracker.get_value())
            return left(DecimalNumber(20*(w+np.sin(w))/np.pi,num_decimal_places=2,unit=r'\,\mathrm{J}',font_size=42,color=MINT),3.52,-1.28)
        self.add(always_redraw(width_read),always_redraw(energy_read))
        self.add(put(label('The negative half-cycle delivers the same energy.',22,MUTED),0,-3.30))
        self.at(7.75)
        self.play(tracker.animate.set_value(float(np.rad2deg(WIDTH))),run_time=4,rate_func=linear)
        self.at(13.3)
        self.play(FadeIn(placed_tex(r'E_{R,+}=5.00\,\mathrm J',-.8,-2.83,30,GOLD)),run_time=.6)
        self.finish()

    def solve(self):
        self.chapter('solve','Solve for the conduction angle')
        self.add(small('One centered window per half-cycle',-6.10,1.74,MINT,24),
                 placed_tex(r'\alpha=\frac{\pi-w}{2},\qquad \beta=\frac{\pi+w}{2}',0,1.05,38))
        self.at(3.45)
        self.play(FadeIn(placed_tex(r'E_R=\frac{2}{\omega}\int_\alpha^\beta \frac{2V_{\rm rms}^2}{R}\sin^2\theta\,d\theta'
                                     r'=\frac{V_{\rm rms}^2}{Rf}\,\frac{w+\sin w}{\pi}',0,-.17,40)),run_time=.8)
        self.at(8.8)
        self.play(FadeIn(placed_tex(r'10\,\mathrm J=20\,\mathrm J\,\frac{w+\sin w}{\pi}'
                                     r'\qquad\Longrightarrow\qquad w+\sin w=\frac{\pi}{2}',0,-1.48,35)),run_time=.7)
        self.at(15.1)
        self.play(FadeIn(placed_tex(r'w\approx 0.831711\ \mathrm{rad}\ \approx 47.65354^\circ',0,-2.85,40,GOLD)),run_time=.65)
        self.finish()

    def gates(self):
        self.chapter('gates','Two gate commands, four switching edges')
        leftx,rightx=-5.18,5.99
        positive = Chart(leftx,rightx,.91,1.63,(-.12,1.2))
        negative = Chart(leftx,rightx,-.08,.65,(-.12,1.2))
        current = Chart(leftx,rightx,-2.23,-.38,(-16,16))
        for name,ch,col in [(r'g_1',positive,GOLD),(r'g_2',negative,MINT),(r'i_s\,[\mathrm A]',current,BLUE)]:
            self.add(ch.grid(TICKS,[0],xticks=ch is current,yticks=False),
                     left(math(name,28,col),-6.41,(ch.t+ch.b)/2))
        self.add(small('Electrical angle from the rising voltage zero crossing',-5.20,1.96,MUTED,18))
        for ch,a,b,col in [(positive,ALPHA,BETA,GOLD),(negative,ALPHA+180,BETA+180,MINT)]:
            self.play(Create(ch.curve([0,a,a,b,b,360],[0,0,1,1,0,0],col,4)),run_time=1.35)
        self.add(placed_tex(r'G_1:\;66.17^\circ\ \to\ 113.83^\circ',-3.14,-3.08,30,GOLD),
                 placed_tex(r'G_2:\;246.17^\circ\ \to\ 293.83^\circ',3.08,-3.08,30,MINT))
        self.at(7.2)
        self.play(Create(switch_curve(current,GTO,BLUE)),run_time=2.65,rate_func=linear)
        self.at(12.7)
        self.add(current.mark(BETA,GOLD),
                 put(Dot(radius=.064,color=GOLD),current.x(BETA),current.y(PEAK*np.sin(np.deg2rad(BETA)))),
                 put(Dot(radius=.064,color=MINT),current.x(BETA),current.y(0)))
        self.play(FadeIn(put(label('At turn-off   12.94 A → 0 A',20,WHITE_INK),0,-3.67)),run_time=.6)
        self.finish()

    def phase(self):
        self.chapter('phase','When does the fundamental reach its peak?')
        x=np.linspace(0,360,401)
        self.add(small('Each current is normalized to its own peak.',-5.33,1.85,MUTED,20),
                 legend(.67,1.86,'Voltage peak at 90°',BLUE))
        for name,bounds,col,b,t in [('SCR',SCR,VIOLET,-.38,1.25),('GTO',GTO,GOLD,-2.43,-.86)]:
            ch=Chart(-5.19,5.91,b,t,(-1.18,1.18))
            lag=quantities(bounds)['lag']
            self.add(left(math(r'i_{1,\mathrm{'+name+r'}}',27,col),-6.36,(b+t)/2),
                     ch.grid(TICKS,[0],xticks=name=='GTO',yticks=False),ch.mark(90,BLUE))
            curve=ch.curve(x,np.sin(np.deg2rad(x-lag)),col,4.3)
            if name=='GTO':
                self.at(7.0)
            self.play(Create(curve),run_time=1.75)
            self.add(put(Dot(radius=.07,color=col),ch.x(90+lag),ch.y(1)),
                     left(label(f'{90+lag:.2f}°',18,col),ch.x(90+lag)+.14,ch.y(1)+.26))

        self.at(12.15)
        self.play(FadeIn(placed_tex(r'\varphi_{1,\rm SCR}=32.48^\circ\qquad \varphi_{1,\rm GTO}=0^\circ',0,-3.42,33)),run_time=.6)
        self.finish()

    def rms(self):
        self.chapter('rms','Where do the remaining Amperes go?')
        self.add(placed_tex(r'I_{\rm rms}^2=I_P^2+I_Q^2+\sum_{h\ge2}I_h^2=50\,\mathrm{A}^2',0,1.64,37),
                 legend(-5.75,.84,'In-phase fundamental',BLUE),
                 legend(-1.65,.84,'Quadrature fundamental',VIOLET),
                 legend(3.10,.84,'Harmonics',GOLD))
        for row,(name,m,y) in enumerate([('SCR',S,-.02),('GTO',G,-1.29)]):
            self.at(4.20 if row==0 else 10.50)
            self.add(small(name,-6.20,y,WHITE_INK,25))
            x=-4.93
            for value,col in [(m['ip'],BLUE),(m['iq'],VIOLET),(m['ih'],GOLD)]:
                length=10.70*value**2/50
                if length<1e-9:
                    continue
                rect=Rectangle(width=length,height=.7,stroke_width=0,fill_color=col,fill_opacity=.88)
                self.play(FadeIn(put(rect,x+length/2,y)),run_time=.26)
                self.add(put(label(f'{value**2:.2f}',22,'#10212d'),x+length/2,y))
                x+=length
        self.add(put(label('Bar sections show mean-square current in A².',20,MUTED),0,-2.37))
        self.at(15.30)
        self.play(FadeIn(placed_tex(r'I_{1,\rm GTO}=5.00\,\mathrm A\qquad I_{H,\rm GTO}=5.00\,\mathrm A'
                                     r'\qquad \mathrm{THD}_I=100\%',0,-3.21,32,GOLD)),run_time=.65)
        self.finish()

    def fourier(self):
        self.chapter('fourier','Build the GTO current one harmonic at a time')
        ch=Chart(-5.54,5.92,-2.19,1.04,(-17.5,17.5))
        self.add(ch.grid(TICKS,[-15,0,15]),small('Source current [A]',-5.95,1.78,WHITE_INK,22),
                 legend(-1.68,1.78,'Ideal switch reference',MUTED),
                 legend(2.46,1.78,'Fourier sum',MINT))
        ref=DashedVMobject(switch_curve(ch,GTO,MUTED,3),num_dashes=105)
        self.add(ref)
        x=np.linspace(0,360,901)
        cs=coefficients(GTO)
        sums=np.cumsum((cs[:,None]*np.exp(1j*np.arange(51)[:,None]*np.deg2rad(x))).real,axis=0)
        trace=ch.curve(x,sums[0],MINT,4)
        self.add(trace,small('Harmonic order',-4.9,-3.13,WHITE_INK,22))
        count=put(Integer(0,font_size=37,color=MINT),-1.99,-3.13)
        self.add(count,placed_tex(r'i_N=\sum_{h=1}^{N}\hat I_h\cos(h\theta+\psi_h)',2.12,-3.10,29))
        self.at(2.1)
        for n in range(1,51):
            if n==10:
                self.at(12.55)
            self.remove(count)
            count=put(Integer(n,font_size=37,color=MINT),-1.99,-3.13)
            self.add(count)
            duration=.88 if n<=9 else .14
            if n%2:
                self.play(Transform(trace,ch.curve(x,sums[n],MINT,4)),run_time=duration)
            else:
                self.wait(duration)
        self.finish()

    def result(self):
        self.chapter('result','Same true power factor, different current spectra')
        self.add(small('Source-side quantities',-5.86,1.74,MUTED,22),
                 put(label('SCR pair',25,VIOLET),1.15,1.74),put(label('GTO pair',25,GOLD),4.57,1.74))
        rows=[('Energy to the resistor','10.00 J/cycle','10.00 J/cycle'),
              ('Active / apparent power','600 W / 848.53 VA','600 W / 848.53 VA'),
              ('True power factor','0.7071','0.7071'),
              ('Fundamental reactive power','381.97 VAr','0 VAr'),
              ('Current THD','65.05%','100.00%')]
        for n,(title,a,b) in enumerate(rows):
            y=1.11-.63*n
            self.at([.6,2.1,4.6,6.7,9.9][n])
            self.add(seg(-5.94,y-.31,5.99,y-.31,GRID,1),
                     small(title,-5.86,y,WHITE_INK,22),
                     put(label(a,22,VIOLET),1.15,y),put(label(b,22,GOLD),4.57,y))
        self.at(13.85)
        self.play(FadeIn(placed_tex(r'\mathrm{PF}=\frac{P}{V_{\rm rms}I_{\rm rms}}'
                                     r'=\frac{I_{1,\rm rms}}{I_{\rm rms}}\cos\varphi_1',0,-2.45,34,MINT)),run_time=.75)
        self.add(put(label('Ideal switches   /   120 V RMS   /   60 Hz   /   12 Ω',19,MUTED),0,-3.50))
        self.finish()

    def construct(self):
        self.cues=[]
        for scene in (self.question,self.energy,self.tune,self.solve,self.gates,self.phase,
                      self.rms,self.fourier,self.result):
            scene()
