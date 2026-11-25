"""Part 4: gate turn-off, load energy and Fourier synthesis."""
from pathlib import Path
import json
import wave
import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parent
RESULT = json.loads((ROOT/"data/results.json").read_text())
with np.load(ROOT/"data/waveforms.npz") as data:
    DEG, PAIR, CO, SCR_CO = [data[x] for x in ("angle","current","c","scr_c")]
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


class GTOFilm(Scene):
    def page(self,section,title):
        self.clear()
        title_obj=Text(title,font="Georgia",font_size=42,color=WHITE_INK)
        if title_obj.width>12.80:
            title_obj.scale_to_fit_width(12.80)
        self.add(left(label("POWER ELECTRONICS   /   PART 4",18,MINT),-6.44,3.58),
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
        self.page("The circuit","Can a shorter window deliver more power?")
        end=self.cue("intro")
        self.add(box(-3.24,-.33,6.18,4.12),box(3.24,-.33,6.18,4.12))
        self.add(left(label("Antiparallel GTOs",27),-6.03,1.29))
        art=ImageMobject(str(ROOT/"data/gto_circuit.png")).scale_to_fit_width(5.30)
        self.play(FadeIn(put(art,-3.24,-.38)),run_time=.65)
        self.add(legend(-5.84,-1.95,"Positive branch",GOLD),legend(-3.02,-1.95,"Negative branch",MINT))
        self.add(left(math(r"V_s=120\,\mathrm{V_{rms}}\quad f=60\,\mathrm{Hz}",32),.53,1.00),
                 left(math(r"R=12\,\Omega",34),.53,.29))
        self.play(FadeIn(left(math(r"G_1:\ 60^\circ\ \text{to}\ 120^\circ",33,GOLD),.53,-.65)),
                  FadeIn(left(math(r"G_2:\ 240^\circ\ \text{to}\ 300^\circ",33,MINT),.53,-1.47)),run_time=.85)
        self.add(put(label("Part 3 used SCRs firing at the voltage peaks.",23,MUTED),0,-3.18))
        self.hold(end)

    def switching(self):
        self.page("Gate turn-off","Freeze just before turn-off")
        end=self.cue("freeze")
        voltage=Chart(-4.96,5.98,.91,1.84,(-1.08,1.08))
        gate=Chart(-4.96,5.98,-.26,.51,(-.12,1.15))
        current=Chart(-4.96,5.98,-2.32,-.66,(-16,16))
        ticks=[0,60,120,180,240,300,360]
        for chart,symbol,col in [(voltage,r"v_s/\hat V",BLUE),(gate,r"g_1,\,g_2",VIOLET),(current,r"i_s\,[\mathrm A]",WHITE_INK)]:
            self.add(chart.grid(ticks,[0],xticks=chart is current,yticks=False),
                     left(math(symbol,27,col),-6.4,(chart.t+chart.b)/2))
        x=np.arange(0,360.01,.25)
        v=np.sin(np.deg2rad(x))
        g=((x>=60)&(x<120))|((x>=240)&(x<300))
        def reveal(start,stop,col,seconds):
            mask=(x>=start)&(x<=stop)
            curves=[chart.curve(x[mask],series[mask],color,3.7) for chart,series,color in
                    [(voltage,v,BLUE),(gate,g,col),(current,PAIR,col)]]
            self.play(*(Create(c) for c in curves),rate_func=linear,run_time=seconds)
        reveal(0,60,GOLD,1.1)
        reveal(60,119.75,GOLD,1.75)
        question=put(math(r"i_s(120^{\circ-})\approx12.25\,\mathrm A\qquad i_s(120^{\circ+})=?",34,GOLD),0,-3.19)
        self.play(FadeIn(question),run_time=.45)
        self.hold(end,1.55)
        end=self.cue("off")
        self.remove(question)
        answer=put(math(r"12.25\,\mathrm A\ \longrightarrow\ 0\,\mathrm A",41,GOLD),0,-3.22)
        self.add(answer,current.mark(120,VIOLET))
        reveal(119.75,121,GOLD,.7)
        self.wait(.9)
        reveal(121,180,GOLD,1.2)
        reveal(180,240,MINT,1.6)
        reveal(240,300.25,MINT,1.8)
        reveal(300.25,360,MINT,1.1)
        self.hold(end)

    def power_area(self):
        self.page("Instantaneous load power","Which area delivers more energy?")
        end=self.cue("area")
        chart=Chart(-5.62,5.89,-1.88,1.21,(0,2.6),(0,180))
        self.add(chart.grid([0,30,60,90,120,150,180],[0,1,2]),left(math(r"p_R\,[\mathrm{kW}]",24),-6.23,1.84),
                 legend(-2.80,1.85,"GTO only",GOLD),legend(.10,1.85,"Both",MINT),legend(2.38,1.85,"SCR only",VIOLET))
        def power(deg):
            return 2.4*np.sin(np.deg2rad(deg))**2
        x=np.linspace(0,180,361)
        self.add(DashedVMobject(chart.curve(x,power(x),MUTED,2),num_dashes=65))
        def patch(a,b,col):
            xx=np.linspace(a,b,91); yy=power(xx)
            top=chart.curve(xx,yy,col,4.5)
            verts=[pos(chart.x(a),chart.y(0)),*[pos(chart.x(xi),chart.y(yi)) for xi,yi in zip(xx,yy)],
                   pos(chart.x(b),chart.y(0))]
            return VGroup(Polygon(*verts,stroke_width=0,fill_color=col,fill_opacity=.36),
                          top,seg(chart.x(a),chart.y(0),chart.x(a),chart.y(yy[0]),col,1.4),
                          seg(chart.x(b),chart.y(0),chart.x(b),chart.y(yy[-1]),col,1.4))
        self.play(FadeIn(patch(90,120,MINT)),run_time=.85)
        self.wait(.6)
        self.play(FadeIn(patch(60,90,GOLD)),run_time=.9)
        self.play(FadeIn(patch(120,180,VIOLET)),run_time=1.05)
        self.add(put(math(r"p_R=v_s^2/R\;\; \text{during ideal conduction}",32),0,-3.02))
        self.hold(end,1.)

    def energy(self):
        self.page("Energy per cycle","The shorter interval wins")
        end=self.cue("energy")
        self.add(put(math(r"E_R=\int_0^T p_R(t)\,dt \qquad P_R=f E_R",36),0,1.72))
        for j,(name,window,e,p,col) in enumerate([("SCR pair",r"90^\circ\ \mathrm{to}\ 180^\circ",10.,600.,VIOLET),
                                                 ("GTO pair",r"60^\circ\ \mathrm{to}\ 120^\circ",12.17995562,730.797337,GOLD)]):
            cx=-3.23+6.46*j
            self.add(box(cx,-.74,6.12,3.72),left(label(name,26,col),cx-2.63,.65))
            for k,s in enumerate([window,rf"E_R={e:.2f}\,\mathrm{{J/cycle}}",rf"P_R={p:.1f}\,\mathrm W"]):
                self.play(FadeIn(left(math(s,36,col if k==2 else WHITE_INK),cx-2.63,-.06-.79*k)),run_time=.42)
        self.add(put(label("Ideal switches  /  60 cycles per second",21,MUTED),0,-3.18))
        self.hold(end)

    def phase(self):
        self.page("Fundamental phase","The GTO fundamental follows the voltage")
        end=self.cue("phase")
        ch=Chart(-5.57,5.90,-1.95,1.25,(-1.12,1.12))
        self.add(ch.grid(TICKS,[-1,0,1]),legend(-5.65,1.86,"Source voltage",BLUE),legend(-1.64,1.86,"SCR fundamental",VIOLET),
                 legend(2.27,1.86,"GTO fundamental",GOLD))
        x=np.linspace(0,360,541); rad=np.deg2rad(x)
        self.play(Create(ch.curve(x,np.sin(rad),BLUE,3.5)),run_time=1.)
        for key,col in [("scr",VIOLET),("gto",GOLD)]:
            m=RESULT[key]
            wave=m["i1"]/10*np.sin(rad-np.deg2rad(m["lag"]))
            self.play(Create(ch.curve(x,wave,col,4.)),run_time=1.2)
        self.add(ch.mark(90,GOLD),ch.mark(90+RESULT["scr"]["lag"],VIOLET),
                 put(math(r"\varphi_{1,\rm SCR}=32.48^\circ\qquad \varphi_{1,\rm GTO}=0^\circ\qquad Q_{1,\rm GTO}=0",31),0,-2.78),
                 put(label("Voltage base = source peak. Current base = peak voltage / resistance.",19,MUTED),0,-3.53))
        self.hold(end)

    def spectrum(self):
        self.page("Current spectrum","Unity displacement, distorted current")
        end=self.cue("spectrum")
        ch=Chart(-5.52,5.86,-1.83,1.28,(0,6.5),(-.5,9.5))
        self.add(ch.grid(range(10),[0,2,4,6],degrees=False),left(math(r"I_{h,\rm rms}\,[\mathrm A]",25),-6.3,1.85),
                 legend(-1.48,1.87,"SCR pair",VIOLET),legend(1.33,1.87,"GTO pair",GOLD))
        for coeff,offset,col in [(SCR_CO,-.14,VIOLET),(CO,.14,GOLD)]:
            bars=[]
            for n in range(10):
                val=abs(coeff[n])/(np.sqrt(2) if n else 1.)
                if val<1e-6:
                    continue
                base=ch.y(0); top=ch.y(val)
                bars.append(put(Rectangle(height=top-base,width=.23,stroke_width=0,fill_color=col,fill_opacity=1),
                                ch.x(n+offset),(top+base)/2))
            self.play(LaggedStart(*[GrowFromEdge(bar,DOWN) for bar in bars],lag_ratio=.12),run_time=1.55)
        m=RESULT["gto"]
        self.add(put(math(rf"\mathrm{{PF}}=\cos\varphi_1\,\frac{{I_1}}{{I}}=1\times\frac{{{m['i1']:.2f}}}{{{m['ir']:.2f}}}\approx{m['pf']:.3f}",36),0,-2.91),
                 put(label("Source current · RMS magnitudes",18,MUTED),0,-3.57))
        self.hold(end)


    def fourier(self):
        self.page("Fourier reconstruction","Reconstruct the four switching edges")
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
                 *[chart.mark(a,VIOLET) for a in (60,120,240,300)])
        self.hold(end)

    def construct(self):
        self.cues=[]
        self.intro()
        self.switching()
        self.power_area()
        self.energy()
        self.phase()
        self.spectrum()
        self.fourier()
