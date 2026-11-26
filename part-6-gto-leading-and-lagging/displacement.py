"""Narrated Part 6 animation of equal-energy GTO gate windows and current phasors."""
import wave

import numpy as np
from manim import (
    Arrow, Create, DashedLine, DashedVMobject, DecimalNumber, Dot, FadeIn,
    FadeOut, ImageMobject, Integer, Rectangle, Scene, Text, Transform,
    UpdateFromAlphaFunc, VGroup, config, linear,
)

from study6 import ROOT, PART5, CASES, VALUES, bounds, coefficients, quantities
from equal_energy import (
    BLUE, GOLD, GRID, MINT, MUTED, VIOLET, WHITE_INK, Chart, box, label,
    left, legend, math, placed_tex, pos, power, put, seg, shaded_power, small, switch_curve,
)

config.background_color = '#10212d'
COLORS = {'unity': MINT, 'lag': GOLD, 'lead': VIOLET}
NAMES = {'unity': 'In phase', 'lag': '30° lagging', 'lead': '30° leading'}
TICKS = [0, 90, 180, 270, 360]


def number(value, x, y, digits=2, color=WHITE_INK, size=33, signed=False):
    if abs(value)<.5*10**(-digits):
        value=0.0
    return put(DecimalNumber(value,num_decimal_places=digits,include_sign=signed,
                             group_with_commas=False,font_size=size,color=color),x,y)


