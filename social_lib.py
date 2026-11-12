import os,math,random,wave,subprocess,sys,urllib.request
try: import imageio_ffmpeg
except ImportError: subprocess.run([sys.executable,"-m","pip","install","-q","imageio-ffmpeg"]); import imageio_ffmpeg
FD="/home/user/fonts"; O="/home/user/out/"; os.makedirs(FD,exist_ok=True); os.makedirs(O,exist_ok=True)
for w in ["Bold","Medium"]:
    p=f"{FD}/Poppins-{w}.ttf"
    if not os.path.exists(p): urllib.request.urlretrieve(f"https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-{w}.ttf",p)
FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
from PIL import Image,ImageDraw,ImageFont
import numpy as np
def font(w,s): return ImageFont.truetype(f"{FD}/Poppins-{w}.ttf",s)
TH={"nicki":dict(bg1="#FFF8EC",bg2="#FCEFD8",fg="#1E2A2A",p="#0F8A7E",a="#F2654A",sub="#4A5A5A",brand="NICKI'S STATIONERY"),
"pasifik":dict(bg1="#071822",bg2="#0E4D5C",fg="#FFFFFF",p="#F2B33D",a="#4FD1C5",sub="#BFD7DC",brand="PASIFIK SIGNAL"),
"wantok":dict(bg1="#121212",bg2="#1E1E1E",fg="#FFFFFF",p="#F7C11B",a="#E23A2E",sub="#CFCFCF",brand="WANTOK MARKET PNG"),
"nexus":dict(bg1="#07070C",bg2="#16121F",fg="#FFFFFF",p="#FF4B2B",a="#FFB020",sub="#B9B4C7",brand="MODERN NEXUS PNG")}
def rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def bg(t,W,H,n,seed):
    im=Image.new("RGB",(W,H)); d=ImageDraw.Draw(im); c1,c2=rgb(t["bg1"]),rgb(t["bg2"]); s=W/1080; R=random.Random(seed)
    for y in range(H): d.line([(0,y),(W,y)],fill=tuple(int(c1[i]+(c2[i]-c1[i])*y/H) for i in range(3)))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    if n=="nicki":
        for y in range(int(160*s),H,int(54*s)): d.line([(0,y),(W,y)],fill="#E6DCC6",width=max(1,int(2*s)))
        d.line([(int(110*s),0),(int(110*s),H)],fill="#F5B4A6",width=int(4*s))
    elif n=="pasifik":
        for i in range(9): od.line([(x,H*.8+i*26*s+30*s*math.sin(x/(140*s)+i*.7)) for x in range(0,W+10,10)],fill=(79,209,197,40+i*6),width=max(2,int(3*s)))
        cx,cy=W-int(150*s),int(170*s)
        for r in (40,80,120,160): od.arc([cx-r*s,cy-r*s,cx+r*s,cy+r*s],200,340,fill=(242,179,61,90),width=int(6*s))
    elif n=="wantok":
        b=int(70*s); y0=H-b; d.rectangle([0,y0,W,H],fill="#000")
        for i,x in enumerate(range(-b,W+b,b)): d.polygon([(x,H),(x+b//2,y0),(x+b,H)],fill=t["a"] if i%2 else t["p"])
        d.rectangle([0,0,W,int(14*s)],fill=t["p"])
    else:
        pts=[(R.randint(0,W),R.randint(0,H)) for _ in range(46)]
        for i,p in enumerate(pts):
            for q in pts[i+1:]:
                if math.dist(p,q)<190*s: od.line([p,q],fill=(255,75,43,38),width=max(1,int(2*s)))
        for p in pts: r=R.choice([3,4,6])*s; od.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=(255,176,32,120))
    im.paste(ov,(0,0),ov); return im
def wrap(d,txt,f,mw):
    L=[]
    for para in txt.split("\n"):
        c=""
        for w in para.split(" "):
            t=(c+" "+w).strip()
            if d.textlength(t,font=f)<=mw: c=t
            else:
                if c: L.append(c)
                c=w
        L.append(c)
    return L
def card(n,blocks,W,H,path,seed=1,footer=None,ts=1.0):
    """blocks: dict(text,size,color='p'|'a'|'fg'|'sub'|hex,weight='Bold'|'Medium',gap=30,lh=1.22,pill=False,pillc='p')"""
    t=TH[n]; im=bg(t,W,H,n,seed); d=ImageDraw.Draw(im); s=W/1080; m=int((150 if n=="nicki" else 90)*s); mw=W-m-int(90*s)
    d.text((m,int(70*s)),t["brand"],font=font("Bold",int(30*s)),fill=t["a"] if n=="nexus" else t["p"])
    d.line([(m,int(118*s)),(m+int(90*s),int(118*s))],fill=t["p"] if n=="pasifik" else t["a"],width=int(6*s))
    lay=[];tot=0
    for b in blocks:
        f=font(b.get("weight","Bold"),int(b["size"]*s*ts)); L=wrap(d,b["text"],f,mw-(int(40*s) if b.get("pill") else 0))
        lh=int(b["size"]*s*ts*b.get("lh",1.22)); h=lh*len(L)+(int(28*s) if b.get("pill") else 0); lay.append((b,f,L,lh,h)); tot+=h+int(b.get("gap",30)*s)
    top,bot=int(170*s),H-int((190 if footer else 120)*s); y=top+max(0,(bot-top-tot)//2)
    for b,f,L,lh,h in lay:
        col=t.get(b.get("color","fg"),b.get("color","fg")); x=m
        if b.get("pill"):
            d.rounded_rectangle([m,y,m+max(d.textlength(l,font=f) for l in L)+int(40*s),y+h],radius=int(18*s),fill=t.get(b.get("pillc","p"),b.get("pillc"))); x=m+int(20*s); yy=y+int(14*s)
        else: yy=y
        for l in L: d.text((x,yy),l,font=f,fill=col); yy+=lh
        y+=h+int(b.get("gap",30)*s)
    if footer: d.text((m,H-int((175 if n=="wantok" else 140)*s)),footer,font=font("Bold",int(34*s)),fill=t["a"] if n=="nexus" else t["p"])
    im.save(path,quality=92); return path
SR=44100
def note(k): return 440*2**((k-69)/12)
def track(path,bpm,prog,dur=16.0,br=1.0,seed=0):
    g=np.random.default_rng(seed); N=int(SR*dur); o=np.zeros(N); bt=60/bpm; bar=bt*4; T=np.arange(N)/SR
    for i in range(int(dur/bar)+1):
        ch=prog[i%len(prog)]; s0=int(i*bar*SR); n=min(int(bar*SR),N-s0)
        if n<=0: break
        tt=np.arange(n)/SR; pe=np.minimum(1,tt/.25)*np.minimum(1,(bar-tt)/.2)
        o[s0:s0+n]+=.06*sum(np.sin(2*np.pi*note(k)*tt)+.3*np.sin(4*np.pi*note(k)*tt) for k in ch)*pe+.12*np.sin(2*np.pi*note(ch[0]-12)*tt)*pe
        ar=[ch[0]+12,ch[1]+12,ch[2]+12,ch[1]+12]
        for k in range(8):
            a0=s0+int(k*bt/2*SR); mm=int(bt/2*SR)
            if a0+mm>N: break
            ta=np.arange(mm)/SR; f=note(ar[k%4]); o[a0:a0+mm]+=.07*(np.sin(2*np.pi*f*ta)+.25*br*np.sin(4*np.pi*f*ta))*np.minimum(1,ta/.005)*np.exp(-ta/.18)
    for b in range(int(dur/bt)):
        k0=int(b*bt*SR); mm=int(.25*SR)
        if k0+mm>N: break
        tk=np.arange(mm)/SR; o[k0:k0+mm]+=.35*np.sin(2*np.pi*(50+90*np.exp(-tk*30))*tk)*np.exp(-tk*12)
        if b%2: o[k0:k0+mm]+=.08*g.normal(0,1,mm)*np.exp(-tk*22)
        h0=k0+int(bt/2*SR); hm=int(.05*SR)
        if h0+hm<N: o[h0:h0+hm]+=.04*g.normal(0,1,hm)*np.exp(-np.arange(hm)/SR*90)
    o*=np.minimum(1,np.minimum(T/.8,(dur-T)/1.5)); o/=np.max(np.abs(o))*1.15; q=(o*32767).astype(np.int16)
    with wave.open(path,"wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.stack([q,q],1).tobytes())
MUSIC={"nicki":(112,[[60,64,67],[67,71,74],[69,72,76],[65,69,72]],1.0),"pasifik":(92,[[62,65,69],[58,62,65],[60,64,67],[57,60,64]],1.0),"wantok":(120,[[67,71,74],[64,67,71],[60,64,67],[62,66,69]],1.0),"nexus":(100,[[57,60,64],[53,57,60],[60,64,67],[55,59,62]],1.5),"moti":(84,[[60,64,67],[57,60,64],[65,69,72],[67,71,74]],0.8)}
def make_music():
    for i,(k,(bpm,pr,b)) in enumerate(MUSIC.items()):
        if not os.path.exists(O+f"m_{k}.wav"): track(O+f"m_{k}.wav",bpm,pr,br=b,seed=i+1)
def reel(name,slides,music,first=2.6,each=3.6):
    """slides: list of image paths (720x1280). First slide shorter = faster hook."""
    k=len(slides); durs=[first]+[each]*(k-1); xf=.5; fc=[]; prev="0"; off=0
    for i in range(1,k):
        off+=durs[i-1]-xf; lab=f"x{i}" if i<k-1 else "xv"; fc.append(f"[{prev}][{i}]xfade=transition=slideleft:duration={xf}:offset={off:.2f}[{lab}]"); prev=lab
    D=sum(durs)-xf*(k-1); fc=";".join(fc)+f";[xv]format=yuv420p,fps=30[v];[{k}]atrim=0:{D:.2f},afade=t=out:st={D-1.5:.2f}:d=1.5[au]"
    cmd=[FFMPEG,"-y","-loglevel","error"]
    for p,du in zip(slides,durs): cmd+=["-loop","1","-t",f"{du}","-i",p]
    out=O+f"{name}.mp4"; cmd+=["-i",music,"-filter_complex",fc,"-map","[v]","-map","[au]","-c:v","libx264","-preset","veryfast","-crf","26","-c:a","aac","-b:a","96k","-t",f"{D:.2f}","-movflags","+faststart",out]
    subprocess.run(cmd,check=True); return out
PAGES={"nicki":"1361725270362613","pasifik":"1422912810907467","wantok":"1414963638362827","nexus":"1446959875167370"}
ACC="facebook_elod-sanga"
LINKS={"nicki":"📲 Order on WhatsApp: https://wa.me/67576564482","wantok":"📲 WhatsApp Wantok Market: https://wa.me/67581392582","pasifik":"▶️ Watch more on YouTube: https://www.youtube.com/@pasifiksignal","nexus":"💬 Message Modern Nexus PNG: https://m.me/modernnexuspng"}
def s3key(path):
    r,e=upload_local_file(path)
    if e: raise RuntimeError(e)
    return r.get("s3key") or r.get("data",{}).get("s3key")
# --- AI voiceover reels (edge-tts). In the workbench call with: out,dur = await voiced_reel(...)
def wav_dur(p):
    with wave.open(p) as w: return w.getnframes()/w.getframerate()
async def voiced_reel(key,name,lines,slides_blocks,voice="en-AU-WilliamMultilingualNeural",pad=0.35):
    """lines: narration sentences; slides_blocks: one block-list per line (on-screen captions). Returns (mp4 path, seconds)."""
    try: import edge_tts
    except ImportError: subprocess.run([sys.executable,"-m","pip","install","-q","edge-tts"]); import edge_tts
    clips=[];slides=[]
    for i,(ln,blk) in enumerate(zip(lines,slides_blocks)):
        mp3=O+f"{name}_v{i}.mp3"; wv=O+f"{name}_v{i}.wav"
        await edge_tts.Communicate(ln,voice,rate="+4%").save(mp3)
        subprocess.run([FFMPEG,"-y","-loglevel","error","-i",mp3,"-ar","44100","-ac","2",wv],check=True)
        clips.append((wv,wav_dur(wv)+pad)); slides.append(card(key,blk,720,1280,O+f"{name}_s{i}.png",seed=i+3,ts=1.3))
    total=sum(d for _,d in clips); voicef=O+f"{name}_voice.wav"
    fc="".join(f"[{i}]apad=pad_dur={pad}[a{i}];" for i in range(len(clips)))+"".join(f"[a{i}]" for i in range(len(clips)))+f"concat=n={len(clips)}:v=0:a=1[o]"
    subprocess.run([FFMPEG,"-y","-loglevel","error"]+sum([["-i",w] for w,_ in clips],[])+["-filter_complex",fc,"-map","[o]",voicef],check=True)
    bpm,pr,b=MUSIC.get(key,MUSIC["moti"]); mus=O+f"{name}_m.wav"; track(mus,bpm,pr,dur=total+1.0,br=b,seed=7)
    vl=O+f"{name}_slides.txt"
    with open(vl,"w") as f:
        for p,(_,d) in zip(slides,clips): f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{slides[-1]}'\n")
    out=O+f"{name}.mp4"
    subprocess.run([FFMPEG,"-y","-loglevel","error","-f","concat","-safe","0","-i",vl,"-i",voicef,"-i",mus,"-filter_complex",
        "[0:v]fps=30,format=yuv420p[v];[2:a]volume=0.16[m];[1:a][m]amix=inputs=2:duration=first:dropout_transition=0[au]",
        "-map","[v]","-map","[au]","-c:v","libx264","-preset","veryfast","-crf","26","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",out],check=True)
    return out,total
# --- Josh's anime character (Modern Nexus PNG thumbnails) ---
ASSETS="https://raw.githubusercontent.com/JoshAria-Creator/nickis-stationery/social-media-assets/"
JOSH={"point":"josh/anime-point.png","openhands":"josh/anime-openhands.png","wave":"josh/anime-wave.png","present":"josh/anime-present.png","side_point":"josh/anime-side-point.png"}
def josh(pose="point"):
    p=O+f"josh_{pose}.png"
    if not os.path.exists(p): urllib.request.urlretrieve(ASSETS+JOSH[pose],p)
    return p
def person_card(n,blocks,W,H,path,pose="point",person_h=0.55,x_frac=0.6,seed=1,ts=1.0):
    """Text at the top, Josh's anime cutout at the bottom (glow behind). Use for Modern Nexus thumbnails, reel slide 1 and outros."""
    from PIL import ImageFilter
    t=TH[n]; im=bg(t,W,H,n,seed).convert("RGBA"); s=W/1080; m=int(90*s); mw=W-m-int(90*s)
    pc=Image.open(josh(pose)).convert("RGBA"); pc=pc.crop(pc.getbbox()); ph=int(H*person_h); pc=pc.resize((int(pc.width*ph/pc.height),ph),Image.LANCZOS)
    if pc.width>W: pc=pc.resize((W,int(pc.height*W/pc.width)),Image.LANCZOS)
    px=int(W*x_frac-pc.width/2); px=max(0,min(W-pc.width,px)); py=H-pc.height
    g=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g); r=int(260*s); cx,cy=px+pc.width//2,py+int(pc.height*.35)
    gd.ellipse([cx-r,cy-r,cx+r,cy+r],fill=rgb(t["p"])+(150,)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(int(120*s))))
    d=ImageDraw.Draw(im); d.text((m,int(70*s)),t["brand"],font=font("Bold",int(30*s)),fill=t["a"] if n=="nexus" else t["p"])
    d.line([(m,int(118*s)),(m+int(90*s),int(118*s))],fill=t["p"] if n=="pasifik" else t["a"],width=int(6*s))
    limit=py+int(pc.height*0.06)  # top of headdress
    k=1.0
    while True:
        y=int(190*s); lay=[]
        for b in blocks:
            f=font(b.get("weight","Bold"),max(10,int(b["size"]*s*ts*k))); lh=int(b["size"]*s*ts*k*b.get("lh",1.12))
            L=wrap(d,b["text"],f,mw); lay.append((b,f,L,lh,y)); y+=lh*len(L)+int(b.get("gap",20)*s)
        if y<=limit or k<=0.45: break
        k-=0.05
    for b,f,L,lh,y0 in lay:
        for l in L: d.text((m,y0),l,font=f,fill=t.get(b.get("color","fg"),b.get("color","fg"))); y0+=lh
    im.alpha_composite(pc,(px,py)); im.convert("RGB").save(path,quality=92); return path

# --- Original techno track (used for Modern Nexus reels) ---
def techno(path,dur=30.0,bpm=126,root=45,seed=3):
    """Original four-on-the-floor techno: kick, offbeat hats, claps, rolling 16th bass, chord stabs, filter build."""
    g=np.random.default_rng(seed); N=int(SR*dur); L=np.zeros(N); R=np.zeros(N); T=np.arange(N)/SR
    bt=60/bpm; st=bt/4
    def add(sig,start,pan=0.0,vol=1.0):
        i=int(start*SR); j=min(N,i+len(sig))
        if i>=N: return
        L[i:j]+=sig[:j-i]*vol*(1-pan)/1; R[i:j]+=sig[:j-i]*vol*(1+pan)/1
    tk=np.arange(int(.35*SR))/SR
    kick=np.sin(2*np.pi*(45+120*np.exp(-tk*35))*tk)*np.exp(-tk*9); kick+=0.3*np.sin(2*np.pi*3000*tk)*np.exp(-tk*400)
    th=np.arange(int(.06*SR))/SR; hat=g.normal(0,1,len(th)); hat=np.diff(np.concatenate([[0],hat]))*np.exp(-th*60)
    ohat=g.normal(0,1,int(.18*SR)); ohat=np.diff(np.concatenate([[0],ohat]))*np.exp(-np.arange(len(ohat))/SR*18)
    tc=np.arange(int(.2*SR))/SR; clap=g.normal(0,1,len(tc))*(np.exp(-tc*30)+0.6*np.exp(-np.maximum(tc-.012,0)*30)*(tc>.012))
    prog=[0,0,-4,-2]  # i, i, VI, VII feel in minor
    nb=int(dur/bt)
    for b in range(nb):
        t0=b*bt; bar=b//4; sec=bar//4  # 4-bar sections
        intro = bar<2
        add(kick,t0,vol=0.9 if not intro else 0.6)
        if not intro: add(ohat,t0+bt/2,pan=0.25,vol=0.18)
        add(hat,t0+bt/4,pan=-0.3,vol=0.08); add(hat,t0+3*bt/4,pan=0.3,vol=0.08)
        if b%2==1 and bar>=1: add(clap,t0,vol=0.22)
        # rolling bass 16ths (skip the downbeat for groove)
        off=prog[bar%4]
        for k in range(4):
            if k==0: continue
            ts=np.arange(int(st*SR*.9))/SR; f=note(root+off-12+(12 if k==2 else 0))
            saw=2*((ts*f)%1)-1; env=np.exp(-ts*14)
            cut=0.35+0.6*min(1,(t0)/dur)  # filter opens over time
            sig=np.convolve(saw*env,np.ones(int(6/cut))/int(6/cut),mode="same")
            add(sig,t0+k*st,vol=0.28)
        # chord stab on the "and" of beat 3 every bar
        if b%4==2 and not intro:
            ts=np.arange(int(.22*SR))/SR; ch=[root+off+12,root+off+15,root+off+19]
            stab=sum((2*((ts*note(c))%1)-1) for c in ch)/3*np.exp(-ts*12)
            stab=np.convolve(stab,np.ones(8)/8,mode="same")
            add(stab,t0+bt/2,pan=0.15,vol=0.16); add(stab*0.5,t0+bt/2+bt*0.75,pan=-0.3,vol=0.12)  # echo
    # riser into the last section
    rs=max(0,dur-8.5); n=int(4*SR); tr=np.arange(n)/SR
    if rs>0: add(g.normal(0,1,n)*(tr/4)**2*0.12,rs-4)
    fade=np.minimum(1,np.minimum(T/0.6,(dur-T)/1.8)); L*=fade; R*=fade
    m=max(np.max(np.abs(L)),np.max(np.abs(R)))*1.12; L/=m; R/=m
    s=(np.stack([L,R],1)*32767).astype(np.int16)
    with wave.open(path,"wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())

def make_techno(dur=31.0):
    p=O+f"m_techno_{int(dur)}.wav"
    if not os.path.exists(p): techno(p,dur=dur)
    return p
