import time, numpy as np, sys
sys.path.insert(0, ".")
from aeon.datasets import load_from_ts_file
from aeon.transformations.collection.convolution_based import MiniRocket as AeonMR
from sklearn.linear_model import RidgeClassifierCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from src.models.maskrocket import MaskRocket

def load(name):
    p=f"data/raw/Univariate_ts/{name}/{name}"
    Xtr,ytr=load_from_ts_file(p+"_TRAIN.ts"); Xte,yte=load_from_ts_file(p+"_TEST.ts")
    return Xtr[:,0].astype(np.float32),ytr,Xte[:,0].astype(np.float32),yte
def clf(): return make_pipeline(StandardScaler(), RidgeClassifierCV(alphas=np.logspace(-3,3,10)))
for name in ["ArrowHead","GunPoint","ECG200","Wafer","ShapesAll"]:
    Xtr,ytr,Xte,yte=load(name)
    a=MaskRocket(conv="group_mean",random_state=0).fit(Xtr); b=MaskRocket(conv="zero_fill",random_state=0).fit(Xtr)
    t=time.time(); Fa=a.transform(Xte); ta=time.time()-t; Fb=b.transform(Xte)
    eq=np.abs(Fa-Fb).max()
    acc=clf().fit(a.transform(Xtr),ytr).score(Fa,yte)
    t=time.time(); am=AeonMR(random_state=0,n_jobs=4).fit(Xtr[:,None]); Ftr=am.transform(Xtr[:,None]); Fte=am.transform(Xte[:,None]); tm=time.time()-t
    acc2=clf().fit(Ftr,ytr).score(Fte,yte)
    # missing 30% MCAR quick sanity
    rng=np.random.RandomState(0); Xtr_m=Xtr.copy(); Xte_m=Xte.copy(); Xtr_m[rng.rand(*Xtr.shape)<0.3]=np.nan; Xte_m[rng.rand(*Xte.shape)<0.3]=np.nan
    t=time.time(); c=MaskRocket(random_state=0).fit(Xtr_m); acc3=clf().fit(c.transform(Xtr_m),ytr).score(c.transform(Xte_m),yte); t3=time.time()-t
    print(f"{name}: N={len(Xtr)}+{len(Xte)} L={Xtr.shape[1]} maxdiff(group_mean vs zero_fill, complete)={eq:.2e} | ours acc={acc:.3f} (transform test {ta:.1f}s) | aeon MiniRocket acc={acc2:.3f} ({tm:.1f}s) | ours@MCAR30 acc={acc3:.3f} ({t3:.1f}s)")
