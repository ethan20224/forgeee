// FORGE — Screen 01: Home / Today
// The 7am surface. In/out in 90 seconds.

const HomeScreen = () => {
  const [done, setDone] = React.useState({ clarity: true, sharpness: true, density: false, frame: false, recovery: false });
  const completed = Object.values(done).filter(Boolean).length;
  const remaining = 5 - completed;
  const protocols = [
    { key: 'clarity',   cat: 'Clarity',   title: 'AM cleanse, barrier serum',     sub: 'Barrier-safe · 7:12'      },
    { key: 'sharpness', cat: 'Sharpness', title: 'Beard line — corners only',     sub: 'Edge work · 7:18'         },
    { key: 'density',   cat: 'Density',   title: 'Scalp circulation, 3 minutes',  sub: 'Microcirculation · pending' },
    { key: 'frame',     cat: 'Frame',     title: 'Standing chin tucks ×20',       sub: 'Cervical alignment · pending' },
    { key: 'recovery',  cat: 'Recovery',  title: 'Wind-down at 22:30',            sub: 'Sleep prep · evening'      },
  ];

  return (
    <div style={{ background: C.surface, color: C.bone, minHeight: '100%', position: 'relative' }}>
      {/* Subtle grain — kills AI flatness */}
      <div style={{ position: 'absolute', inset: 0, backgroundImage: `url("${GRAIN_SVG}")`, opacity: 0.05, pointerEvents: 'none', mixBlendMode: 'overlay' }}/>

      <div style={{ position: 'relative', padding: '14px 20px 100px' }}>
        {/* 01 — Top bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
          <span style={{ ...T.eyebrow, color: C.ash }}>FRI · 19 APR</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: C.raised, padding: '5px 11px 5px 9px', borderRadius: 999 }}>
            {/* 14 vertical hairline strokes — streak indicator, no flame emoji */}
            <svg width="36" height="9" viewBox="0 0 36 9" fill="none">
              {Array.from({ length: 14 }).map((_, i) => (
                <line key={i} x1={i * 2.5 + 1} y1={i < 12 ? 1.5 : 3} x2={i * 2.5 + 1} y2="8" stroke={i >= 12 ? C.bone : C.ash} strokeWidth="1" strokeLinecap="round"/>
              ))}
            </svg>
            <span style={{ ...T.micro, color: C.bone, fontFeatureSettings: '"tnum" 1' }}>14 day</span>
          </div>
        </div>

        {/* 02 — Greeting */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ ...T.caption, color: C.ash, marginBottom: 2 }}>Good morning,</div>
          <div style={{ ...T.display, color: C.bone, marginBottom: 6 }}>Marcus</div>
          <div style={{ ...T.caption, color: C.ash }}>Day 47 of 90 · Season 01</div>
        </div>

        {/* 03 — Composite score (signature artifact) */}
        <div style={{ marginBottom: 36 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 18 }}>
            <span style={{ ...T.hero, color: C.bone }}>68</span>
            <span style={{ fontSize: 28, fontWeight: 600, letterSpacing: '-0.018em', color: C.muted, fontFeatureSettings: '"tnum" 1' }}>.7</span>
            <span style={{ ...T.micro, color: C.ember, marginLeft: 10, alignSelf: 'flex-end', paddingBottom: 8, textTransform: 'uppercase' }}>+3.2 this cycle</span>
          </div>
          {/* 9-segment progress bar */}
          <div style={{ display: 'flex', gap: 4, marginBottom: 8 }}>
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} style={{ flex: 1, height: 3, borderRadius: 1.5, background: i < 5 ? C.ember : C.divider }}/>
            ))}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ ...T.eyebrow, color: C.muted }}>DAY 47 / 90</span>
            <span style={{ ...T.eyebrow, color: C.muted }}>52% COMPLETE</span>
          </div>
        </div>

        {/* 04 — Today's protocol header card */}
        <div style={{ ...T.eyebrow, color: C.ash, marginBottom: 12 }}>Today's protocol</div>
        <div style={{ background: C.raised, borderRadius: 12, padding: '20px', marginBottom: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
              <span style={{ ...T.hero, color: C.bone }}>{completed}</span>
              <span style={{ fontSize: 28, fontWeight: 600, color: C.muted, fontFeatureSettings: '"tnum" 1' }}>/ 5</span>
            </div>
            <span style={{ ...T.micro, color: C.ember, paddingBottom: 6, textTransform: 'uppercase' }}>
              {remaining === 0 ? 'all logged' : remaining === 1 ? 'one remains' : `${['','one','two','three','four','five'][remaining]} remain`}
            </span>
          </div>
          {/* 5-segment ember bar */}
          <div style={{ display: 'flex', gap: 4 }}>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} style={{ flex: 1, height: 3, borderRadius: 1.5, background: i < completed ? C.ember : C.divider }}/>
            ))}
          </div>
        </div>

        {/* 05 — Protocol items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {protocols.map(p => {
            const isDone = done[p.key];
            return (
              <div key={p.key}
                onClick={() => setDone(d => ({ ...d, [p.key]: !d[p.key] }))}
                style={{
                  background: C.raised, borderRadius: 12,
                  padding: '16px 18px 14px 16px',
                  display: 'flex', alignItems: 'center', gap: 14,
                  cursor: 'pointer',
                  transition: `background 240ms ${EASE.state}`,
                }}>
                {/* Checkmark — raised tone circle, not green, not ember */}
                <div style={{
                  width: 22, height: 22, borderRadius: '50%',
                  border: isDone ? 'none' : `1px solid ${C.divider}`,
                  background: isDone ? C.bone : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                  transition: `all 180ms ${EASE.resolution}`,
                }}>
                  {isDone && (
                    <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                      <path d="M2 5.5L4.3 7.8L9 3" stroke={C.canvas} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 3 }}>
                    <span style={{
                      ...T.body,
                      color: isDone ? C.muted : C.bone,
                      textDecoration: isDone ? 'line-through' : 'none',
                      textDecorationThickness: '0.5px',
                      transition: `color 240ms ${EASE.state}`,
                    }}>{p.title}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ ...T.micro, color: C.muted, textTransform: 'none', letterSpacing: '0em' }}>{p.sub}</span>
                    <span style={{ ...T.eyebrow, color: C.ash }}>{p.cat}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <BottomNav active="home"/>
    </div>
  );
};

