"""Part 2 of the half-wave rectifier study. Angles use the rising voltage zero."""
from pathlib import Path
import json
import wave

import numpy as np
from manim import *

ROOT=Path(__file__).resolve().parent
STUDY=json.loads((ROOT/'data/study.json').read_text())
M=STUDY['scr']
BURG='#101e2b'
INK='#f0f4f6'
MUTED='#afc3cc'
GRID='#354e5d'
PANEL='#172b3a'
GOLD='#ffb65c'
MINT='#62e0cb'
BLUE='#9fc5ff'
PURPLE='#c1adff'
config.background_color=BURG
C=np.array(STUDY['co_re'])+1j*np.array(STUDY['co_im'])
DEG=np.array(STUDY['angle'])
I=np.array(STUDY['current'])

def xy(x,y):return np.array((x,y,0.))
def label(s,size=25,color=INK):
    return Text(s,font='Segoe UI',font_size=size,color=color)
def tex(s,size=35,color=INK):
    return MathTex(s,font_size=size,color=color)
def at(m,x,y):return m.move_to(xy(x,y))
def left(m,x,y):return at(m,x+m.width/2,y)
def line(a,b,color=GRID,w=2):
    return Line(xy(*a),xy(*b),color=color,stroke_width=w)
def card(x,y,w,h):
    return at(RoundedRectangle(width=w,height=h,corner_radius=.18,stroke_color=GRID,stroke_width=1,fill_color=PANEL,fill_opacity=1),x,y)
def key(x,y,name,color):
    return VGroup(line((x,y),(x+.32,y),color,4),left(label(name,21,color),x+.46,y))
def fourier(n,angles):
    return np.real(np.exp(1j*np.deg2rad(angles)[:,None]*np.arange(n+1))@C[:n+1])

class Plot:
    def __init__(self,x0,x1,y0,y1,xlim,ylim):
        self.l,self.r,self.b,self.t=x0,x1,y0,y1
        self.xmin,self.xmax=xlim;self.ymin,self.ymax=ylim
    def x(self,v):return self.l+(np.asarray(v)-self.xmin)*(self.r-self.l)/(self.xmax-self.xmin)
    def y(self,v):return self.b+(np.asarray(v)-self.ymin)*(self.t-self.b)/(self.ymax-self.ymin)
    def axes(self,xs,ys,degree=True):
        g=VGroup()
        for x in xs:
            g.add(line((self.x(x),self.b),(self.x(x),self.t),GRID,1))
            g.add(at(tex(str(x)+(r'^\circ' if degree else ''),23,MUTED),self.x(x),self.b-.26))
        for y in ys:
            g.add(line((self.l,self.y(y)),(self.r,self.y(y)),MUTED if y==0 else GRID,1.6 if y==0 else 1))
            g.add(at(tex(str(y),22,MUTED),self.l-.33,self.y(y)))
        return g
    def curve(self,x,y,col,w=4):
        px=self.x(x);py=self.y(y)
        return VMobject(stroke_color=col,stroke_width=w).set_points_as_corners(np.c_[px,py,np.zeros_like(px)])
    def dash(self,x,col=MUTED):
        return DashedLine(xy(self.x(x),self.b),xy(self.x(x),self.t),color=col,dash_length=.075,stroke_width=2)

