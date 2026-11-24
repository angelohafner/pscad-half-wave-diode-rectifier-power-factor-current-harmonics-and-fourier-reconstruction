"""English-language Manim film based on the two recorded PSCAD input channels."""
import json
import wave
from pathlib import Path
import numpy as np
from manim import *

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
DATA=json.loads((ASSETS/'data.json').read_text())
if not DATA['native']:
    raise RuntimeError('Run both native cases and prepare.py before rendering.')
A,B=DATA['direct'],DATA['diode']
BG='#101e2b'; INK='#f0f4f6'; SUB='#afc3cc'; GRID='#334b5c'
TEAL='#62e0cb'; GOLD='#ffb65c'; SKY='#9fc5ff'; LILAC='#c1adff'; PANEL='#172b3a'
config.background_color=BG
def pos(x,y): return np.array([x,y,0.])
def text(s,size=27,color=INK,bold=False):
    return Text(s,font='Segoe UI',font_size=size,color=color,weight=BOLD if bold else NORMAL)
def math(s,size=33,color=INK):return MathTex(s,font_size=size,color=color)
def at(m,x,y): return m.move_to(pos(x,y))
def left(m,x,y): return m.move_to(pos(x+m.width/2,y))
def ln(x0,y0,x1,y1,color=GRID,width=1.4):return Line(pos(x0,y0),pos(x1,y1),color=color,stroke_width=width)
def card(x,y,w,h):
    return at(RoundedRectangle(corner_radius=.18,width=w,height=h,stroke_width=1,stroke_color=GRID,fill_color=PANEL,fill_opacity=1),x,y)
def key(x,y,label,color,dots=False):
    sample=(VGroup(*(at(Dot(radius=.034,color=color),x+.085*j,y) for j in range(5))) if dots else ln(x,y,x+.34,y,color,4))
    return VGroup(sample,left(text(label,20,color),x+.46,y))
class Field:
    def __init__(self,box,xrange,yrange):
        self.l,self.r,self.b,self.t=box
        self.xmin,self.xmax=xrange
        self.ymin,self.ymax=yrange
    def x(self,v):return self.l+(np.asarray(v)-self.xmin)*(self.r-self.l)/(self.xmax-self.xmin)
    def y(self,v):return self.b+(np.asarray(v)-self.ymin)*(self.t-self.b)/(self.ymax-self.ymin)
    def grid(self,xticks,yticks,xlabels=None):
        g=VGroup()
        for k,v in enumerate(xticks):
            xx=self.x(v);g.add(ln(xx,self.b,xx,self.t))
            lab=xlabels[k] if xlabels else str(v)
            g.add(at(math(lab,24,SUB),xx,self.b-.24))
        for v in yticks:
            yy=self.y(v);g.add(ln(self.l,yy,self.r,yy,SUB if v==0 else GRID,1.8 if v==0 else 1.2))
            g.add(at(math(str(v),24,SUB),self.l-.32,yy))
        return g
    def curve(self,x,y,color,width=4):
        xx=self.x(x); yy=self.y(y)
        return VMobject(stroke_color=color,stroke_width=width).set_points_as_corners(np.c_[xx,yy,np.zeros_like(xx)])