// Bottom nav — 5 icons, Lucide-style stroke 1.5px
const BottomNav = ({ active }) => {
  const items = [
    { id: 'home',     d: 'M3 12L12 3L21 12V21H15V15H9V21H3V12Z' },
    { id: 'camera',   custom: <><path d="M3 7h3l2-3h8l2 3h3v13H3z"/><circle cx="12" cy="13" r="4"/></> },
    { id: 'chart',    custom: <><path d="M3 3v18h18"/><path d="M7 14l4-5 4 3 5-7"/></> },
    { id: 'shield',   d: 'M12 2L4 5v6c0 5 3.5 9 8 11 4.5-2 8-6 8-11V5l-8-3z' },
    { id: 'person',   custom: <><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.5 3.6-8 8-8s8 3.5 8 8"/></> },
  ];
  return (
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0,
      display: 'flex', justifyContent: 'space-around', alignItems: 'center',
      background: C.surface, borderTop: `0.5px solid ${C.divider}`,
      padding: '12px 0 28px',
    }}>
      {items.map(it => {
        const on = active === it.id;
        const stroke = on ? C.bone : C.muted;
        return (
          <div key={it.id} style={{ padding: 8, cursor: 'pointer' }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              {it.d ? <path d={it.d}/> : it.custom}
            </svg>
          </div>
        );
      })}
    </div>
  );
};

if (typeof window !== 'undefined') Object.assign(window, { HomeScreen, BottomNav });