class ThyristorFilm(Scene):
    def page(self,section,title):
        self.clear()
        self.add(left(label('POWER ELECTRONICS  /  PART 2',18,MINT),-6.4,3.56),
                 at(label(section,19,MUTED),6.34-label(section,19).width/2,3.56),
                 left(Text(title,font='Georgia',font_size=43,color=INK),-6.4,2.83),
                 line((-6.4,2.30),(6.4,2.30),GRID,1.5))
    def cue(self,name):
        path=ROOT/'media'/'voice'/(name+'.wav')
        with wave.open(str(path)) as w: duration=w.getnframes()/w.getframerate()
        # Each new cue starts at the encoded boundary of its next partial movie.
        self.cues.append((name,len(self.renderer.file_writer.partial_movie_files),duration))
        return self.time+duration+.35
    def finish(self,end):
        if end>self.time:self.wait(end-self.time)
    def intro(self):
        self.page('The circuit','What changes when the gate waits?')
        end=self.cue('intro')
        self.add(card(-3.26,-.35,6.2,4.35),card(3.26,-.35,6.2,4.35))
        self.add(left(label('Half-wave SCR',27,GOLD),-5.97,1.40))
        drawing=ImageMobject(str(ROOT/'data/scr_circuit.png')).scale_to_fit_height(2.79)
        self.play(FadeIn(at(drawing,-3.24,-.46)),run_time=.65)
        self.add(left(tex(r'V_{\rm rms}=120\,\mathrm V',36),.75,.98),
                 left(tex(r'f=60\,\mathrm{Hz}',36),.75,.14),
                 left(tex(r'R=12\,\Omega',36),.75,-.70))
        self.play(FadeIn(left(tex(r'\alpha=90^\circ',46,PURPLE),.75,-1.69)),run_time=.7)
        self.add(at(label('Predict the phase of the fundamental current.',23,MUTED),0,-3.28))
        self.finish(end)
    def firing(self):
        self.page('Switching','Freeze at the voltage peak')
        end=self.cue('freeze')
        x=np.linspace(0,360,721)
        voltage=np.sin(np.deg2rad(x));gate=(np.array(STUDY['gate'])[::2])
        rails=[]
        for mid,vals,lab,col,lo,hi in [(1.13,voltage,r'v_s/\hat V',BLUE,-1,1),(-.17,gate,r'g',PURPLE,-.1,1.1),(-1.80,I[::2],r'i_s\,[\mathrm A]',GOLD,-.6,15)]:
            p=Plot(-4.90,5.93,mid-.47,mid+.48,(0,360),(lo,hi));rails.append((p,vals,col))
            self.add(left(tex(lab,27,col),-6.36,mid),line((p.l,p.y(0)),(p.r,p.y(0)),GRID,1.6))
            for a in [0,90,180,270,360]:self.add(line((p.x(a),p.b),(p.x(a),p.t),GRID,.9))
        for a in [0,90,180,270,360]:self.add(at(tex(rf'{a}^\circ',23,MUTED),p.x(a),-2.57))
        tracker=ValueTracker(.10)
        def trails():
            g=VGroup()
            now=tracker.get_value()
            visible=np.append(x[x<now],now)
            for p,vals,col in rails:
                selected=np.interp(visible,x,vals)
                g.add(p.curve(visible,selected,col,3.8),at(Dot(radius=.055,color=col),p.x(now),p.y(selected[-1])))
            g.add(line((rails[0][0].x(now),-2.34),(rails[0][0].x(now),1.75),MUTED,1.1))
            return g
        traces=always_redraw(trails);self.add(traces)
        self.play(tracker.animate.set_value(89.5),run_time=2.8,rate_func=linear)
        self.add(at(tex(r'i_s(90^{\circ-})=?',34,GOLD),0,-3.29))
        question=self.mobjects[-1]
        self.finish(end);self.wait(1.8)
        end=self.cue('fire')
        self.play(FadeOut(question),FadeIn(at(tex(r'i_s(90^{\circ-})=0\qquad i_s(90^{\circ+})\simeq14.14\,\mathrm A',33,GOLD),0,-3.29)),run_time=.36)
        self.play(tracker.animate.set_value(100.5),run_time=1.4,rate_func=linear)
        self.wait(.7);self.play(tracker.animate.set_value(180),run_time=2.4,rate_func=linear)
        self.play(tracker.animate.set_value(360),run_time=2.1,rate_func=linear)
        self.finish(end)
    def phase(self):
        self.page('Fundamental current','How late is the fundamental?')
        end=self.cue('phase'); x=np.linspace(0,360,541);shift=M['phase']
        f=Plot(-5.65,5.92,-1.90,1.28,(0,360),(-1.13,1.13))
        self.add(f.axes([0,90,180,270,360],[-1,0,1]),key(-5.65,1.83,'Source voltage / peak',BLUE),key(-.42,1.83,'Fundamental current / peak',GOLD))
        v=np.sin(np.deg2rad(x));i=np.sin(np.deg2rad(x-shift))
        self.play(Create(f.curve(x,v,BLUE,4)),run_time=1.2)
        self.play(Create(f.curve(x,i,GOLD,4)),run_time=1.5)
        self.add(f.dash(90,BLUE),f.dash(90+shift,GOLD))
        self.wait(1.6)
        self.play(FadeIn(at(tex(rf'\alpha=90^\circ\qquad \varphi_1={shift:.1f}^\circ\ \text{{lagging}}',39,GOLD),0,-2.98)),run_time=.6)
        self.finish(end)
    def powers(self):
        self.page('Source-side power','Three hundred watts from six hundred VA')
        end=self.cue('power')
        self.add(at(tex(r'P=\frac{1}{T}\int_0^T v_s(t)i_s(t)\,dt',36,MINT),-3.20,1.44),
                 at(tex(r'S=V_{\rm rms}I_{\rm rms}',37,BLUE),3.24,1.44))
        for j,(caption,m,col) in enumerate([('Diode reference',STUDY['diode'],MINT),('SCR at peak firing',M,GOLD)]):
            x=-3.24+j*6.48
            self.add(card(x,-1.00,6.15,3.77),left(label(caption,25,col),x-2.71,.49))
            rows=[rf"I_{{\rm rms}}={m['ir']:.2f}\,\mathrm A",
                  rf"P={m['p']:.1f}\,\mathrm W\quad S={m['s']:.1f}\,\mathrm{{VA}}",
                  rf"\mathrm{{PF}}=P/S={m['pf']:.3f}"]
            for k,row in enumerate(rows):
                self.play(FadeIn(left(tex(row,32,col if k==2 else INK),x-2.69,-.26-k*.74)),run_time=.35)
        self.add(at(label('PSCAD source measurements (SCR)' if STUDY['native'] else 'Ideal-switch calculation',20,MUTED),0,-3.42))
        self.finish(end)
    def geometry(self):
        self.page('Power geometry','The reactive edge returns')
        end=self.cue('box')
        origin=np.array([-5.83,-1.95,0])
        def wire(p,q,d):
            # Isometric projection of three perpendicular power axes, in common VA units.
            a=p*np.array([.006,0.,0]); b=q*np.array([.0036,.0027,0]); c=d*np.array([0,.006,0])
            def edge(s,t,col,width):
                u=origin+s;v=origin+t
                if np.linalg.norm(v-u)<1.e-6:return Line(u,u+.0001*RIGHT,stroke_opacity=0)
                return Line(u,v,color=col,stroke_width=width)
            zero=np.zeros(3);g=VGroup()
            for start,direction in [(a,b),(a,c),(b,a),(b,c),(c,a),(c,b),(a+b,c),(a+c,b),(b+c,a)]:
                g.add(edge(start,start+direction,GRID,2.3))
            for stop,col,w in [(a,MINT,5),(b,BLUE,5),(c,PURPLE,5),(a+b+c,GOLD,4)]:
                g.add(edge(zero,stop,col,w))
            return g
        sh=wire(600,0,600)
        self.add(sh,at(label('Diode',22,MUTED),-3.8,1.92))
        case=self.mobjects[-1]
        self.add(left(tex(r'S^2=P^2+Q_1^2+D^2',37),.48,1.52))
        self.wait(1.8)
        self.play(Transform(sh,wire(M['p'],M['q'],M['d'])),Transform(case,at(label('SCR',24,GOLD),-3.8,1.92)),run_time=2.25)
        for j,(sym,val,unit,col) in enumerate([('P',M['p'],'W',MINT),('Q_1',M['q'],'var',BLUE),('D',M['d'],'VA',PURPLE),('S',M['s'],'VA',GOLD)]):
            self.add(left(tex(rf'{sym}={val:.1f}\,\mathrm{{{unit}}}',34,col),.50,.59-j*.64))
        self.add(at(tex(rf"\mathrm{{PF}}=\cos\varphi_1\,\frac{{I_{{1,\rm rms}}}}{{I_{{\rm rms}}}}={M['disp']:.3f}\times{M['df']:.3f}\simeq{M['pf']:.3f}",33),0,-3.12))
        self.finish(end)
    def spectrum(self):
        self.page('Current spectrum','Odd harmonics join the spectrum')
        end=self.cue('spectrum')
        f=Plot(-5.43,5.88,-2.22,1.24,(-.45,10.45),(0,5.45))
        self.add(f.axes(list(range(11)),[0,1,2,3,4,5],False),left(tex(r'I_{h,\rm rms}\;[\mathrm A]',25),-6.22,1.85),
                 key(-1.4,1.87,'Diode',MINT),key(1.2,1.87,'SCR',GOLD))
        bars=VGroup();diode=np.array(STUDY['diode_re'])+1j*np.array(STUDY['diode_im'])
        for h in range(11):
            for coef,shift,col in [(diode,-.15,MINT),(C,.15,GOLD)]:
                height=abs(coef[h])/(np.sqrt(2) if h else 1.)
                if height<.012:continue
                x=f.x(h+shift);y=f.y(height);y0=f.y(0)
                bars.add(at(Rectangle(width=.21,height=y-y0,stroke_width=0,fill_color=col,fill_opacity=1),x,(y+y0)/2))
        self.play(LaggedStart(*[GrowFromEdge(b,DOWN) for b in bars],lag_ratio=.045),run_time=2.1)
        self.add(at(tex(r'h=0:\ \mathrm{DC}\qquad h=1:\ \mathrm{fundamental}',28,MUTED),0,-3.26))
        self.finish(end)
    def synthesis(self):
        self.page('Fourier synthesis','Rebuild the current, one order at a time')
        f=Plot(-5.65,5.92,-2.15,1.22,(0,360),(-4,17))
        self.add(f.axes([0,90,180,270,360],[0,5,10,15]),left(tex(r'i_s\;[\mathrm A]',24),-6.27,1.82),
                 at(tex(r'i_N(\theta)=I_{\rm DC}+\sum_{h=1}^{N}\hat I_h\cos(h\theta+\psi_h)',32),.55,1.76))
        x=np.linspace(0,360,1001)
        waves=np.cumsum(np.real(np.exp(1j*np.deg2rad(x)[None,:]*np.arange(51)[:,None])*C[:,None]),axis=0)
        def read(n):
            if n:
                amplitude=abs(C[n]); angle=(np.angle(C[n],deg=True)+180)%360-180
                if abs(abs(angle)-180)<.5:angle=180
            else:amplitude=abs(C[0]);angle=0
            def number(v,places,color):
                return DecimalNumber(v,num_decimal_places=places,font_size=30,color=color)
            count=VGroup(tex('N=',31,GOLD),number(n,0,GOLD)).arrange(RIGHT,buff=.06)
            amp=VGroup(tex(r'\hat I=',31),number(amplitude,2,INK),tex(r'\mathrm A',29)).arrange(RIGHT,buff=.08)
            phase=VGroup(tex(r'\psi=',31))
            if n:phase.add(number(angle,0,INK),tex(r'^\circ',26))
            else:phase.add(tex(r'\text{---}',29,MUTED))
            phase.arrange(RIGHT,buff=.07)
            return VGroup(left(count,-4.97,-3.25),left(amp,-2.04,-3.25),left(phase,2.00,-3.25))
        end=self.cue('slow')
        trace=f.curve(x,waves[0],GOLD,4);readout=read(0)
        self.play(Create(trace),FadeIn(readout),run_time=.85);self.wait(.85)
        def step(n,sec):
            nonlocal readout
            self.remove(readout);readout=read(n);self.add(readout)
            self.play(Transform(trace,f.curve(x,waves[n],GOLD,4)),run_time=sec,rate_func=smooth)
        for n,sec in enumerate([2.05,1.85,1.45,1.37,1.2,1.11,1.02,1.,.9],1):step(n,sec)
        self.finish(end)
        end=self.cue('fast')
        for n in range(10,51):step(n,.25)
        self.finish(end);self.remove(readout)
        end=self.cue('overlay');ix=np.unique(np.linspace(0,len(DEG)-1,75).round().astype(int))
        dots=VGroup(*[at(Dot(radius=.036,color=MINT),f.x(DEG[k]),f.y(I[k])) for k in ix])
        self.play(FadeIn(dots),run_time=.55)
        self.add(key(-5.51,-3.22,'PSCAD samples' if STUDY['native'] else 'Ideal reference samples',MINT),
                 key(1.12,-3.22,'50-order sum',GOLD),f.dash(90,PURPLE))
        self.finish(end)
    def gibbs(self):
        self.page('Detail at firing','A closer look at the jump')
        end=self.cue('gibbs')
        f=Plot(-5.65,5.9,-2.17,1.14,(78,103),(-2.4,16.6))
        self.add(f.axes([80,85,90,95,100],[0,5,10,15]),left(tex(r'i_s\;[\mathrm A]',23),-6.26,1.84))
        x=np.linspace(78,103,901)
        if STUDY['native']:
            ids=(DEG>=78)&(DEG<=103);refx=DEG[ids];refy=I[ids]
        else:
            refx=np.r_[78,90,90,np.linspace(90.01,103,160)]
            refy=np.r_[0,0,120*np.sqrt(2)/12,120*np.sqrt(2)/12*np.sin(np.deg2rad(refx[3:]))]
        self.add(f.curve(refx,refy,MINT,3.6))
        self.add(key(-4.22,1.8,'PSCAD' if STUDY['native'] else 'Ideal SCR',MINT),key(-.50,1.8,'10 orders',BLUE),key(2.62,1.8,'50 orders',GOLD))
        self.play(Create(f.curve(x,fourier(10,x),BLUE,2.6)),run_time=1.1)
        self.play(Create(f.curve(x,fourier(50,x),GOLD,4)),run_time=1.5)
        self.add(at(tex(r'\lim_{N\to\infty}i_N(90^\circ)=\frac{i^-+i^+}{2}\simeq7.07\,\mathrm A',32),0,-3.14))
        self.finish(end);self.wait(.85)
    def construct(self):
        self.cues=[]
        for scene in [self.intro,self.firing,self.phase,self.powers,self.geometry,self.spectrum,self.synthesis,self.gibbs]:
            scene()