class RectifierFilm(Scene):
    def frame(self,section,title):
        title_m=Text(title,font='Georgia',font_size=44,color=INK)
        return VGroup(left(text('POWER ELECTRONICS',17,TEAL,True),-6.38,3.54),
                      left(title_m,-6.38,2.78),ln(-6.38,2.23,6.38,2.23),
                      at(text(section,18,SUB),6.38-text(section,18).width/2,3.54))
    def say(self,name):
        path=ASSETS/'voice'/(name+'.wav')
        with wave.open(str(path)) as f: dur=f.getnframes()/f.getframerate()
        print(f'Cue {name} {self.time:.3f} {dur:.3f}',flush=True)
        # A visually cached preceding animation must not suppress the next voice cue.
        self.renderer.file_writer.add_sound(str(path),self.time+.12)
        return self.time+.12+dur+.23
    def finish(self,end):
        if end>self.time:self.wait(end-self.time)
    def fresh(self): self.clear()
    def instantaneous(self):
        self.fresh()
        end=self.say('inst')
        self.add(self.frame('Instantaneous power','Follow one instant through the circuit'))
        self.add(at(math(r'p(t)=v_s(t)\,i_s(t)',44,GOLD),0,1.72))
        x=np.linspace(0,1,len(B['wave']))[::5]
        voltage=np.array(B['volts'])[::5]
        current=np.array(B['wave'])[::5]
        power=voltage*current
        fields=[]
        for name, values, limits, ticks, baseline, color in [
            (r'v_s\ [\mathrm V]',voltage,(-180,180),[-170,0,170],.42,SKY),
            (r'i_s\ [\mathrm A]',current,(-1,15),[0,14],-1.00,TEAL),
            (r'p\ [\mathrm W]',power,(-140,2500),[0,2400],-2.45,GOLD)]:
            g=Field((-4.87,5.8,baseline-.47,baseline+.58),(0,1),limits)
            for tick in ticks:
                self.add(ln(g.l,g.y(tick),g.r,g.y(tick),GRID,1),at(math(str(tick),19,SUB),-5.25,g.y(tick)))
            self.add(left(math(name,25,color),-6.62,baseline+.10),g.curve(x,values,color,3.5))
            fields.append((g,values,color))
        self.add(at(math(r'0',22,SUB),-4.87,-3.32),at(math(r'T/2',22,SUB),.465,-3.32),at(math(r'T',22,SUB),5.8,-3.32))
        scan=ValueTracker(0)
        def probes():
            phase=scan.get_value()
            xx=fields[0][0].x(phase)
            marks=VGroup(ln(xx,-2.93,xx,1.0,SUB,1.7))
            for field,values,color in fields:
                marks.add(at(Dot(radius=.065,color=color),xx,field.y(np.interp(phase,x,values))))
            return marks
        cursor=always_redraw(probes)
        self.add(cursor)
        self.wait(1)
        self.play(scan.animate.set_value(1),run_time=5.7,rate_func=linear)
        self.finish(end); self.fresh()

    def phase_comparison(self):
        end=self.say('phase')
        self.add(self.frame('Rectifier fundamental','Do the voltage and fundamental line up?'))
        x=np.linspace(0,1,len(B['volts']))[::4]
        v=np.array(B['volts'])[::4]
        c=complex(B['re'][1],B['im'][1])
        i=np.real(c*np.exp(2j*np.pi*x))
        for mid,values,col,label in [(.93,v,SKY,r'v_s/\hat V_s'),(-.8,i,GOLD,r'i_1/\hat I_1')]:
            f=Field((-4.95,4.95,mid-.66,mid+.66),(0,1),(-1,1))
            self.add(ln(f.l,mid,f.r,mid),left(math(label,28,col),-6.43,mid))
            self.play(Create(f.curve(x,values/max(abs(values)),col,3.8)),run_time=1.1)
        for k in [.25,.5,.75]:
            xx=f.x(k)
            self.add(DashedLine(pos(xx,-1.58),pos(xx,1.67),dash_length=.075,stroke_width=1.6,color=SUB))
        self.wait(2.4)
        self.play(FadeIn(at(math(r'\varphi_1=0^\circ\qquad Q_1=V_{\rm rms}I_{1,\rm rms}\sin\varphi_1=0\ \mathrm{var}',35),0,-2.65)),run_time=.6)
        self.finish(end);self.fresh()

    def power_products(self):
        end=self.say('product_intro')
        self.add(self.frame('Power over one cycle','Which currents deliver energy?'))
        self.add(at(math(r'p_h(t)=v_s(t)\,i_h(t)',46,GOLD),0,1.25))
        self.play(FadeIn(at(math(r'P_h=\frac{1}{T}\int_0^T v_s(t)\,i_h(t)\,dt',40),0,-.25)),run_time=.6)
        self.add(key(-4.80,-1.80,'Positive area',TEAL),key(.65,-1.80,'Negative area',LILAC))
        self.finish(end);self.fresh()
        x=np.linspace(0,1,601)
        voltage=np.interp(x,np.linspace(0,1,len(B['volts'])),B['volts'])
        for h,caption in [(0,'DC current'),(1,'Fundamental current'),(2,'Second harmonic'),(4,'Fourth harmonic')]:
            end=self.say('product'+str(h))
            self.add(self.frame('Power over one cycle',caption))
            c=complex(B['re'][h],B['im'][h])
            current=np.real(c*np.exp(2j*np.pi*h*x))
            product=voltage*current
            gtop=Field((-5.40,1.65,.90,1.57),(0,1),(-1.05,1.05))
            subs=r'\mathrm{DC}' if h==0 else str(h)
            self.add(ln(gtop.l,gtop.y(0),gtop.r,gtop.y(0)),
                     left(math(r'v_s/\hat V_s',21,SKY),-5.4,1.83),
                     left(math(rf'i_{{{subs}}}/\hat I_{{{subs}}}',21,TEAL),-3.80,1.83))
            self.play(Create(gtop.curve(x,voltage/max(abs(voltage)),SKY,4.8)),
                      Create(gtop.curve(x,current/max(abs(current)),TEAL,2.1)),run_time=1.0)
            limit={0:800,1:1250,2:550,4:110}[h]
            f=Field((-5.4,1.65,-2.20,.38),(0,1),(-limit*1.04,limit*1.04))
            self.add(f.grid([0,.25,.5,.75,1],[-limit,0,limit],['0','T/4','T/2','3T/4','T']),
                     left(math(r'p_h\ [\mathrm W]',21,GOLD),-6.62,.62))
            fills=VGroup()
            for sign,color in [(1,TEAL),(-1,LILAC)]:
                active=np.flatnonzero(sign*product>1e-5)
                for band in np.split(active,np.flatnonzero(np.diff(active)>1)+1):
                    if not len(band):continue
                    idx=np.arange(max(0,band[0]-1),min(len(x),band[-1]+2))
                    vertices=[pos(f.x(x[idx[0]]),f.y(0))]
                    vertices += [pos(f.x(x[k]),f.y(sign*max(0,sign*product[k]))) for k in idx]
                    vertices.append(pos(f.x(x[idx[-1]]),f.y(0)))
                    fills.add(Polygon(*vertices,stroke_width=0,fill_color=color,fill_opacity=.55))
            self.play(FadeIn(fills),Create(f.curve(x,product,GOLD,3.4)),run_time=1.3)
            self.add(card(4.25,-.28,4.20,4.04),left(text('Energy per cycle',22,SUB),2.55,1.25),
                     left(text('Active power',22,SUB),2.55,-.60))
            ask=left(math(rf'P_{{{subs}}}=?',37,GOLD),2.55,-1.31)
            factor=r'I_{\rm DC}' if h==0 else rf'i_{{{h}}}(t)'
            integral=at(math(rf'P_{{{subs}}}=\frac{{1}}{{T}}\int_0^T v_s(t)\,{factor}\,dt',34),-.66,-3.19)
            self.add(ask,integral)
            self.finish(end);self.wait(1.85)
            response=self.say('result'+str(h))
            values=B['products'][str(h)]
            average=values['mean'] if abs(values['mean'])>.005 else 0.
            pos_j=values['positive_j']
            neg_j=values['negative_j'] if abs(values['negative_j'])>.0005 else 0.
            self.play(FadeIn(left(math(rf'E_+={pos_j:.3f}\,\mathrm J',31,TEAL),2.55,.65)),
                      FadeIn(left(math(rf'E_-={neg_j:.3f}\,\mathrm J',31,LILAC),2.55,.04)),run_time=.55)
            self.play(ReplacementTransform(ask,left(math(rf'P_{{{subs}}}={average:.2f}\,\mathrm W',35,GOLD),2.55,-1.32)),run_time=.6)
            self.finish(response);self.fresh()

    def power_geometry(self):
        end=self.say('triangle')
        self.add(self.frame('Power geometry','From the power triangle to the power box'))
        origin=pos(-5.59,-1.85)
        p=pos(3.35,0)
        q=pos(0,2.08)
        depth=pos(1.05,1.04)
        def edge(start,stop,color,width=3):
            if np.linalg.norm(stop-start)<1e-6:
                return Line(start,start+RIGHT*.001,stroke_opacity=0)
            return Line(start,stop,color=color,stroke_width=width)
        def wire(reactive,extra,show_box):
            o=origin; a=p; b=reactive; c=extra
            model=VGroup()
            for start,stop in [(o,o+b),(o+b,o+b+a),(o+b,o+b+c),(o+a,o+a+c),
                               (o+c,o+c+a),(o+c,o+c+b),(o+a+b,o+a+b+c),
                               (o+b+c,o+b+c+a),(o+a+c,o+a+b+c)]:
                model.add(edge(start,stop,GRID,1.8).set_stroke(opacity=.95 if show_box and np.linalg.norm(stop-start)>1e-6 else 0))
            model.add(edge(o,o+a,TEAL,5),edge(o+a,o+a+b,SKY,5),
                      edge(o,o+c,LILAC,5),edge(o,o+a+b+c,GOLD,3.7))
            return model
        shape=wire(q,depth*0,False)
        p_label=at(math('P',31,TEAL),-3.91,-2.22)
        q_label=at(math('Q_1',29,SKY),-1.88,-.81)
        s_label=at(math('S_1',29,GOLD),-4.24,-.64)
        sin_head=left(text('Sinusoidal voltage and current',23,SUB),.62,1.57)
        formula=left(math(r'S_1^2=P^2+Q_1^2',39),.62,.75)
        self.add(shape,p_label,q_label,s_label,sin_head,formula)
        self.wait(6.15)
        direct=VGroup(left(text('Direct resistor',23,TEAL,True),.62,-.32),
                      left(math(r'P=1{,}200\,\mathrm W,\quad S_1=1{,}200\,\mathrm{VA}',26),.62,-1.08))
        self.play(Transform(shape,wire(q*0,depth*0,False)),FadeOut(q_label),FadeOut(s_label),FadeIn(direct),run_time=1.1)
        self.finish(end);self.wait(.65)
        end=self.say('box')
        self.play(FadeOut(direct),FadeOut(sin_head),FadeOut(formula),Transform(shape,wire(q,depth*0,False)),run_time=.72)
        dim=left(text('DC and higher-order current',22,LILAC,True),.62,1.57)
        eq=left(math(r'D=V_{\rm rms}\sqrt{I_{\rm DC}^2+\sum_{h\ge2}I_{h,\rm rms}^2}',30,LILAC),.62,.69)
        diag=left(math(r'S^2=P^2+Q_1^2+D^2',34,GOLD),.62,-.34)
        q_tag=at(math('Q_1',27,SKY),-1.91,-.80)
        d_tag=at(math('D',27,LILAC),-5.34,-1.08)
        self.add(q_tag)
        self.play(Transform(shape,wire(q,depth,True)),FadeIn(d_tag),FadeIn(dim),run_time=2.25)
        self.play(FadeIn(eq),FadeIn(diag),run_time=.8)
        self.finish(end);self.wait(.9)
        end=self.say('face')
        self.play(Transform(shape,wire(q*0,depth,True)),FadeOut(q_tag),run_time=1.65)
        self.play(Transform(shape,wire(q*0,pos(0,3.35),True)),d_tag.animate.move_to(pos(-5.92,-.18)),run_time=1.15)
        self.add(left(math(r'Q_1=0\ \mathrm{var}',30,SKY),.62,-1.20),
                 left(math(rf"P={B['p']:.1f}\,\mathrm W\quad D={B['residual_va']:.1f}\,\mathrm{{VA}}",29),.62,-1.93),
                 left(math(rf"S={B['s']:.1f}\,\mathrm{{VA}}",34,GOLD),.62,-2.68))
        self.play(FadeIn(at(math('S',29,GOLD),-4.22,-.08)),run_time=.4)
        self.finish(end);self.fresh()

    def sum_rules(self):
        self.fresh()
        end=self.say('rules')
        self.add(self.frame('One-cycle averages','Two sums explain the power factor'))
        for x,title,color in [(-3.26,'Active power',TEAL),(3.26,'Total RMS current',GOLD)]:
            self.add(card(x,-.25,6.15,3.98),left(text(title,28,color,True),x-2.74,1.21))
        self.play(FadeIn(at(math(r'P=\sum_{h=0}^{\infty}\frac{1}{T}\int_0^T v_s(t)\,i_h(t)\,dt',29,TEAL),-3.26,.15)),
                  FadeIn(at(math(r'0+599.95+0+\cdots',30),-3.26,-.96)),run_time=.75)
        self.wait(3.8)
        self.play(FadeIn(at(math(r'I_{\rm rms}=\sqrt{I_{\rm DC}^2+\sum_{h\ge1}I_{h,\rm rms}^2}',31,GOLD),3.26,.15)),
                  FadeIn(at(math(r'\sqrt{4.50^2+5.00^2+2.12^2+\cdots}',26),3.26,-.96)),run_time=.75)
        line=at(math(rf"P={B['p']:.2f}\,\mathrm W\qquad I_{{\rm rms}}={B['ir']:.3f}\,\mathrm A\qquad \mathrm{{PF}}={B['pf']:.4f}",33),0,-2.97)
        self.play(FadeIn(line),run_time=.6)
        self.finish(end);self.wait(2.1)

    def construct(self):
        end=self.say('intro')
        self.add(self.frame('Circuit comparison','What changes when we add one diode?'))
        for j,(name,caption,color) in enumerate([('direct','Direct resistor',TEAL),('diode','Half-wave rectifier',GOLD)]):
            x=-3.26+j*6.52
            panel=card(x,-.05,6.20,3.96)
            cap=left(text(caption,28,color,True),x-2.72,1.47)
            icon=at(ImageMobject(str(ASSETS/(name+'.png'))).set_height(2.18),x,-.14)
            self.play(FadeIn(panel),FadeIn(cap),FadeIn(icon,shift=.12*UP),run_time=.75)
        self.play(FadeIn(at(math(r'V_{\mathrm{rms}}=120\,\mathrm{V}\qquad f=60\,\mathrm{Hz}\qquad R=12\,\Omega',35),0,-2.67)),run_time=.6)
        self.finish(end);self.fresh()

        end=self.say('waves')
        self.add(self.frame('Time domain','The diode passes one half-cycle'))
        x=np.linspace(0,1,len(A['wave']))
        f=Field((-5.6,5.94,-2.62,1.35),(0,1),(-16,16))
        self.add(f.grid([0,.25,.5,.75,1],[-15,-10,-5,0,5,10,15],[r'0',r'90^\circ',r'180^\circ',r'270^\circ',r'360^\circ']),
                 left(math(r'i_s\;[\mathrm A]',26),-6.35,1.82),
                 key(-2.9,1.84,'Direct resistor',TEAL),key(.2,1.84,'Half-wave rectifier',GOLD))
        direct=f.curve(x[::4],np.array(A['wave'])[::4],TEAL,6)
        diode=f.curve(x[::4],np.array(B['wave'])[::4],GOLD,3)
        self.play(Create(direct),run_time=2.4,rate_func=linear)
        self.wait(1.2);self.play(Create(diode),run_time=3.1,rate_func=linear)
        self.play(FadeIn(at(text('conduction',23,GOLD),f.x(.25),f.y(5))),FadeIn(at(text('blocking',23,GOLD),f.x(.75),f.y(4))),run_time=.5)
        self.finish(end);self.fresh()

        self.instantaneous()
        end=self.say('rms')
        self.add(self.frame('PSCAD measurements','What do the two meters read?'))
        voltage_rms=at(math(r'V_{\rm rms}=\sqrt{\frac{1}{T}\int_0^T v_s^2(t)\,dt}',38,SKY),-3.26,1.41)
        current_rms=at(math(r'I_{\rm rms}=\sqrt{\frac{1}{T}\int_0^T i_s^2(t)\,dt}',38,GOLD),3.26,1.41)
        self.play(FadeIn(voltage_rms),FadeIn(current_rms),run_time=.65)
        for j,(s,cap,color) in enumerate([(A,'Direct resistor',TEAL),(B,'Half-wave rectifier',GOLD)]):
            x=-3.26+j*6.52
            self.add(card(x,-1.12,6.20,3.65),left(text(cap,25,color,True),x-2.72,.30))
            readings=VGroup(math(rf"V_{{\rm rms}}={s['vr']:.1f}\,\mathrm V",34,SKY),
                            math(rf"I_{{\rm rms}}={s['ir']:.3f}\,\mathrm A",34,color)).arrange(DOWN,aligned_edge=LEFT,buff=.21)
            self.play(FadeIn(left(readings,x-2.66,-1.01)),run_time=.65)
        self.finish(end);self.fresh()
        end=self.say('power')
        self.add(self.frame('PSCAD measurements','How much power reaches the resistor?'))
        self.add(at(math(r'P=\frac{1}{T}\int_0^T v_s(t)\,i_s(t)\,dt',37,TEAL),-3.18,1.43),
                 at(math(r'S=V_{\rm rms}\,I_{\rm rms}',37,GOLD),3.20,1.43))
        for j,(s,cap,color) in enumerate([(A,'Direct resistor',TEAL),(B,'Half-wave rectifier',GOLD)]):
            x=-3.26+j*6.52
            self.add(card(x,-1.12,6.20,3.66),left(text(cap,25,color,True),x-2.72,.30))
            values=VGroup(math(rf"P={s['p']:.2f}\,\mathrm{{W}}",32),
                          math(rf"S={s['s']:.2f}\,\mathrm{{VA}}",32)).arrange(DOWN,aligned_edge=LEFT,buff=.16)
            self.play(FadeIn(left(values,x-2.72,-.69)),run_time=.55)
        self.finish(end); self.wait(1.7)
        end=self.say('pf')
        for j,(s,color) in enumerate([(A,TEAL),(B,GOLD)]):
            self.play(FadeIn(left(math(rf"\mathrm{{PF}}=\frac{{{s['p']:.2f}}}{{{s['s']:.2f}}}={s['pf']:.3f}",32,color),-5.98+j*6.52,-1.87)),run_time=.55)
        self.finish(end);self.fresh()

        end=self.say('spectrum')
        self.add(self.frame('Frequency domain','What is hidden in the current?'))
        bars=VGroup()
        for j,(case,cap,color) in enumerate([(A,'Direct resistor',TEAL),(B,'Half-wave rectifier',GOLD)]):
            xmid=-3.15+j*6.5
            self.add(left(text(cap,25,color,True),xmid-2.72,1.75))
            g=Field((xmid-2.19,xmid+2.62,-2.12,1.04),(-.6,8.65),(0,10.8))
            self.add(g.grid([0,1,2,4,6,8],[0,5,10],[r'\mathrm{DC}','1','2','4','6','8']))
            for h in range(9):
                value=case['spectrum'][h]
                if value<.005:continue
                b=Rectangle(width=.245,height=g.y(value)-g.y(0),stroke_width=0,fill_color=color,fill_opacity=1)
                bars.add(at(b,g.x(h),(g.y(value)+g.y(0))/2))
        self.add(at(text('Harmonic order',21,SUB),0,-2.84),left(math(r'I_{h,\mathrm{rms}}\ [\mathrm A]',24,SUB),-6.12,1.15))
        self.play(LaggedStart(*[GrowFromEdge(b,DOWN) for b in bars],lag_ratio=.15),run_time=2.7)
        self.play(FadeIn(at(math(r'i_s(t)=I_{\mathrm{DC}}+i_1(t)+i_2(t)+i_4(t)+\cdots',33),0,-3.43)),run_time=.7)
        self.finish(end);self.fresh()

        self.phase_comparison()
        self.power_products()
        self.power_geometry()
        end=self.say('distortion')
        self.add(self.frame('RMS current','Why the power factor falls'))
        info=[('Fundamental',rf"{B['i1']:.2f}\,\mathrm{{A}}",SKY),('Total RMS',rf"{B['ir']:.2f}\,\mathrm{{A}}",GOLD),('DC component',rf"{B['dc']:.2f}\,\mathrm{{A}}",TEAL)]
        for j,(cap,val,color) in enumerate(info):
            cx=-4.25+j*4.25
            self.add(card(cx,1,3.96,1.72),left(text(cap,21,SUB),cx-1.70,1.48),left(math(val,40,color),cx-1.70,.76))
        eq=at(math(r'\mathrm{PF}=\underbrace{\cos\varphi_1}_{1.000}\,\times\,\underbrace{\frac{I_{1,\mathrm{rms}}}{I_{\mathrm{rms}}}}_{0.707}',46),0,-1.0)
        self.play(FadeIn(eq),run_time=.7); self.wait(3.7)
        self.play(FadeIn(at(math(r'\mathrm{THD}_{2:50}=\frac{\sqrt{\sum_{h=2}^{50}I_{h,\mathrm{rms}}^2}}{I_{1,\mathrm{rms}}}='+f"{100*B['thd']:.1f}"+r'\%',34,SUB),0,-2.92)),run_time=.6)
        self.finish(end);self.fresh()

        self.add(self.frame('Fourier synthesis','Building the half-wave current'))
        g=Field((-5.68,5.94,-2.30,1.14),(0,1),(-5,16))
        self.add(g.grid([0,.25,.5,.75,1],[-5,0,5,10,15],['0',r'90^\circ',r'180^\circ',r'270^\circ',r'360^\circ']),
                 left(math(r'i_s\;[\mathrm A]',26),-6.3,1.72),
                 at(math(r'i_N(\theta)=I_{\mathrm{DC}}+\sum_{h=1}^{N}\hat I_h\cos(h\theta+\phi_h)',31),.57,1.69))
        xs=np.linspace(0,1,801);theta=2*np.pi*xs
        co=np.array(B['re'])+1j*np.array(B['im'])
        terms=np.real(co[:,None]*np.exp(1j*np.arange(51)[:,None]*theta))
        sums=terms.cumsum(axis=0)
        traces=[g.curve(xs,y,GOLD,4.7) for y in sums]
        # Use LaTeX glyphs for the live readout. Phases of negligible terms are undefined.
        def readout(n):
            order=VGroup(math('N=',32,GOLD),DecimalNumber(n,num_decimal_places=0,font_size=32,color=GOLD)).arrange(RIGHT,buff=.09)
            amplitude=VGroup(math(r'\hat I_h=',30),DecimalNumber(abs(co[n]),num_decimal_places=3,font_size=30),math(r'\mathrm A',30)).arrange(RIGHT,buff=.09)
            angle=VGroup(math(r'\phi_h=',30))
            if n>0 and abs(co[n])>.0005:
                phase=np.rad2deg(np.angle(co[n]));phase=180 if abs(abs(phase)-180)<.5 else phase
                angle.add(DecimalNumber(phase,num_decimal_places=0,font_size=30,unit=r'^\circ'))
            else:angle.add(math(r'\text{---}',30,SUB))
            angle.arrange(RIGHT,buff=.09)
            return VGroup(left(order,-4.38,-3.22),left(amplitude,-1.92,-3.22),left(angle,2.04,-3.22))
        labels=[readout(n) for n in range(51)]
        curve=traces[0].copy(); current=labels[0]
        end=self.say('slow');self.play(Create(curve),FadeIn(current),run_time=1.0);self.wait(1.4)
        def add_order(n,duration):
            nonlocal current
            self.remove(current);current=labels[n];self.add(current)
            self.play(Transform(curve,traces[n]),run_time=duration,rate_func=smooth)
        for n,seconds in enumerate([2.1,2.15,1.55,1.6,1.15,1.15,1.05,.98,.95],1):
            add_order(n,seconds)
        self.finish(end)
        end=self.say('fast')
        # Hold each high-order readout for six frames at 24 fps.
        for n in range(10,51):
            add_order(n,.25)
        self.finish(end)
        self.remove(current)
        end=self.say('end')
        newtitle=self.frame('Fourier synthesis','Fifty orders against the simulation')
        self.remove(self.mobjects[0]);self.add(newtitle)
        reference=np.array(B['wave'])
        indices=np.unique(np.linspace(0,len(reference)-1,46).round().astype(int))
        dots=VGroup(*[at(Dot(radius=.044,stroke_width=2,stroke_color=TEAL,fill_color=BG,fill_opacity=1),g.x(k/(len(reference)-1)),g.y(reference[k])) for k in indices])
        self.play(FadeIn(dots),FadeIn(key(-5.77,-3.29,'PSCAD samples',TEAL,True)),FadeIn(key(-1.90,-3.29,'Fourier sum',GOLD)),run_time=.75)
        self.play(FadeIn(left(math(r'\varepsilon_{\mathrm{rms}}='+f"{1000*B['err']:.1f}"+r'\,\mathrm{mA}',30,INK),2.05,-3.29)),run_time=.55)
        self.finish(end)
        self.sum_rules()
