// FORGE — Screen 03: Cycle photo capture
// Every 3 days. A moment, not a tap. Tailor's chalk, not Instagram filter.

const CaptureScreen = () => {
  const [pressed, setPressed] = React.useState(false);

  return (
    <div style={{ background: C.canvas, color: C.bone, minHeight: '100%', position: 'relative', display: 'flex', flexDirection: 'column' }}>
      {/* Slightly stronger grain on canvas — this is a quieter, darker surface */}
      <div style={{ position: 'absolute', inset: 0, backgroundImage: `url("${GRAIN_SVG}")`, opacity: 0.07, pointerEvents: 'none', mixBlendMode: 'overlay' }}/>

      <div style={{ position: 'relative', padding: '16px 20px 0', display: 'flex', flexDirection: 'column', flex: 1 }}>

        {/* 01 — Top eyebrow */}
        <div style={{ ...T.eyebrow, color: C.muted, textAlign: 'center', marginBottom: 36 }}>
          CYCLE 16 · DAY 48
        </div>

        {/* 02 — Face frame guide. Tailor's chalk: 4 corner ticks + ghost oval. */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
          <div style={{ position: 'relative', width: 234, height: 308 }}>
            {/* Subtle ghost oval, very faint */}
            <svg width="234" height="308" viewBox="0 0 234 308" style={{ position: 'absolute', inset: 0 }}>
              <ellipse cx="117" cy="154" rx="92" ry="128" fill="none" stroke={C.bone} strokeWidth="0.5" opacity="0.18"/>
            </svg>
            {/* Four corner ticks — the chalk marks. Asymmetric placement. */}
            {[
              { top: 0,    left: 0,    rot: 0 },
              { top: 0,    right: 0,   rot: 90 },
              { bottom: 0, left: 0,    rot: 270 },
              { bottom: 0, right: 0,   rot: 180 },
            ].map((p, i) => (
              <div key={i} style={{ position: 'absolute', ...p, width: 22, height: 22, transform: `rotate(${p.rot}deg)` }}>
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                  <path d="M0 1H10" stroke={C.bone} strokeWidth="0.5"/>
                  <path d="M1 0V10" stroke={C.bone} strokeWidth="0.5"/>
                </svg>
              </div>
            ))}
          </div>
        </div>

        {/* 03 — Instructions */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ ...T.body, color: C.ash, fontSize: 13, marginBottom: 6 }}>Frame your face inside the outline.</div>
          <div style={{ ...T.micro, color: C.muted, textTransform: 'none', letterSpacing: '0em' }}>
            Even lighting. Neutral expression. Same time of day.
          </div>
        </div>

        {/* 04 — Last cycle thumbnail */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, marginBottom: 24 }}>
          <div style={{ ...T.eyebrow, color: C.muted }}>Last cycle</div>
          <div style={{
            width: 40, height: 50, borderRadius: 3,
            background: C.raised, border: `0.5px solid ${C.divider}`,
            position: 'relative', overflow: 'hidden',
          }}>
            {/* Photo grid placeholder — face suggestion */}
            <div style={{ position: 'absolute', inset: 0, opacity: 0.4 }}>
              <svg width="40" height="50" viewBox="0 0 40 50" fill="none">
                <ellipse cx="20" cy="22" rx="11" ry="14" fill={C.muted} opacity="0.6"/>
                <ellipse cx="20" cy="44" rx="13" ry="6" fill={C.muted} opacity="0.4"/>
              </svg>
            </div>
            <div style={{
              position: 'absolute', bottom: 0, left: 0, right: 0,
              fontSize: 9, fontWeight: 500, letterSpacing: '0.04em',
              color: C.bone, textAlign: 'center', padding: '1px 0 2px',
              background: 'rgba(10,9,7,0.7)',
            }}>DAY 45</div>
          </div>
        </div>

        {/* 05 — Capture button. 72px circle, 0.5px bone stroke, raised fill, center dot. */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 18 }}>
          <button
            onClick={() => { setPressed(true); setTimeout(() => setPressed(false), 200); }}
            style={{
              width: 72, height: 72, borderRadius: '50%',
              background: C.raised, border: `0.5px solid ${C.bone}`,
              cursor: 'pointer', padding: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transform: pressed ? 'scale(0.94)' : 'scale(1)',
              transition: `transform 180ms ${EASE.resolution}`,
            }}>
            {/* Center dot, offset 0.5px right of optical center for hand-machined feel */}
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: C.bone, marginLeft: 0.5 }}/>
          </button>
        </div>

        {/* 06 — Skip. Quiet. Not punishing. */}
        <div style={{ textAlign: 'center', paddingBottom: 36 }}>
          <span style={{
            ...T.micro, color: C.muted, textTransform: 'none', letterSpacing: '0em',
            borderBottom: `0.5px solid ${C.muted}`, paddingBottom: 1,
            cursor: 'pointer',
          }}>Skip this cycle</span>
        </div>
      </div>
    </div>
  );
};

if (typeof window !== 'undefined') Object.assign(window, { CaptureScreen });
