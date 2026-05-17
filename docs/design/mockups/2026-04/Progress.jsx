// FORGE — Screen 02: Progress / Score detail
// The trajectory surface. Proves the work is working. Quietly.

const ProgressScreen = () => {
  const cats = [
    { name: 'Clarity',      score: 71, delta: +8,  trend: [62,64,66,68,70,71], up: true  },
    { name: 'Sharpness',    score: 68, delta: +4,  trend: [62,63,65,66,67,68], up: true  },
    { name: 'Density',      score: 64, delta: +1,  trend: [63,63,64,64,64,64], up: false },
    { name: 'Frame',        score: 73, delta: +6,  trend: [66,68,69,71,72,73], up: true  },
    { name: 'Presentation', score: 65, delta: +2,  trend: [62,63,64,65,65,65], up: false },
    { name: 'Recovery',     score: 58, delta: -1,  trend: [60,60,59,59,58,58], up: false },
  ];

  const Spark = ({ pts, up }) => {
    const min = Math.min(...pts), max = Math.max(...pts), range = (max - min) || 1;
    const w = 56, h = 16;
    const path = pts.map((v, i) => {
      const x = (i / (pts.length - 1)) * w;
      const y = h - ((v - min) / range) * h;
      return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
    return (
      <svg width={w} height={h} style={{ overflow: 'visible' }}>
        <path d={path} stroke={up ? C.ember : C.muted} strokeWidth="1" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    );
  };

  return (
    <div style={{ background: C.surface, color: C.bone, minHeight: '100%', position: 'relative' }}>
      <div style={{ position: 'absolute', inset: 0, backgroundImage: `url("${GRAIN_SVG}")`, opacity: 0.05, pointerEvents: 'none', mixBlendMode: 'overlay' }}/>

      <div style={{ position: 'relative', padding: '14px 20px 100px' }}>
        {/* 01-02 Eyebrow + title */}
        <div style={{ ...T.eyebrow, color: C.muted, marginBottom: 8 }}>Season 01</div>
        <div style={{ ...T.display, color: C.bone, marginBottom: 32 }}>Progress</div>

        {/* 03 Composite score */}
        <div style={{ ...T.eyebrow, color: C.ash, marginBottom: 8 }}>Composite score</div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 18 }}>
          <span style={{ ...T.hero, color: C.bone }}>68</span>
          <span style={{ fontSize: 28, fontWeight: 600, color: C.muted, fontFeatureSettings: '"tnum" 1' }}>.7</span>
          <span style={{ ...T.micro, color: C.ember, marginLeft: 10, alignSelf: 'flex-end', paddingBottom: 8, textTransform: 'uppercase' }}>+3.2 this cycle</span>
        </div>

        {/* 04 9-segment bar */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 8 }}>
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} style={{ flex: 1, height: 3, borderRadius: 1.5, background: i < 5 ? C.ember : C.divider }}/>
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 36 }}>
          <span style={{ ...T.eyebrow, color: C.muted }}>DAY 47 / 90</span>
          <span style={{ ...T.eyebrow, color: C.muted }}>52% COMPLETE</span>
        </div>

        {/* 05 Categories label + divider */}
        <div style={{ ...T.eyebrow, color: C.ash, marginBottom: 12 }}>Categories</div>
        <div style={{ height: '0.5px', background: C.divider, marginBottom: 4 }}/>

        {/* 06 Category rows */}
        {cats.map((c, i) => (
          <div key={c.name} style={{
            display: 'grid',
            gridTemplateColumns: '1fr auto 64px 44px',
            alignItems: 'center', gap: 12,
            padding: '18px 0',
            borderBottom: i < cats.length - 1 ? `0.5px solid ${C.divider}` : 'none',
          }}>
            <span style={{ ...T.body, color: C.bone, fontSize: 13 }}>{c.name}</span>
            <span style={{ ...T.displaySm, color: C.bone }}>{c.score}</span>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
              <Spark pts={c.trend} up={c.up}/>
            </div>
            <span style={{ ...T.micro, color: c.delta > 0 ? C.ember : c.delta < 0 ? C.muted : C.muted, textAlign: 'right' }}>
              {c.delta > 0 ? `+${c.delta}` : c.delta < 0 ? c.delta : '—'}
            </span>
          </div>
        ))}

        {/* 07 Earned observation */}
        <div style={{ marginTop: 44 }}>
          <div style={{ ...T.eyebrow, color: C.muted, marginBottom: 10 }}>Earned observation</div>
          <div style={{ ...T.body, color: C.bone, fontSize: 14, lineHeight: 1.6, maxWidth: 320 }}>
            your clarity is up 12 points since you started, most of it from the last 14 days
          </div>
        </div>
      </div>

      <BottomNav active="chart"/>
    </div>
  );
};

if (typeof window !== 'undefined') Object.assign(window, { ProgressScreen });