class DisplacementFilm(Scene):
    def heading(self,title):
        self.clear()
        header=Text(title,font='Georgia',font_size=40,color=WHITE_INK)
        if header.width>12.70:
            header.scale_to_fit_width(12.70)
        self.add(small('POWER ELECTRONICS   /   PART 6',-6.40,3.55,MINT,18),
                 left(header,-6.40,2.85),seg(-6.40,2.30,6.40,2.30))

    def cue(self,name):
        with wave.open(str(ROOT/'media'/'voice'/(name+'.wav'))) as wav:
            duration=wav.getnframes()/wav.getframerate()
        self.cues.append((name,len(self.renderer.file_writer.partial_movie_files),duration))
        self.start=self.time
        self.narration_seconds=duration

    def at(self,offset):
        delay=self.start+offset-self.time
        if delay>=1/24:
            self.wait(delay)

    def finish(self):
        self.at(self.narration_seconds+.65)

    def intro(self):
        self.heading('Can a resistor draw a leading fundamental current?')
        self.cue('question')
        self.add(box(-3.10,-.08,6.34,3.86),small('Antiparallel GTOs',-5.94,1.47,MINT,25))
        image=ImageMobject(str(PART5.parent/'part-4-antiparallel-gtos/data/gto_circuit.png'))
        self.play(FadeIn(put(image.scale_to_fit_width(4.79),-3.10,-.33)),run_time=.8)
        self.add(small('Sinusoidal source',.68,1.32,BLUE,24),
                 left(math(r'V_s=120\,\mathrm{V_{rms}},\quad f=60\,\mathrm{Hz}',33),.68,.64),
                 left(math(r'R=12\,\Omega',34),.68,-.12))
        self.at(7.0)
        self.play(FadeIn(left(math(r'E_R=10.00\,\mathrm{J/cycle}',39,GOLD),.68,-1.06)),run_time=.7)
        self.at(11.)
        for x,key in [(-4.16,'lead'),(0,'unity'),(4.16,'lag')]:
            self.add(put(label(NAMES[key],26,COLORS[key]),x,-2.61))
        self.add(put(label('Ideal switches   /   source voltage as the phase reference',19,MUTED),0,-3.55))
        self.finish()

    def energy(self):
        self.heading('Set the area before choosing the gate angles')
        self.cue('energy')
        ch=Chart(-5.80,.35,-1.85,1.17,(0,2.65),(0,180))
        xx=np.linspace(0,180,301)
        self.add(small('Load power [kW]   ·   positive half-cycle',-6.18,1.78,WHITE_INK,21),
                 ch.grid([0,45,90,135,180],[0,1,2]),
                 DashedVMobject(ch.curve(xx,power(xx),MUTED,2.5),num_dashes=50),
                 small('Energy delivered to the resistor',1.10,1.78,MINT,21))
        a,b=CASES['unity']
        self.play(FadeIn(shaded_power(ch,a,b,MINT)),run_time=.85)
        self.add(placed_tex(r'E_+=\frac{1}{\omega}\int_\alpha^\beta'
                            r'\frac{v_s^2(\theta)}{R}\,d\theta',3.76,.80,35))
        self.at(4.8)
        self.play(FadeIn(placed_tex(r'E_+=5.00\,\mathrm J',3.76,-.43,39,GOLD)),run_time=.6)
        self.at(7.35)
        self.add(placed_tex(r'E_R=2E_+=10.00\,\mathrm J',3.76,-1.47,31))
        self.at(11.1)
        self.add(placed_tex(r'\int_\alpha^\beta \sin^2\theta\,d\theta=\frac{\pi}{4}',0,-2.79,34),
                 put(label('Gate angles in this integral are in radians.',17,MUTED),0,-3.66))
        self.finish()

    def shared_diagram(self):
        self.heading('Move the gate window and watch the current phasor')
        ch=Chart(-5.77,-.62,-1.28,1.05,(0,2.6),(0,180))
        x=np.linspace(0,180,240)
        self.add(small('Load power [kW]',-6.15,1.88,WHITE_INK,23),
                 ch.grid([0,45,90,135,180],[0,1,2]),
                 DashedVMobject(ch.curve(x,power(x),MUTED,2.2),num_dashes=53),
                 ch.mark(90,MUTED),seg(-.03,-2.35,-.03,2.01,GRID,1.3),
                 small('Fundamental current phasor [A RMS]',.34,1.88,WHITE_INK,22))
        ox,oy,scale=1.26,-.18,.55
        tipx=ox+5*scale
        self.add(Arrow(pos(ox-.15,oy),pos(5.92,oy),buff=0,stroke_width=2.1,
                       max_tip_length_to_length_ratio=.046,color=BLUE),
                 seg(ox,-1.98,ox,1.55,GRID,1.8),
                 DashedLine(pos(tipx,-1.98),pos(tipx,1.55),color=MUTED,stroke_width=1.3,dash_length=.075),
                 small('Voltage reference',4.21,oy-.36,BLUE,16),
                 small('+j',ox-.52,1.29,MUTED,18),small('−j',ox-.52,-1.69,MUTED,18),
                 put(label('5 A in phase',18,MUTED),tipx,-2.21))
        for v in (0,5):
            self.add(seg(ox+scale*v,oy-.09,ox+scale*v,oy+.09,BLUE,1.6))
        self.add(small('Gate on / off [°]',-6.02,-1.91,MUTED,18),
                 small('Window width [°]',-2.81,-1.91,MUTED,18))
        for x,heading in [(-4.78,'Energy / cycle [J]'),(-.52,'Fundamental lag [°]'),(3.96,'Reactive power [VAr]')]:
            self.add(box(x,-3.10,3.76,1.03),put(label(heading,18,MUTED),x,-2.87))
        return ch,ox,oy,scale

    def phasor_sweep(self):
        ch,ox,oy,scale=self.shared_diagram()
        def display(a):
            ab=bounds(float(a))
            m=quantities(ab)
            imag=-m['iq']
            ink=COLORS['lag'] if imag<-.01 else COLORS['lead'] if imag>.01 else MINT
            tx,ty=ox+scale*m['ip'],oy+scale*imag
            return VGroup(
                shaded_power(ch,*ab,ink),
                Arrow(pos(ox,oy),pos(tx,ty),buff=0,color=ink,stroke_width=5,
                      max_tip_length_to_length_ratio=.095),
                put(Dot(radius=.053,color=ink),tx,ty),
                number(ab[0],-5.65,-2.23,1,ink,27),put(label('/',21,MUTED),-5.01,-2.23),
                number(ab[1],-4.34,-2.23,1,ink,27),number(ab[1]-ab[0],-1.96,-2.23,2,ink,27),
                number(m['energy'],-4.78,-3.33,2,WHITE_INK,32),
                number(m['lag'],-.52,-3.33,1,ink,32,True),
                number(m['q1'],3.96,-3.33,2,ink,32,True))
        first=CASES['unity'][0]
        self.cue('unity')
        group=display(first)
        self.play(FadeIn(group),run_time=.75)
        self.finish()
        for key,target,run_time in [('lag',CASES['lag'][0],4.1),('lead',CASES['lead'][0],6.0)]:
            self.cue(key)
            self.at(1.6)
            self.play(UpdateFromAlphaFunc(group,lambda mob,t: mob.become(display(first+t*(target-first)))),
                      run_time=run_time,rate_func=linear)
            first=target
            self.finish()

    def gates(self):
        self.heading('Program both gates from one voltage zero crossing')
        self.cue('gates')
        self.add(small('Gate-on intervals  ·  electrical angle [°]',-6.13,1.92,WHITE_INK,23),
                 legend(2.15,1.91,'GTO 1',GOLD),legend(4.37,1.91,'GTO 2',BLUE))
        ch=Chart(-3.95,5.96,-1.67,1.19,(0,1))
        for angle in TICKS:
            self.add(seg(ch.x(angle),-1.69,ch.x(angle),1.15,GRID,1.3),
                     put(label(f'{angle}°',18,MUTED),ch.x(angle),-1.99))
        rows=[('unity',.86),('lag',-.22),('lead',-1.30)]
        for index,(key,y) in enumerate(rows):
            a,b=CASES[key]
            self.at(1+index*2.25)
            self.add(small(NAMES[key],-6.21,y,COLORS[key],22),seg(ch.l,y,ch.r,y,GRID,1.7))
            for shift,col in [(0,GOLD),(180,BLUE)]:
                l,r=ch.x(a+shift),ch.x(b+shift)
                bar=Rectangle(width=r-l,height=.26,stroke_width=0,fill_opacity=.93,fill_color=col)
                self.play(FadeIn(put(bar,(l+r)/2,y)),run_time=.27)
                self.add(put(label(f'{a+shift:.2f}° – {b+shift:.2f}°',17,WHITE_INK),(l+r)/2,y+.37))
        self.at(8.8)
        self.add(placed_tex(r'g_2(\theta)=g_1(\theta-\pi)',0,-2.76,31),
                 put(label('Both gates are low between the two conduction intervals.',19,MUTED),0,-3.51))
        self.finish()

    def mirror(self):
        self.heading('Mirrored pulses have the same harmonic magnitudes')
        self.cue('mirror')
        ch=Chart(-5.72,5.94,-1.89,1.22,(0,6.2),(0,12))
        self.add(small('Harmonic current [A RMS]',-6.12,1.89,WHITE_INK,21))
        for x,key in [(-1.88,'unity'),(.47,'lag'),(3.35,'lead')]:
            self.add(legend(x,1.88,NAMES[key],COLORS[key]))
        self.add(ch.grid([1,3,5,7,9,11],[0,2,4,6],degrees=False))
        for k,key in enumerate(('unity','lag','lead')):
            self.at(1+k*1.3)
            bars=VGroup()
            for order in [1,3,5,7,9,11]:
                amps=abs(coefficients(CASES[key],order)[order])/np.sqrt(2)
                height=ch.y(amps)-ch.y(0)
                rect=Rectangle(width=.18,height=height,stroke_width=0,fill_color=COLORS[key],fill_opacity=1)
                bars.add(put(rect,ch.x(order)+(k-1)*.21,ch.y(0)+height/2))
            self.play(FadeIn(bars),run_time=.65)
        self.add(put(label('Harmonic order',18,MUTED),0,-2.56))
        self.at(10.)
        self.play(FadeIn(placed_tex(r'\mathrm{THD}_{I,\rm lead}=\mathrm{THD}_{I,\rm lag}=70.71\%'
                                     r'\qquad \mathrm{THD}_{I,\rm unity}=100\%',0,-3.30,30)),run_time=.7)
        self.finish()

    def fourier(self):
        self.heading('Reconstruct all three currents through order 50')
        self.cue('fourier')
        self.add(small('Source current [A]',-6.11,1.91,WHITE_INK,21),
                 legend(-1.56,1.91,'Ideal switch reference',MUTED),
                 small('Fourier sums in color',2.35,1.91,WHITE_INK,19))
        x=np.linspace(0,360,721)
        synthesis=np.exp(1j*np.arange(51)[:,None]*np.deg2rad(x))
        rows=[]
        for i,key in enumerate(('unity','lag','lead')):
            top=1.49-i*1.36
            ch=Chart(-4.61,5.99,top-1.12,top,(-17,17))
            self.add(ch.grid(TICKS,[0],xticks=i==2,yticks=False),
                     small(NAMES[key],-6.24,top-.54,COLORS[key],20),
                     DashedVMobject(switch_curve(ch,CASES[key],MUTED,2.1),num_dashes=110))
            sums=np.cumsum((coefficients(CASES[key])[:,None]*synthesis).real,axis=0)
            trace=ch.curve(x,sums[0],COLORS[key],3.5)
            self.add(trace)
            rows.append((trace,ch,sums,COLORS[key]))
        self.add(small('Highest harmonic order',-4.84,-3.34,WHITE_INK,20))
        count=put(Integer(0,font_size=32,color=MINT),-1.57,-3.34)
        self.add(count,placed_tex(r'i_N=\sum_{h=1}^{N}\hat I_h\cos(h\theta+\psi_h)',2.10,-3.30,27))
        self.at(2.)
        for n in range(1,51):
            if n==10:
                self.at(10.4)
            self.remove(count)
            count=put(Integer(n,font_size=32,color=MINT),-1.57,-3.34)
            self.add(count)
            duration=.82 if n<10 else .13
            if n%2:
                self.play(*[Transform(trace,ch.curve(x,sums[n],col,3.5)) for trace,ch,sums,col in rows],
                          run_time=duration)
            else:
                self.wait(duration)
        self.finish()

    def result(self):
        self.heading('Three displacements, one true power factor')
        self.cue('result')
        cols=[-.60,2.30,5.09]
        keys=['unity','lag','lead']
        self.add(small('Source and load',-6.07,1.77,MUTED))
        for x,key in zip(cols,keys):
            self.add(put(label(NAMES[key],24,COLORS[key]),x,1.77))
        rows=[('Energy / cycle',lambda m:f"{m['energy']:.2f} J"),
              ('Active / apparent power',lambda m:f"{m['p']:.0f} W / {m['s']:.1f} VA"),
              ('Total RMS current',lambda m:f"{m['i']:.3f} A"),
              ('True power factor',lambda m:f"{m['pf']:.4f}"),
              ('Displacement factor',lambda m:f"{np.cos(np.deg2rad(m['lag'])):.3f}"),
              ('Fundamental reactive power',lambda m:'0 VAr' if abs(m['q1'])<.005 else f"{m['q1']:+.2f} VAr"),
              ('Current THD',lambda m:f"{100*m['thd']:.2f}%")]
        for i,(name,fmt) in enumerate(rows):
            self.at([.3,1.8,4.1,6.8,8.5,10.4,12.0][i])
            y=1.16-.53*i
            self.add(small(name,-6.07,y,WHITE_INK,21),seg(-6.08,y-.265,6.24,y-.265,GRID,1))
            for x,key in zip(cols,keys):
                self.add(put(label(fmt(VALUES[key]),21,COLORS[key]),x,y))
        self.at(14.5)
        self.add(placed_tex(r'p_R(t)=R\,i^2(t)\ge 0\qquad\mathrm{PF}=\frac{600}{848.53}=0.7071',0,-3.10,32))
        self.finish()

    def construct(self):
        self.cues=[]
        self.intro()
        self.energy()
        self.phasor_sweep()
        self.gates()
        self.mirror()
        self.fourier()
        self.result()
