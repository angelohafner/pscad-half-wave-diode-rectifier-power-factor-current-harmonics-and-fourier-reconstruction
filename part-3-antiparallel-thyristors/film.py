"""Narrated Manim scenes for the antiparallel thyristor study."""
from pathlib import Path
import json
import wave
import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parent
RESULT = json.loads((ROOT/"data/results.json").read_text())
with np.load(ROOT/"data/waveforms.npz") as data:
    DEG, PAIR, DIODE, CO, SINGLE = [data[x] for x in ("angle","pair","diode","c_pair","c_single")]
GOLD, MINT, BLUE, VIOLET = "#ffba68", "#68dfc8", "#a5caff", "#cab1ff"
WHITE_INK, MUTED, GRID, PANEL = "#f4f4f0", "#b2c5ce", "#38515f", "#182f3e"
config.background_color = "#10212d"
TICKS = [0,90,180,270,360]


def pos(x,y):
    return np.array([x,y,0])

def label(txt,size=26,color=WHITE_INK):
    return Text(txt,font="Segoe UI",font_size=size,color=color)

def math(expr,size=34,color=WHITE_INK):
    return MathTex(expr,font_size=size,color=color)

def put(obj,x,y):
    return obj.move_to(pos(x,y))

def left(obj,x,y):
    return put(obj,x+obj.width/2,y)

def seg(x1,y1,x2,y2,color=GRID,width=1.5):
    return Line(pos(x1,y1),pos(x2,y2),color=color,stroke_width=width)

def legend(x,y,txt,col):
    return VGroup(seg(x,y,x+.30,y,col,4),left(label(txt,20,col),x+.42,y))

def box(x,y,w,h):
    return put(RoundedRectangle(width=w,height=h,corner_radius=.16,stroke_color=GRID,stroke_width=1,
                                fill_color=PANEL,fill_opacity=1),x,y)


class Chart:
    def __init__(self,left_x,right_x,bottom,top,limits=(-16,16),xlimits=(0,360)):
        self.l,self.r,self.b,self.t=left_x,right_x,bottom,top
        self.low,self.high=limits
        self.x0,self.x1=xlimits

    def x(self,v):
        return self.l+(np.asarray(v)-self.x0)*(self.r-self.l)/(self.x1-self.x0)

    def y(self,v):
        return self.b+(np.asarray(v)-self.low)*(self.t-self.b)/(self.high-self.low)

    def grid(self,xs,ys,*,degrees=True,xticks=True,yticks=True):
        group=VGroup()
        for x in xs:
            group.add(seg(self.x(x),self.b,self.x(x),self.t,GRID,1))
            if xticks:
                group.add(put(math(str(x)+(r"^\circ" if degrees else ""),22,MUTED),self.x(x),self.b-.26))
        for y in ys:
            group.add(seg(self.l,self.y(y),self.r,self.y(y),MUTED if y==0 else GRID,1.5))
            if yticks:
                group.add(put(math(str(y),21,MUTED),self.l-.36,self.y(y)))
        return group

    def curve(self,x,y,color,width=4):
        xx,yy=self.x(x),self.y(y)
        return VMobject(stroke_color=color,stroke_width=width).set_points_as_corners(np.c_[xx,yy,np.zeros_like(xx)])

    def mark(self,x,color):
        return DashedLine(pos(self.x(x),self.b),pos(self.x(x),self.t),color=color,stroke_width=2,dash_length=.07)


