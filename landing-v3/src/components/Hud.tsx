import s from "./Hud.module.css";

const RING_R = 265;
const RING_ARCS: [number, number][] = [
  [121, 257],
  [270, 338],
  [27, 60],
];

const point = (deg: number, r: number) => {
  const a = (deg * Math.PI) / 180;
  return `${(r * Math.cos(a)).toFixed(2)} ${(r * Math.sin(a)).toFixed(2)}`;
};
const arc = ([from, to]: [number, number]) =>
  `M ${point(from, RING_R)} A ${RING_R} ${RING_R} 0 ${to - from > 180 ? 1 : 0} 1 ${point(to, RING_R)}`;
/** from −90 = arriba, 90 = abajo; dos medias vueltas en sentido horario */
const circle = (r: number, from: number) =>
  `M ${point(from, r)} A ${r} ${r} 0 1 1 ${point(from + 180, r)} A ${r} ${r} 0 1 1 ${point(from, r)}`;

/** Lo que SARHA "lee" mientras escanea: aparecen una a una con el scroll. */
const LABELS = [
  { x: 186, y: -188, dx: 46, text: "Leyendo tu consulta" },
  { x: -196, y: -170, dx: -46, text: "4 fuentes oficiales" },
  { x: 210, y: 160, dx: 46, text: "Sin datos personales" },
  { x: -214, y: 150, dx: -46, text: "Respuesta verificada" },
];

const SCAN_YS = Array.from({ length: 51 }, (_, i) => -201 + i * 8);
const SPOKES = Array.from({ length: 24 }, (_, i) => i * 15);

/** El escáner que "lee" el iris de SARHA. Un solo SVG en unidades de diseño alrededor del centro. */
export default function Hud() {
  return (
    <div className={s.wrap} aria-hidden="true">
      <svg viewBox="-320 -320 640 640" className={s.svg} data-scene="hud">
        <defs>
          <clipPath id="hud-clip">
            <circle r={205} />
          </clipPath>
          <filter id="hud-bloom" x="-20%" y="-20%" width="140%" height="140%">
            <feFlood style={{ floodColor: "var(--hud-glow)" }} floodOpacity={1} result="flood" />
            <feGaussianBlur in="SourceAlpha" stdDeviation={2.5} result="b1" />
            <feComposite in="flood" in2="b1" operator="in" result="tight" />
            <feGaussianBlur in="SourceAlpha" stdDeviation={8} result="b2" />
            <feComposite in="flood" in2="b2" operator="in" result="wide" />
            <feMerge>
              <feMergeNode in="wide" />
              <feMergeNode in="tight" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g className={s.scan} data-scene="hud-scan" clipPath="url(#hud-clip)">
          {SCAN_YS.map((y) => (
            <path key={y} d={`M -205 ${y} H 205`} />
          ))}
        </g>

        <g className={s.mesh} data-scene="hud-mesh">
          <circle r={150} />
          <circle r={190} />
          {SPOKES.map((deg) => (
            <path key={deg} d={`M ${point(deg, 105)} L ${point(deg, 190)}`} />
          ))}
          {SPOKES.flatMap((deg) =>
            [150, 190].map((r) => {
              const a = (deg * Math.PI) / 180;
              return <circle key={`${deg}-${r}`} className={s.meshDot} cx={r * Math.cos(a)} cy={r * Math.sin(a)} r={1.6} />;
            }),
          )}
        </g>

        <g className={s.strokes} filter="url(#hud-bloom)">
          <g data-scene="hud-ring">
            {RING_ARCS.map((a) => (
              <path key={a.join()} d={arc(a)} pathLength={1} data-draw="" />
            ))}
          </g>
          <path d="M 0 0 H -300" pathLength={1} data-draw="" />
          <path d="M 0 0 H 305" pathLength={1} data-draw="" />
          <path d={circle(80, -90)} pathLength={1} data-draw="" className={s.white} />
          <path d={circle(105, 90)} pathLength={1} data-draw="" className={s.white} />
        </g>

        <g className={s.labels}>
          {LABELS.map((l) => (
            <g key={l.text} data-scene="hud-label" transform={`translate(${l.x} ${l.y})`}>
              <circle r={3} className={s.labelDot} />
              <path d={`M 0 0 L ${l.dx} 0`} className={s.labelLine} />
              <text x={l.dx + (l.dx > 0 ? 8 : -8)} y={4} textAnchor={l.dx > 0 ? "start" : "end"}>
                {l.text}
              </text>
            </g>
          ))}
        </g>
      </svg>
    </div>
  );
}