class AntiparallelFilm(Scene):
    def page(self,section,title):
        self.clear()
        title_obj=Text(title,font="Georgia",font_size=42,color=WHITE_INK)
        if title_obj.width>12.80:
            title_obj.scale_to_fit_width(12.80)
        self.add(left(label("POWER ELECTRONICS   /   PART 3",18,MINT),-6.44,3.58),
                 left(label(section,18,MUTED),6.42-label(section,18).width,3.58),
                 left(title_obj,-6.44,2.85),
                 seg(-6.44,2.32,6.44,2.32))

    def cue(self,name):
        with wave.open(str(ROOT/"media"/"voice"/(name+".wav"))) as audio:
            length=audio.getnframes()/audio.getframerate()
        self.cues.append((name,len(self.renderer.file_writer.partial_movie_files),length))
        return self.time+length+.45

    def hold(self,end,extra=0):
        wait=end+extra-self.time
        if wait>1/24:
            self.wait(wait)

    def intro(self):
        self.page("The circuit","Can two different currents give the same power factor?")
        end=self.cue("intro")
        self.add(box(-3.25,-.29,6.22,4.22),box(3.25,-.29,6.22,4.22))
        self.add(left(label("Antiparallel thyristors",25),-6.00,1.39))
        art=ImageMobject(str(ROOT/"data/antiparallel.png")).scale_to_fit_width(5.37)
        self.play(FadeIn(put(art,-3.23,-.28)),run_time=.7)
        self.add(legend(-5.83,-1.99,"Positive half-cycle",GOLD),legend(-3.17,-1.99,"Negative half-cycle",MINT))
        for k,expr in enumerate([r"V_s=120\,\mathrm{V_{rms}}",r"f=60\,\mathrm{Hz}",r"R=12\,\Omega",r"\alpha=90^\circ"]):
            self.play(FadeIn(left(math(expr,38,VIOLET if k==3 else WHITE_INK),.85,1.10-k*.79)),run_time=.32)
        self.add(put(label("Compare the input current with the diode case from Part 1.",23,MUTED),0,-3.18))
        self.hold(end)

    def switching(self):
        self.page("Gate timing","One firing pulse per half-cycle")
        end=self.cue("positive")
        voltage=Chart(-5.13,5.94,.82,1.84,(-1.08,1.08))
        gates=Chart(-5.13,5.94,-.29,.49,(-.10,1.1))
        current=Chart(-5.13,5.94,-2.32,-.65)
        for chart,expr,col in [(voltage,r"v_s/\hat V",BLUE),(gates,r"g_1,g_2",VIOLET),(current,r"i_s\,[\mathrm{A}]",WHITE_INK)]:
            self.add(chart.grid(TICKS,[0],xticks=chart is current,yticks=False),
                     left(math(expr,23,col),-6.55,(chart.t+chart.b)/2))
        x=np.arange(0,360.01,.25)
        v=np.sin(np.deg2rad(x))
        gp=(x>=90)&(x<100); gn=(x>=270)&(x<280)
        def reveal(chart,values,start,stop,col,width=4):
            select=(x>=start)&(x<=stop)
            return Create(chart.curve(x[select],values[select],col,width),rate_func=linear)
        for a,b,col,on in [(0,90,GOLD,gp),(90,180,GOLD,gp),(180,269.75,MINT,gn)]:
            self.play(reveal(voltage,v,a,b,BLUE),reveal(gates,on,a,b,col),reveal(current,PAIR,a,b,col),run_time=1.45)
        q=put(label("What happens at the negative voltage peak?",25,MINT),0,-3.20)
        self.play(FadeIn(q),run_time=.4)
        self.hold(end,1.55)
        end=self.cue("negative")
        self.remove(q)
        self.add(put(math(r"\theta_{g1}=90^\circ\qquad \theta_{g2}=270^\circ",35),0,-3.18))
        self.play(reveal(voltage,v,269.75,280.25,BLUE),reveal(gates,gn,269.75,280.25,MINT),
                  reveal(current,PAIR,269.75,280.25,MINT),run_time=1.5)
        self.play(reveal(voltage,v,280.25,360,BLUE),reveal(gates,gn,280.25,360,MINT),
                  reveal(current,PAIR,280.25,360,MINT),run_time=2.0)
        self.hold(end)

    def symmetry(self):
        self.page("Half-wave symmetry","Shift the pulse, then reverse its sign")
        end=self.cue("symmetry")
        chart=Chart(-5.65,5.9,-1.90,1.60)
        self.add(chart.grid(TICKS,[-14,0,14]),left(math(r"i_s\,[\mathrm A]",24),-6.35,1.94))
        x=np.r_[90.,np.linspace(90,180,181)]
        y=np.r_[0.,np.sqrt(2)*10*np.sin(np.deg2rad(x[1:]))]
        pulse=chart.curve(x,y,GOLD)
        self.play(Create(pulse),run_time=1.)
        ghost=pulse.copy().set_color(VIOLET)
        self.play(ghost.animate.shift(RIGHT*(chart.x(180)-chart.x(0))),run_time=1.65)
        self.play(Transform(ghost,chart.curve(x+180,-y,MINT)),run_time=1.4)
        self.add(seg(chart.x(0),chart.y(0),chart.x(90),chart.y(0),GOLD,3),
                 seg(chart.x(180),chart.y(0),chart.x(270),chart.y(0),MINT,3))
        def area(xx,yy,color):
            return Polygon(*[pos(chart.x(a),chart.y(b)) for a,b in zip(xx,yy)],stroke_width=0,fill_color=color,fill_opacity=.25)
        self.play(FadeIn(area(x,y,GOLD)),FadeIn(area(x+180,-y,MINT)),run_time=.65)
        self.add(put(math(r"i(t+T/2)=-i(t)\qquad I_{\rm DC}=\frac{1}{T}\int_0^T i(t)\,dt=0",35),0,-3.02))
        self.hold(end)

    def spectrum(self):
        self.page("Harmonic spectrum","Why do the even orders disappear?")
        end=self.cue("spectrum")
        chart=Chart(-5.54,5.90,-2.14,1.27,(0,6.3),(-.5,9.5))
        self.add(chart.grid(range(10),[0,2,4,6],degrees=False),left(math(r"I_{h,\rm rms}\,[\mathrm A]",25),-6.28,1.87),
                 legend(-2.58,1.85,"One thyristor",VIOLET),legend(1.03,1.85,"Antiparallel pair",MINT))
        for coeff,offset,color in [(SINGLE,-.15,VIOLET),(CO,.15,MINT)]:
            bars=VGroup()
            for h in range(10):
                mag=abs(coeff[h])/(np.sqrt(2) if h else 1)
                if mag>.001:
                    y=chart.y(mag); y0=chart.y(0)
                    bars.add(put(Rectangle(height=y-y0,width=.24,stroke_width=0,fill_color=color,fill_opacity=1),
                                 chart.x(h+offset),(y+y0)/2))
            self.play(LaggedStart(*[GrowFromEdge(bar,DOWN) for bar in bars],lag_ratio=.09),run_time=1.7)
        self.add(put(math(r"C_h^{\rm pair}=\left[1-(-1)^h\right]C_h^{\rm single}",37),0,-3.18))
        self.hold(end)

    def fourier(self):
        self.page("Fourier reconstruction","Watch which terms change the current")
        end=self.cue("synthesis")
        chart=Chart(-5.63,5.91,-2.20,1.25,(-17,17))
        self.add(chart.grid(TICKS,[-15,0,15]),left(math(r"i_s\,[\mathrm A]",25),-6.25,1.87),
                 put(math(r"i_N=I_{\rm DC}+\sum_{h=1}^{N}\hat I_h\cos(h\theta+\psi_h)",32),.56,1.80))
        x=np.linspace(0,360,1081)
        harmonics=np.exp(1j*np.deg2rad(x)[None,:]*np.arange(51)[:,None])
        sums=np.cumsum((harmonics*CO[:,None]).real,axis=0)
        trace=chart.curve(x,sums[0],MINT)
        def readout(n):
            amplitude=abs(CO[n])
            phase=np.angle(CO[n],deg=True)
            phase_tex=rf"{phase:.0f}^\circ" if amplitude>1e-8 else r"\text{---}"
            return VGroup(left(math(rf"N={n}",31,MINT),-5.25,-3.21),
                          left(math(rf"\hat I={amplitude:.2f}\,\mathrm A",31),-2.30,-3.21),
                          left(math(r"\psi="+phase_tex,31),1.60,-3.21))
        read=readout(0)
        self.add(trace,read)
        self.wait(1.05)
        for n in range(1,51):
            if n==10:
                self.hold(end)
                end=self.cue("fast")
            self.remove(read)
            read=readout(n)
            self.add(read)
            duration=([1.8,1.7,1.65,1.35,1.25,1.08,1.0,.95,.85][n-1] if n<10 else .25)
            if n%2:
                self.play(Transform(trace,chart.curve(x,sums[n],MINT)),run_time=duration)
            else:
                self.wait(duration)
        self.hold(end)
        end=self.cue("overlay")
        self.remove(read)
        pick=np.arange(4,len(DEG)-1,15)
        dots=VGroup(*[put(Dot(color=GOLD,radius=.032),chart.x(DEG[j]),chart.y(PAIR[j])) for j in pick])
        self.play(FadeIn(dots),run_time=.75)
        self.add(legend(-5.60,-3.18,RESULT["source"]+" samples",GOLD),legend(1.12,-3.18,"50-order sum",MINT),
                 chart.mark(90,VIOLET),chart.mark(270,VIOLET))
        self.hold(end)

    def comparison(self):
        self.page("Power at the source","Same watts, same volt-amperes")
        end=self.cue("power")
        self.add(put(math(r"P=\frac1T\int_0^T v_s(t)i_s(t)\,dt",32),-3.27,1.88),
                 put(math(r"S=V_{\rm rms}I_{\rm rms}",32),3.22,1.88))
        for j,(name,curve,m,color) in enumerate([("Diode",DIODE,RESULT["diode"],GOLD),("Antiparallel pair",PAIR,RESULT["pair"],MINT)]):
            xc=-3.24+j*6.48
            self.add(box(xc,-.66,6.12,4.00),left(label(name,26,color),xc-2.77,1.00))
            chart=Chart(xc-2.60,xc+2.60,-.70,.56)
            self.add(chart.grid(TICKS,[0],xticks=False,yticks=False))
            self.play(Create(chart.curve(DEG[::2],curve[::2],color,3.3)),run_time=.82)
            self.add(left(math(rf"I_{{\rm rms}}={m['ir']:.2f}\,\mathrm A",31),xc-2.55,-1.23),
                     left(math(rf"P\approx{m['p']:.0f}\,\mathrm W\quad S\approx{m['s']:.1f}\,\mathrm{{VA}}",30),xc-2.55,-1.99))
        self.add(put(math(r"\mathrm{PF}=P/S\approx0.707",38),0,-3.24))
        self.hold(end)

    def closing(self):
        self.page("Displacement and distortion","The same power factor, two different spectra")
        end=self.cue("finish")
        self.add(put(math(r"\mathrm{PF}=\cos\varphi_1\;\frac{I_{1,\rm rms}}{I_{\rm rms}}",37),0,1.80))
        for j,(name,m,col) in enumerate([("Diode",RESULT["diode"],GOLD),("Antiparallel pair",RESULT["pair"],MINT)]):
            x=-3.22+j*6.44
            self.add(box(x,-.78,6.12,3.79),left(label(name,27,col),x-2.75,.69))
            lag=m["lag"] if abs(m["lag"])>.05 else 0.
            self.add(left(math(rf"\varphi_1={lag:.1f}^\circ",35),x-2.65,-.06))
            self.add(left(math(rf"\cos\varphi_1={m['displacement']:.3f}",32),x-2.65,-.79),
                     left(math(rf"I_1/I={m['distortion']:.3f}",32),x-2.65,-1.49))
            self.play(FadeIn(left(math(rf"\mathrm{{PF}}={m['pf']:.3f}",35,col),x-2.65,-2.19)),run_time=.55)
        self.add(put(label("Current distortion factor includes DC. All current ratios use RMS values.",21,MUTED),0,-3.25))
        self.hold(end,.9)

    def construct(self):
        self.cues=[]
        self.intro()
        self.switching()
        self.symmetry()
        self.spectrum()
        self.fourier()
        self.comparison()
        self.closing()
